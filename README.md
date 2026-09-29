# Open Image to CAD (Practical MVP)

Yes — this now gives you a **single place to put images and/or text** and process into CAD outputs.

## What you get
- Input: text prompt and/or image file.
- Output folder per run with:
  - `generated_model.py`
  - `validation_report.json`
  - `model.step` (when CadQuery export succeeds)
  - `model.stl` (best effort)
- Safety gate for imports before execution.
- Timeout-based subprocess execution.
- CLI + Desktop app.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## CLI usage
```bash
open-image-to-cad process --text "make a 40x20x5 mm plate with two holes"
open-image-to-cad process --image ./part.png
open-image-to-cad process --text "simple cylinder" --image ./sketch.png --output-dir ./outputs
```

## Desktop app
```bash
open-image-to-cad desktop
```
- Choose an image (optional)
- Enter prompt text (optional)
- Click **Generate CAD**
- Copy/open output paths from result JSON

## Production notes
- Current model generation is deterministic mock logic for reliability.
- CAD execution is real CadQuery subprocess execution.
- Generated geometry still requires engineering review before manufacturing.

## Troubleshooting
- If `model.step` is missing, check `validation_report.json` for exporter/runtime errors.
- If nothing is generated, ensure you provided at least one of `--text` or `--image`.


## Credential handling

Keep Gemini and other backend API keys in ignored local environment files or a deployment secret store. Commit only empty or clearly placeholder examples. Do not put backend keys in client bundles, comments, logs, issues, or archives. Keep service-account private keys outside the repository. `.gitignore` does not remove tracked files or old commits. Revoke any exposed key and check usage and billing. Firebase web API keys are client identifiers; restrict them to required Firebase APIs and exclude the Generative Language API. Use a separate backend Gemini key. See [Google credential response](https://docs.cloud.google.com/docs/security/compromised-credentials) and [Firebase API key guidance](https://firebase.google.com/docs/projects/api-keys).
