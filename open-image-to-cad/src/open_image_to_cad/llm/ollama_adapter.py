from typing import Optional, Literal
from pathlib import Path
from .base import BaseLLMAdapter
from ..schemas import CADBrief, RepairContext
import os
import json
import requests

class OllamaAdapter(BaseLLMAdapter):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.text_model = os.getenv("OLLAMA_TEXT_MODEL", "qwen2.5-coder:7b")

        # Verify server is up
        try:
            requests.get(f"{self.base_url}/api/version", timeout=5)
        except requests.exceptions.RequestException:
            raise ValueError(f"Ollama server not responding at {self.base_url}")

    def _call_ollama(self, model: str, prompt: str, system: str = "") -> str:
        res = requests.post(f"{self.base_url}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }, timeout=120)
        res.raise_for_status()
        return res.json()["response"]

    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        if image_path:
            raise NotImplementedError("Image support for Ollama adapter is pending a stable local VLM implementation.")

        sys = "You are converting an input into a structured CAD brief. Output strict JSON matching the CADBrief schema. Mark uncertainty explicitly."
        res = self._call_ollama(self.text_model, notes or "Generate a generic brief.", system=sys)

        text = res.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]

        brief_data = json.loads(text.strip())
        return CADBrief(**brief_data)

    def generate_cad_code(self, brief_or_text: CADBrief | str, target_engine: Literal["cadquery", "build123d"] = "cadquery") -> str:
        sys = f"Generate executable {target_engine} Python code. Define a top-level variable named `result`. Use millimeters. Return code only without markdown."
        content = brief_or_text if isinstance(brief_or_text, str) else brief_or_text.model_dump_json()
        code = self._call_ollama(self.text_model, content, system=sys)
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def repair_code(self, context: RepairContext, code: str, error: str) -> str:
        sys = "Fix the CAD code. Preserve design intent. Keep top-level `result`. Use only approved imports. Return code only."
        user_prompt = f"Engine: {context.target_engine}\n\nOriginal Code:\n{code}\n\nError:\n{error}\n\nPlease fix the code."
        code = self._call_ollama(self.text_model, user_prompt, system=sys)
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
