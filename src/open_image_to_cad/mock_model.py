from __future__ import annotations

from pathlib import Path


def infer_prompt(text: str | None, image_path: str | None) -> str:
    src = f"{text or ''} {Path(image_path).name if image_path else ''}".lower()
    if "plate" in src and "hole" in src:
        return "plate_2_holes"
    if "cylinder" in src:
        return "cylinder"
    return "box"


def generate_cadquery_code(kind: str) -> str:
    if kind == "plate_2_holes":
        return """import cadquery as cq
length = 40.0
width = 20.0
thickness = 5.0
hole_diameter = 4.0
hole_spacing = 20.0
result = (
    cq.Workplane(\"XY\")
    .box(length, width, thickness)
    .faces(\">Z\")
    .workplane()
    .pushPoints([(-hole_spacing / 2.0, 0.0), (hole_spacing / 2.0, 0.0)])
    .hole(hole_diameter)
)
"""
    if kind == "cylinder":
        return """import cadquery as cq
radius = 10.0
height = 20.0
result = cq.Workplane(\"XY\").circle(radius).extrude(height)
"""
    return """import cadquery as cq
length = 30.0
width = 20.0
height = 10.0
result = cq.Workplane(\"XY\").box(length, width, height)
"""
