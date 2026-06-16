from abc import ABC, abstractmethod
from typing import Optional, Literal
from pathlib import Path
from ..schemas import CADBrief, RepairContext

class BaseLLMAdapter(ABC):
    @abstractmethod
    def generate_brief(self, image_path: str | Path | None, notes: Optional[str] = None) -> CADBrief:
        """Generate a CAD brief from an image or notes."""
        pass

    @abstractmethod
    def generate_cad_code(
        self,
        brief_or_text: CADBrief | str,
        target_engine: Literal["cadquery", "build123d"] = "cadquery"
    ) -> str:
        """Generate CAD code from a brief or raw text."""
        pass

    @abstractmethod
    def repair_code(
        self,
        context: RepairContext,
        code: str,
        error: str
    ) -> str:
        """Attempt to repair failed CAD code based on error."""
        pass
