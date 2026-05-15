import tempfile
from pathlib import Path
from open_image_to_cad.cad.cadquery_runner import CadQueryRunner

code = """
import cadquery as cq
result = cq.Workplane("XY").box(10, 10, 10)
"""
runner = CadQueryRunner()
with tempfile.TemporaryDirectory() as tmpdir:
    res = runner.run(code, Path(tmpdir))
    print(res)
