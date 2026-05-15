# Open Image-to-CAD

A local-first, adapter-based image/text-to-CAD system.

## 1. Project Summary
This project provides a reliable, open-source pipeline to convert single images, technical drawings, or text notes into editable parametric CAD code (CadQuery) and standard CAD artifacts (STEP/STL).

## 2. What it does
- Extracts structural intent from images or text into a structured JSON `CADBrief`.
- Generates editable Python CAD code using CadQuery.
- Validates code execution safely in a sandbox.
- Auto-repairs failing code utilizing error tracebacks.
- Exports standard CAD formats (STEP, STL).

## 3. What it does NOT do
- It does **not** hallucinate exact mesh geometry.
- It is **not** a proprietary SaaS UI.
- It does **not** rely on a secret backend.

## 4. Why single-image CAD is ambiguous
A single image usually lacks exact scale, hidden geometry, internal holes, tolerances, and wall thicknesses. The system tracks these uncertainties and prompts for missing dimensions rather than pretending uncertain details are exact.

## 5. Installation
See documentation for pip/conda paths.

## 6. CLI Usage
open-image-to-cad text "make a 40mm x 20mm x 5mm plate with two 4mm holes" --adapter mock

open-image-to-cad serve

## 7. Model Modes
- **Mock Mode**: Local, deterministic code generation for testing (`--adapter mock`).
- **API-Key Mode**: Uses proprietary LLM endpoints (OpenAI, Gemini).
- **Local Ollama Mode**: Fully private local generation using Ollama.
- **Command / Subscription Bridge Mode**: Connect external CLI tools or organizational gateways via environment variables.

*Note: ChatGPT Plus/Pro subscriptions are not automatically OpenAI API credits. Gemini subscription access is not automatically Gemini API access unless Google provides that path.*

## 8. Development Commands
ruff check .
pytest
open-image-to-cad text "make a plate" --adapter mock

## Roadmap & Docs
See `docs/` for architecture, pipeline design, security limits, and the roadmap.

## License
MIT License.

### Installation Details
**Primary Path (Pip)**
`python -m venv .venv`
`source .venv/bin/activate`
`pip install -e ".[dev]"`

**Fallback Path (Conda)**
`conda env create -f environment.yml`
`conda activate open-image-to-cad`
`pip install -e ".[dev]"`
