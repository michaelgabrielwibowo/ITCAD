from typing import Optional, Literal
from pathlib import Path
from .base import BaseLLMAdapter
from ..schemas import CADBrief, RepairContext
import os
import json

class GeminiAdapter(BaseLLMAdapter):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        prompt = "You are converting an input into a structured CAD brief. Output strict JSON matching the CADBrief schema. Do not invent hidden geometry. Separate known from inferred dimensions. Mark uncertainty explicitly.\n\n"
        if notes:
            prompt += f"Notes: {notes}\n"

        inputs = [prompt]
        if image_path:
            import PIL.Image
            img = PIL.Image.open(image_path)
            inputs.append(img)

        response = self.client.generate_content(inputs)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]

        brief_data = json.loads(text.strip())
        return CADBrief(**brief_data)

    def generate_cad_code(self, brief_or_text: CADBrief | str, target_engine: Literal["cadquery", "build123d"] = "cadquery") -> str:
        prompt = f"Generate executable {target_engine} Python code. Define a top-level variable named `result`. Use millimeters. Return code only. Do not output markdown fences."
        if isinstance(brief_or_text, str):
            content = f"Brief/Request: {brief_or_text}"
        else:
            content = f"Brief: {brief_or_text.model_dump_json()}"

        response = self.client.generate_content(f"{prompt}\n\n{content}")
        code = response.text.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()

    def repair_code(self, context: RepairContext, code: str, error: str) -> str:
        sys_prompt = "Fix the CAD code. Preserve design intent. Keep top-level `result`. Use only approved imports. Return code only. Do not add Markdown blocks."
        user_prompt = f"Engine: {context.target_engine}\n\nOriginal Code:\n{code}\n\nError:\n{error}\n\nPlease fix the code."

        response = self.client.generate_content(f"{sys_prompt}\n\n{user_prompt}")
        code = response.text.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
