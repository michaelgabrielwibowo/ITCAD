from typing import Optional, Literal
from pathlib import Path
from .base import BaseLLMAdapter
from ..schemas import CADBrief, RepairContext
import os
import json
from openai import OpenAI

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.client = OpenAI(api_key=self.api_key)

    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        messages = [
            {"role": "system", "content": "You are converting an input into a structured CAD brief. Output strict JSON matching the CADBrief schema. Do not invent hidden geometry. Separate known from inferred dimensions. Mark uncertainty explicitly."},
        ]

        content = []
        if image_path:
            import base64
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            })

        if notes:
            content.append({"type": "text", "text": notes})
        else:
            content.append({"type": "text", "text": "Extract brief from image."})

        messages.append({"role": "user", "content": content})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"}
        )

        brief_data = json.loads(response.choices[0].message.content)
        return CADBrief(**brief_data)

    def generate_cad_code(self, brief_or_text: CADBrief | str, target_engine: Literal["cadquery", "build123d"] = "cadquery") -> str:
        prompt = f"Generate executable {target_engine} Python code. Define a top-level variable named `result`. Use millimeters. Avoid file access except normal CAD export. Do not output markdown fences. Return code only."
        if isinstance(brief_or_text, str):
            content = f"Brief/Request: {brief_or_text}"
        else:
            content = f"Brief: {brief_or_text.model_dump_json()}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ]
        )
        code = response.choices[0].message.content.strip()
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        code = response.choices[0].message.content.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
