from pathlib import Path
from typing import Dict, Any, Optional

from .schemas import CADBrief, RepairContext
from .llm.base import BaseLLMAdapter
from .cad.cadquery_runner import CadQueryRunner
from .cad.validators import create_validation_report

class Pipeline:
    def __init__(
        self,
        llm_adapter: BaseLLMAdapter,
        output_dir: Path,
        max_repair_attempts: int = 3,
        timeout_seconds: int = 20
    ):
        self.llm_adapter = llm_adapter
        self.output_dir = output_dir
        self.max_repair_attempts = max_repair_attempts
        self.cad_runner = CadQueryRunner(timeout_seconds=timeout_seconds)

    def generate_from_text(self, text: str, target_engine: str = "cadquery") -> Dict[str, Any]:
        """Run the text-to-CAD pipeline."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate brief (optional for text, but we'll adapt text into a mock brief for structured repair context)
        # We can skip generating a formal brief for simple text to save time, or do it.
        # For this MVP, we just pass the text directly to generate_cad_code

        # 2. Generate code
        code = self.llm_adapter.generate_cad_code(text, target_engine) # type: ignore

        with open(self.output_dir / "generated_model.py", "w") as f:
            f.write(code)

        # 3. Validate
        return self._validate_and_repair(code, target_engine, text, None)

    def generate_from_image(self, image_path: str | Path, notes: Optional[str] = None, target_engine: str = "cadquery") -> Dict[str, Any]:
        """Run the image-to-CAD pipeline."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate brief
        brief = self.llm_adapter.generate_brief(image_path, notes)

        with open(self.output_dir / "brief.json", "w") as f:
            f.write(brief.model_dump_json(indent=2))

        # 2. Generate code
        code = self.llm_adapter.generate_cad_code(brief, target_engine)

        with open(self.output_dir / "generated_model.py", "w") as f:
            f.write(code)

        # 3. Validate
        return self._validate_and_repair(code, target_engine, None, brief)

    def _validate_and_repair(
        self,
        initial_code: str,
        target_engine: str,
        original_text: Optional[str],
        brief: Optional[CADBrief]
    ) -> Dict[str, Any]:

        current_code = initial_code

        for attempt in range(1, self.max_repair_attempts + 2):
            result_info = self.cad_runner.run(current_code, self.output_dir)
            report = create_validation_report(result_info, attempt)

            with open(self.output_dir / "validation_report.json", "w") as f:
                f.write(report.model_dump_json(indent=2))

            if report.ok:
                return {
                    "status": "success",
                    "attempts": attempt,
                    "report": report
                }

            if attempt > self.max_repair_attempts:
                break

            # Need repair
            repair_dir = self.output_dir / "attempts"
            repair_dir.mkdir(exist_ok=True)

            with open(repair_dir / f"attempt_{attempt}.py", "w") as f:
                f.write(current_code)

            error_str = "\n".join(report.errors)
            with open(repair_dir / f"attempt_{attempt}_error.txt", "w") as f:
                f.write(error_str)

            context = RepairContext(
                original_text=original_text,
                brief=brief,
                target_engine=target_engine,
                validation_report=report,
                traceback=error_str
            )

            current_code = self.llm_adapter.repair_code(context, current_code, error_str)

            with open(self.output_dir / "generated_model.py", "w") as f:
                f.write(current_code)

        return {
            "status": "failed",
            "attempts": attempt,
            "report": report
        }
