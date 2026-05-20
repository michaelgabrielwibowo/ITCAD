from __future__ import annotations

import ast

FORBIDDEN = {"os", "sys", "subprocess", "pathlib", "socket", "requests", "urllib", "shutil", "importlib"}


def validate_imports(code: str, target_engine: str = "cadquery") -> tuple[bool, list[str]]:
    allowed = {"cadquery", "math", "typing"}
    if target_engine == "build123d":
        allowed.add("build123d")
    errors: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"syntax error: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in FORBIDDEN or top not in allowed:
                    errors.append(f"disallowed import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod in FORBIDDEN or mod not in allowed:
                errors.append(f"disallowed import-from: {node.module}")
    return len(errors) == 0, errors
