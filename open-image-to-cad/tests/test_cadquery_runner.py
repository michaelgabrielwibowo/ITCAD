import tempfile
from pathlib import Path
from open_image_to_cad.cad.cadquery_runner import CadQueryRunner
from open_image_to_cad.cad.validators import create_validation_report

def test_runner_valid_code():
    code = """
import cadquery as cq
result = cq.Workplane("XY").box(10, 10, 10)
"""
    runner = CadQueryRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = Path(tmpdir)
        res = runner.run(code, out_dir)
        assert res["ok"] is True
        assert res["exports"]["step"] is True
        assert (out_dir / "model.step").exists()

        report = create_validation_report(res)
        assert report.ok is True

def test_runner_invalid_imports():
    code = """
import os
import cadquery as cq
result = cq.Workplane("XY").box(10, 10, 10)
"""
    runner = CadQueryRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        res = runner.run(code, Path(tmpdir))
        assert res["imports_ok"] is False
        assert "Disallowed import: os" in res["errors"][0]

def test_runner_missing_result():
    code = """
import cadquery as cq
my_box = cq.Workplane("XY").box(10, 10, 10)
"""
    runner = CadQueryRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        res = runner.run(code, Path(tmpdir))
        assert res["execution_ok"] is False
        assert any("Variable 'result' not found" in err for err in res["errors"])
