import pytest
from open_image_to_cad.llm.command_adapter import CommandModelAdapter

def test_command_adapter_execution(monkeypatch, tmp_path):
    # Create a mock script that acts like our CLI tool
    script = tmp_path / "mock_cmd.py"
    script.write_text("""
import sys, json
data = json.load(sys.stdin)
if data["task"] == "generate_cad_code":
    print(json.dumps({"ok": True, "content": "import cadquery as cq"}))
""")

    monkeypatch.setenv("COMMAND_MODEL_CAD", f"python {script}")
    adapter = CommandModelAdapter()

    code = adapter.generate_cad_code("make a box")
    assert code == "import cadquery as cq"

def test_command_adapter_bad_json(monkeypatch, tmp_path):
    script = tmp_path / "mock_cmd.py"
    script.write_text("print('not json')")

    monkeypatch.setenv("COMMAND_MODEL_CAD", f"python {script}")
    adapter = CommandModelAdapter()

    with pytest.raises(ValueError, match="invalid JSON"):
        adapter.generate_cad_code("make a box")
