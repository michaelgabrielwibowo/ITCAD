import ast
from typing import List, Tuple

ALLOWED_IMPORTS = {"cadquery", "math", "typing"}

def validate_imports(code: str, target_engine: str = "cadquery") -> Tuple[bool, List[str]]:
    """Validate that code only uses allowed imports."""
    allowed = ALLOWED_IMPORTS.copy()
    if target_engine == "build123d":
        allowed.add("build123d")

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"Syntax error: {e}"]

    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base_module = alias.name.split('.')[0]
                if base_module not in allowed:
                    errors.append(f"Disallowed import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base_module = node.module.split('.')[0]
                if base_module not in allowed:
                    errors.append(f"Disallowed import: {node.module}")

    return len(errors) == 0, errors
