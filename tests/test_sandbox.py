from open_image_to_cad.cad.sandbox import validate_imports


def test_import_allowlist():
    ok, errs = validate_imports('import cadquery as cq\nimport math\nresult=1')
    assert ok
    assert not errs


def test_import_blocklist():
    ok, errs = validate_imports('import os\nresult=1')
    assert not ok
    assert errs
