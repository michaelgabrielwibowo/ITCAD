from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from open_image_to_cad.cad.sandbox import validate_imports


def run_cadquery(code: str, out_dir: Path, timeout_seconds: int = 20) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    py_path = out_dir / "generated_model.py"
    py_path.write_text(code)

    syntax_ok = True
    imports_ok, import_errors = validate_imports(code, "cadquery")
    if not imports_ok:
        return {
            "ok": False,
            "syntax_ok": syntax_ok,
            "imports_ok": False,
            "execution_ok": False,
            "result_object_found": False,
            "exports": {"step": False, "stl": False, "glb": False},
            "errors": import_errors,
            "warnings": [],
            "attempts": 1,
        }

    runner = f'''
import json
from pathlib import Path
import cadquery as cq
ns = {{}}
code = Path(r"{py_path}").read_text()
exec(code, ns, ns)
result = ns.get("result")
rep = {{"result_object_found": result is not None, "step": False, "stl": False, "glb": False, "warnings": []}}
if result is not None:
    try:
        cq.exporters.export(result, r"{out_dir/'model.step'}")
        rep["step"] = True
    except Exception as e:
        rep["warnings"].append(f"STEP export failed: {{e}}")
    try:
        cq.exporters.export(result, r"{out_dir/'model.stl'}")
        rep["stl"] = True
    except Exception as e:
        rep["warnings"].append(f"STL export failed: {{e}}")
rep["warnings"].append("GLB export not implemented in MVP")
print(json.dumps(rep))
'''
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(runner)
        runner_path = f.name

    try:
        proc = subprocess.run(["python", runner_path], capture_output=True, text=True, timeout=timeout_seconds)
        if proc.returncode != 0:
            return {
                "ok": False,
                "syntax_ok": syntax_ok,
                "imports_ok": True,
                "execution_ok": False,
                "result_object_found": False,
                "exports": {"step": False, "stl": False, "glb": False},
                "errors": [proc.stderr.strip() or "execution failed"],
                "warnings": [],
                "attempts": 1,
            }
        rep = json.loads(proc.stdout.strip() or "{}")
        out = {
            "ok": bool(rep.get("result_object_found") and rep.get("step")),
            "syntax_ok": syntax_ok,
            "imports_ok": True,
            "execution_ok": True,
            "result_object_found": bool(rep.get("result_object_found")),
            "exports": {"step": bool(rep.get("step")), "stl": bool(rep.get("stl")), "glb": False},
            "errors": [],
            "warnings": rep.get("warnings", []),
            "attempts": 1,
        }
        (out_dir / "validation_report.json").write_text(json.dumps(out, indent=2))
        return out
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "syntax_ok": syntax_ok,
            "imports_ok": True,
            "execution_ok": False,
            "result_object_found": False,
            "exports": {"step": False, "stl": False, "glb": False},
            "errors": [f"timeout after {timeout_seconds}s"],
            "warnings": [],
            "attempts": 1,
        }
