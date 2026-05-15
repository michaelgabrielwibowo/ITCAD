# Security
CAD code executes arbitrary Python. We employ AST validation (`sandbox.py`) and standard subprocess timeouts, but do not consider this completely isolated from a malicious user providing a hijacked model backend.
