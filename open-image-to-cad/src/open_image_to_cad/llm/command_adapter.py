import json
import subprocess
from typing import Optional, Literal
from pathlib import Path
from .base import BaseLLMAdapter
from ..schemas import CADBrief, RepairContext
import os

class CommandModelAdapter(BaseLLMAdapter):
    def __init__(self):
        self.brief_cmd = os.getenv("COMMAND_MODEL_BRIEF")
        self.cad_cmd = os.getenv("COMMAND_MODEL_CAD")
        self.repair_cmd = os.getenv("COMMAND_MODEL_REPAIR")
        self.timeout = int(os.getenv("OITC_COMMAND_TIMEOUT_SECONDS", os.getenv("OITC_TIMEOUT_SECONDS", "20")))

    def _run_cmd(self, cmd: Optional[str], payload: dict) -> dict:
        if not cmd:
            raise RuntimeError("Command not configured for this operation")

        import shlex
        args = shlex.split(cmd)

        proc = subprocess.run(
            args,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            timeout=self.timeout
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Command failed: {proc.stderr}")

        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise ValueError(f"Command returned invalid JSON: {proc.stdout}")

    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        payload = {"task": "generate_brief", "image_path": str(image_path) if image_path else None, "notes": notes}
        res = self._run_cmd(self.brief_cmd, payload)
        return CADBrief(**res.get("content", {}))

    def generate_cad_code(self, brief_or_text: CADBrief | str, target_engine: Literal["cadquery", "build123d"] = "cadquery") -> str:
        payload = {
            "task": "generate_cad_code",
            "target_engine": target_engine,
            "brief": brief_or_text.model_dump() if isinstance(brief_or_text, CADBrief) else None,
            "text": brief_or_text if isinstance(brief_or_text, str) else None
        }
        res = self._run_cmd(self.cad_cmd, payload)
        return res.get("content", "")

    def repair_code(self, context: RepairContext, code: str, error: str) -> str:
        payload = {
            "task": "repair_cad_code",
            "context": context.model_dump(),
            "code": code,
            "error": error
        }
        res = self._run_cmd(self.repair_cmd, payload)
        return res.get("content", "")
