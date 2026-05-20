from __future__ import annotations

import json
from pathlib import Path

from open_image_to_cad.cad.cadquery_runner import run_cadquery


def run_with_repair(adapter, code: str, out_dir: Path, max_attempts: int = 3):
    attempts_dir = out_dir / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    current = code
    last_report = None
    for i in range(1, max_attempts + 1):
        (attempts_dir / f"attempt_{i}.py").write_text(current)
        report = run_cadquery(current, out_dir)
        last_report = report
        if report.get("ok"):
            report["attempts"] = i
            (out_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
            return current, report
        err = "\n".join(report.get("errors", []))
        (attempts_dir / f"attempt_{i}_error.txt").write_text(err)
        current = adapter.repair_code(None, current, err)

    last_report["attempts"] = max_attempts
    (out_dir / "validation_report.json").write_text(json.dumps(last_report, indent=2))
    return current, last_report
