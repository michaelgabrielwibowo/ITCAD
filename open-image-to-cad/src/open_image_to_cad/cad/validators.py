from typing import Dict, Any
from ..schemas import ValidationReport

def create_validation_report(runner_result: Dict[str, Any], attempt: int = 1) -> ValidationReport:
    return ValidationReport(
        ok=runner_result.get("ok", False),
        syntax_ok=runner_result.get("syntax_ok", False),
        imports_ok=runner_result.get("imports_ok", False),
        execution_ok=runner_result.get("execution_ok", False),
        result_object_found=runner_result.get("result_object_found", False),
        exports=runner_result.get("exports", {}),
        volume=runner_result.get("volume"),
        errors=runner_result.get("errors", []),
        warnings=runner_result.get("warnings", []),
        attempts=attempt
    )
