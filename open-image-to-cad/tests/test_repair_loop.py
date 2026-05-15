import tempfile
from pathlib import Path
from typing import Literal, Optional
from open_image_to_cad.pipeline import Pipeline
from open_image_to_cad.llm.base import BaseLLMAdapter
from open_image_to_cad.schemas import CADBrief, RepairContext, InputType

class FailingMockAdapter(BaseLLMAdapter):
    def __init__(self):
        self.attempts = 0

    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        return CADBrief(
            title="Test",
            description="Test",
            input_type=InputType.UNKNOWN,
            confidence=1.0
        )

    def generate_cad_code(self, brief_or_text: CADBrief | str, target_engine: Literal["cadquery", "build123d"] = "cadquery") -> str:
        # First attempt: invalid code
        return "invalid python syntax..."

    def repair_code(self, context: RepairContext, code: str, error: str) -> str:
        self.attempts += 1
        # Second attempt: valid code
        return """
import cadquery as cq
result = cq.Workplane("XY").box(10, 10, 10)
"""

def test_repair_loop():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        adapter = FailingMockAdapter()
        pipeline = Pipeline(adapter, out_dir, max_repair_attempts=2)

        result = pipeline.generate_from_text("make something")

        assert result["status"] == "success"
        assert result["attempts"] == 2
        assert adapter.attempts == 1
        assert (out_dir / "attempts" / "attempt_1.py").exists()
        assert (out_dir / "attempts" / "attempt_1_error.txt").exists()
        assert (out_dir / "model.step").exists()
