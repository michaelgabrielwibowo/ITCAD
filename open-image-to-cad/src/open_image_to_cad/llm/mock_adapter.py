from typing import Optional, Literal
from pathlib import Path
from .base import BaseLLMAdapter
from ..schemas import (
    CADBrief, InputType, Dimension, DimensionSource, Primitive, PrimitiveType,
    Feature, FeatureType, RepairContext
)

class MockLLMAdapter(BaseLLMAdapter):
    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        # Return a deterministic brief for testing
        brief = CADBrief(
            title="Mock Plate with Holes",
            input_type=InputType.SIMPLE_GEOMETRIC_PART,
            description="A rectangular plate with two holes.",
            known_dimensions=[
                Dimension(name="length", value=40.0, unit="mm", confidence=1.0, source=DimensionSource.KNOWN),
                Dimension(name="width", value=20.0, unit="mm", confidence=1.0, source=DimensionSource.KNOWN),
                Dimension(name="thickness", value=5.0, unit="mm", confidence=1.0, source=DimensionSource.KNOWN),
            ],
            primitives=[
                Primitive(type=PrimitiveType.BOX, parameters={"length": 40.0, "width": 20.0, "height": 5.0}, confidence=0.9)
            ],
            features=[
                Feature(type=FeatureType.HOLE, parameters={"diameter": 4.0, "count": 2}, confidence=0.9)
            ],
            confidence=0.95
        )
        return brief

    def generate_cad_code(
        self,
        brief_or_text: CADBrief | str,
        target_engine: Literal["cadquery", "build123d"] = "cadquery"
    ) -> str:
        if target_engine == "cadquery":
            return """import cadquery as cq

# A rectangular plate 40 x 20 x 5 mm
length = 40.0
width = 20.0
thickness = 5.0
hole_diameter = 4.0

# Create the base plate and two holes
result = (
    cq.Workplane("XY")
    .box(length, width, thickness)
    .faces(">Z")
    .workplane()
    .pushPoints([(-10, 0), (10, 0)])
    .hole(hole_diameter)
)
"""
        else:
            return """from build123d import *

with BuildPart() as result:
    Box(40, 20, 5)
"""

    def repair_code(self, context: RepairContext, code: str, error: str) -> str:
        # Just return the same valid code for mock purposes
        return self.generate_cad_code("repair", context.target_engine) # type: ignore
