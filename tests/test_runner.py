from open_image_to_cad.cad.cadquery_runner import _parse_runner_stdout


def test_parse_runner_stdout_with_noise():
    stdout = "hello from model\n__OITC_REPORT__{\"result_object_found\": true, \"step\": true, \"stl\": false, \"warnings\": []}\n"
    parsed, warnings = _parse_runner_stdout(stdout)
    assert parsed is not None
    assert parsed["step"] is True
    assert warnings == []
