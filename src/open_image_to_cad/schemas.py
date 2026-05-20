from __future__ import annotations

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    text: str | None = None
    image_path: str | None = None
    output_dir: str = "outputs"


class RunResult(BaseModel):
    run_id: str
    output_dir: str
    generated_code_path: str
    validation_report_path: str
    step_path: str | None = None
    stl_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
