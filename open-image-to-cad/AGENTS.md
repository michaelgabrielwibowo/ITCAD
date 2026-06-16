# Instructions for AI Coding Agents

- Always edit source files, not generated binaries.
- Generated CAD artifacts must be created through scripts.
- Do not manually edit STEP/STL/GLB.
- Keep large outputs out of git unless explicitly requested.
- Prefer STEP as the primary CAD artifact.
- Run tests (`pytest`) before final answer.
- Run `ruff check .` before final answer.
- Use mock adapter for deterministic tests.
- Never pretend image-derived geometry is exact. Document uncertainty.
- Do not add proprietary SaaS dependencies.
- Do not use Zoo API as required backend.
- Do not copy Zoo branding.
- Do not commit secrets.
- Preserve license notices.
