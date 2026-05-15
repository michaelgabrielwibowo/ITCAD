import pytest
from open_image_to_cad.schemas import CADBrief, InputType, Dimension, DimensionSource

def test_cadbrief_validation():
    brief = CADBrief(
        title="Test Brief",
        input_type=InputType.SIMPLE_GEOMETRIC_PART,
        description="A simple block",
        known_dimensions=[
            Dimension(name="length", value=10.0, unit="mm", confidence=1.0, source=DimensionSource.KNOWN)
        ],
        confidence=0.9
    )
    assert brief.title == "Test Brief"
    assert len(brief.known_dimensions) == 1
    assert brief.known_dimensions[0].value == 10.0

def test_cadbrief_invalid_confidence():
    with pytest.raises(ValueError):
        CADBrief(
            title="Test Brief",
            description="A simple block",
            confidence=1.5 # Invalid
        )
