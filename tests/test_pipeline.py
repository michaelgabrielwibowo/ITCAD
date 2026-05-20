from pathlib import Path

from open_image_to_cad.pipeline import run
from open_image_to_cad.schemas import RunRequest


def test_process_text(tmp_path: Path):
    res = run(RunRequest(text="plate with holes", output_dir=str(tmp_path)))
    out = Path(res.output_dir)
    assert (out / "generated_model.py").exists()
    assert (out / "validation_report.json").exists()
