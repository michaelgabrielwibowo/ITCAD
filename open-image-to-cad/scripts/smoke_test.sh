#!/bin/bash
set -e

echo "Running ruff..."
ruff check .

echo "Running pytest..."
PYTHONPATH=src pytest

echo "Running mock text generation smoke test..."
PYTHONPATH=src python -m open_image_to_cad.cli text "make a 40mm x 20mm x 5mm plate with two 4mm holes" --adapter mock

# Find the latest output directory
LATEST_DIR=$(ls -td outputs/* | head -1)

echo "Verifying output in $LATEST_DIR..."
ls -l "$LATEST_DIR"
test -f "$LATEST_DIR/generated_model.py" || (echo "ERROR: generated_model.py missing" && false)
test -f "$LATEST_DIR/validation_report.json" || (echo "ERROR: validation_report.json missing" && false)
test -f "$LATEST_DIR/model.step" || (echo "ERROR: model.step missing" && false)

echo "Smoke test passed successfully."
