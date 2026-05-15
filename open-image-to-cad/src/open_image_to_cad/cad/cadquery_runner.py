import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any
from .sandbox import validate_imports

# We'll use a runner script that actually evaluates the code in a subprocess
RUNNER_TEMPLATE = """
import sys
import json
import traceback

# Setup basic error logging for the runner
def write_error(msg):
    sys.stderr.write(msg + "\\n")
    sys.exit(1)

try:
{code_indented}

    if 'result' not in locals():
        write_error("Variable 'result' not found in generated code.")

    import cadquery as cq

    res = locals().get('result')
    if not isinstance(res, (cq.Workplane, cq.Shape, cq.Assembly)):
        write_error("Variable 'result' is not a valid CadQuery object.")

    # Try to export
    exports = {{}}

    try:
        if hasattr(res, 'val') and hasattr(res.val(), 'exportStep'):
            res.val().exportStep("{output_dir}/model.step")
        elif hasattr(res, 'exportStep'):
            res.exportStep("{output_dir}/model.step")
        elif hasattr(cq.exporters, 'export'):
            cq.exporters.export(res, "{output_dir}/model.step")
        exports["step"] = True
    except Exception as e:
        sys.stderr.write(f"STEP export failed: {{e}}\\n")
        exports["step"] = False

    try:
        if hasattr(cq.exporters, 'export'):
            cq.exporters.export(res, "{output_dir}/model.stl")
            exports["stl"] = True
        else:
            exports["stl"] = False
    except Exception as e:
        sys.stderr.write(f"STL export failed: {{e}}\\n")
        exports["stl"] = False

    # We explicitly skip GLB for MVP, but we'll report it as False
    exports["glb"] = False

    # Try to get volume
    volume = None
    try:
        if hasattr(res, 'val') and hasattr(res.val(), 'Volume'):
            volume = res.val().Volume()
        elif hasattr(res, 'Volume'):
            volume = res.Volume()
    except Exception:
        pass

    out_meta = {{"exports": exports, "volume": volume}}
    with open("{output_dir}/run_meta.json", "w") as f:
        json.dump(out_meta, f)

except Exception as e:
    traceback.print_exc()
    sys.exit(1)
"""

class CadQueryRunner:
    def __init__(self, timeout_seconds: int = 20):
        self.timeout_seconds = timeout_seconds

    def run(self, code: str, output_dir: Path) -> Dict[str, Any]:
        result_info: Dict[str, Any] = {
            "ok": False,
            "syntax_ok": False,
            "imports_ok": False,
            "execution_ok": False,
            "result_object_found": False,
            "exports": {},
            "errors": [],
            "warnings": [],
            "volume": None
        }

        # 1. Validate imports
        imports_ok, import_errors = validate_imports(code, "cadquery")
        if not imports_ok:
            result_info["errors"].extend(import_errors)
            return result_info

        result_info["syntax_ok"] = True
        result_info["imports_ok"] = True

        # Indent code for runner template
        indented_code = "\n".join("    " + line for line in code.splitlines())
        runner_code = RUNNER_TEMPLATE.format(
            code_indented=indented_code,
            output_dir=output_dir.absolute().as_posix()
        )

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(runner_code)
            runner_file = f.name

        try:
            # 2. Execute
            proc = subprocess.run(
                ["python", runner_file],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )

            if proc.returncode == 0:
                result_info["execution_ok"] = True
                result_info["result_object_found"] = True

                # Check meta
                meta_path = output_dir / "run_meta.json"
                if meta_path.exists():
                    import json
                    with open(meta_path, "r") as mf:
                        meta = json.load(mf)
                        result_info["exports"] = meta.get("exports", {})
                        result_info["volume"] = meta.get("volume")

                if not result_info["exports"].get("glb"):
                    result_info["warnings"].append("GLB export is experimental and was not produced.")

                result_info["ok"] = result_info["exports"].get("step", False)
            else:
                result_info["errors"].append(proc.stderr or proc.stdout)

        except subprocess.TimeoutExpired:
            result_info["errors"].append(f"Execution timed out after {self.timeout_seconds}s")
        except Exception as e:
            result_info["errors"].append(f"Execution error: {str(e)}")
        finally:
            if os.path.exists(runner_file):
                os.unlink(runner_file)

        return result_info
