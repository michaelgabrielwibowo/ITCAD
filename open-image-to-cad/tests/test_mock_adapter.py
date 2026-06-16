from open_image_to_cad.llm.mock_adapter import MockLLMAdapter

def test_mock_adapter_brief():
    adapter = MockLLMAdapter()
    brief = adapter.generate_brief(None, "make a plate")
    assert brief.title == "Mock Plate with Holes"
    assert brief.known_dimensions[0].name == "length"
    assert brief.known_dimensions[0].value == 40.0

def test_mock_adapter_code():
    adapter = MockLLMAdapter()
    code = adapter.generate_cad_code("make a plate")
    assert "import cadquery as cq" in code
    assert "cq.Workplane" in code
