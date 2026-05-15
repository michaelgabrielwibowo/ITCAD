import tempfile
from pathlib import Path
from open_image_to_cad.pipeline import Pipeline
from open_image_to_cad.llm.mock_adapter import MockLLMAdapter

def test_pipeline_text_mock():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        adapter = MockLLMAdapter()
        pipeline = Pipeline(adapter, out_dir)

        result = pipeline.generate_from_text("make a plate")

        assert result["status"] == "success"
        assert (out_dir / "generated_model.py").exists()
        assert (out_dir / "model.step").exists()
        assert (out_dir / "validation_report.json").exists()

def test_pipeline_image_mock():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        adapter = MockLLMAdapter()
        pipeline = Pipeline(adapter, out_dir)

        result = pipeline.generate_from_image(Path("dummy.png"))

        assert result["status"] == "success"
        assert (out_dir / "brief.json").exists()
        assert (out_dir / "generated_model.py").exists()
        assert (out_dir / "model.step").exists()
