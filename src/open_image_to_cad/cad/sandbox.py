from __future__ import annotations

import ast

FORBIDDEN = {
    "os",
    "sys",
    "subprocess",
    "pathlib",
    "socket",
    "requests",
    "urllib",
    "shutil",
    "importlib",
}
FORBIDDEN_CALLS = {"__import__", "eval", "exec", "compile", "open", "input", "globals", "locals"}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def validate_imports(code: str, target_engine: str = "cadquery") -> tuple[bool, list[str]]:
    allowed = {"cadquery", "math", "typing"}
    if target_engine == "build123d":
        allowed.add("build123d")

    errors: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, [f"syntax error: {exc}"]

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
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in FORBIDDEN_CALLS:
                errors.append(f"disallowed runtime call: {name}")

    return len(errors) == 0, errors
