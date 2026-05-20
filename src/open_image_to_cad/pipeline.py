from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path

from open_image_to_cad.cad.cadquery_runner import run_cadquery
from open_image_to_cad.mock_model import generate_cadquery_code, infer_prompt
from open_image_to_cad.schemas import RunRequest, RunResult


def run(req: RunRequest) -> RunResult:
    run_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    out = Path(req.output_dir) / run_id
    out.mkdir(parents=True, exist_ok=True)

    kind = infer_prompt(req.text, req.image_path)
    code = generate_cadquery_code(kind)
    code_path = out / "generated_model.py"
    code_path.write_text(code)

    if req.text:
        (out / "input_text.txt").write_text(req.text)
    if req.image_path:
        src = Path(req.image_path)
        if src.exists():
            (out / src.name).write_bytes(src.read_bytes())

    report = run_cadquery(code, out)
    report_path = out / "validation_report.json"
    if not report_path.exists():
        report_path.write_text(json.dumps(report, indent=2))

    return RunResult(
        run_id=run_id,
        output_dir=str(out),
        generated_code_path=str(code_path),
        validation_report_path=str(report_path),
        step_path=str(out / "model.step") if (out / "model.step").exists() else None,
        stl_path=str(out / "model.stl") if (out / "model.stl").exists() else None,
        warnings=report.get("warnings", []),
    )
