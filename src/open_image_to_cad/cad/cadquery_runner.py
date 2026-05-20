from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from open_image_to_cad.cad.sandbox import validate_imports


RUNNER_SENTINEL = "__OITC_REPORT__"


def _base_report(errors: list[str] | None = None) -> dict:
    return {
        "ok": False,
        "syntax_ok": True,
        "imports_ok": False,
        "execution_ok": False,
        "result_object_found": False,
        "exports": {"step": False, "stl": False, "glb": False},
        "errors": errors or [],
        "warnings": [],
        "attempts": 1,
    }


def _parse_runner_stdout(stdout: str) -> tuple[dict | None, list[str]]:
    warnings: list[str] = []
    for line in stdout.splitlines()[::-1]:
        if line.startswith(RUNNER_SENTINEL):
            payload = line[len(RUNNER_SENTINEL) :]
            try:
                return json.loads(payload), warnings
            except json.JSONDecodeError as exc:
                return None, [f"invalid runner JSON payload: {exc}"]
        if line.strip():
            warnings.append(f"non-report stdout: {line[:200]}")
    return None, ["runner report sentinel not found", *warnings]


def run_cadquery(code: str, out_dir: Path, timeout_seconds: int = 20) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    py_path = out_dir / "generated_model.py"
    py_path.write_text(code)

    imports_ok, import_errors = validate_imports(code, "cadquery")
    if not imports_ok:
        report = _base_report(import_errors)
        (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
        return report

    runner = f'''
import json
from pathlib import Path
import cadquery as cq
SAFE_BUILTINS = {{
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "pow": pow,
    "print": print,
    "range": range,
    "round": round,
    "set": set,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "__import__": _safe_import,
}}

ns = {{"__builtins__": SAFE_BUILTINS}}
code = Path(r"{py_path}").read_text()
exec(code, ns, ns)
result = ns.get("result")
rep = {{"result_object_found": result is not None, "step": False, "stl": False, "glb": False, "warnings": []}}
if result is not None:
    try:
        cq.exporters.export(result, r"{out_dir / 'model.step'}")
        rep["step"] = True
    except Exception as e:
        rep["warnings"].append(f"STEP export failed: {{e}}")
    try:
        cq.exporters.export(result, r"{out_dir / 'model.stl'}")
        rep["stl"] = True
    except Exception as e:
        rep["warnings"].append(f"STL export failed: {{e}}")
rep["warnings"].append("GLB export not implemented in MVP")
print("{RUNNER_SENTINEL}" + json.dumps(rep))
'''

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(runner)
        runner_path = tmp.name

    try:
        proc = subprocess.run(
            [sys.executable, runner_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        report = _base_report([f"timeout after {timeout_seconds}s"])
        report["imports_ok"] = True
        (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
        return report

    if proc.returncode != 0:
        report = _base_report([proc.stderr.strip() or "execution failed"])
        report["imports_ok"] = True
        (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
        return report

    parsed, parse_warnings = _parse_runner_stdout(proc.stdout)
    if parsed is None:
        report = _base_report(parse_warnings)
        report["imports_ok"] = True
        report["execution_ok"] = True
        report["warnings"] = parse_warnings
        (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
        return report

    report = {
        "ok": bool(parsed.get("result_object_found") and parsed.get("step")),
        "syntax_ok": True,
        "imports_ok": True,
        "execution_ok": True,
        "result_object_found": bool(parsed.get("result_object_found")),
        "exports": {
            "step": bool(parsed.get("step")),
            "stl": bool(parsed.get("stl")),
            "glb": False,
        },
        "errors": [],
        "warnings": parsed.get("warnings", []) + parse_warnings,
        "attempts": 1,
    }
    (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
    return report
