from pathlib import Path

from open_image_to_cad.pipeline import run
from open_image_to_cad.schemas import RunRequest


def test_process_text(tmp_path: Path):
    res = run(RunRequest(text="plate with holes", output_dir=str(tmp_path)))
    out = Path(res.output_dir)
    assert (out / "generated_model.py").exists()
    assert (out / "validation_report.json").exists()


def test_run_id_unique(tmp_path: Path):
    a = run(RunRequest(text="box", output_dir=str(tmp_path)))
    b = run(RunRequest(text="box", output_dir=str(tmp_path)))
    assert a.run_id != b.run_id
