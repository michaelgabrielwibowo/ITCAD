from typer.testing import CliRunner
from open_image_to_cad.cli import app

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "open-image-to-cad v0.1.0" in result.stdout

def test_text_command():
    result = runner.invoke(app, ["text", "make a plate", "--adapter", "mock"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    assert "outputs/" in result.stdout
