from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class InputType(str, Enum):
    TECHNICAL_DRAWING = "technical_drawing"
    ORTHOGRAPHIC_DRAWING = "orthographic_drawing"
    ROUGH_SKETCH = "rough_sketch"
    PRODUCT_PHOTO = "product_photo"
    CAD_SCREENSHOT = "cad_screenshot"
    SIMPLE_GEOMETRIC_PART = "simple_geometric_part"
    UNKNOWN = "unknown"

class DimensionSource(str, Enum):
    KNOWN = "known"
    INFERRED = "inferred"
    DEFAULT = "default"
    USER = "user"

class Dimension(BaseModel):
    name: str
    value: float
    unit: str = "mm"
    confidence: float = Field(ge=0.0, le=1.0)
    source: DimensionSource

class PrimitiveType(str, Enum):
    BOX = "box"
    CYLINDER = "cylinder"
    SPHERE = "sphere"
    CONE = "cone"
    EXTRUDE = "extrude"
    REVOLVE = "revolve"
    UNKNOWN = "unknown"

class Primitive(BaseModel):
    type: PrimitiveType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)

class FeatureType(str, Enum):
    HOLE = "hole"
    SLOT = "slot"
    FILLET = "fillet"
    CHAMFER = "chamfer"
    POCKET = "pocket"
    BOSS = "boss"
    RIB = "rib"
    PATTERN = "pattern"
    THREAD = "thread"
    UNKNOWN = "unknown"

class Feature(BaseModel):
    type: FeatureType
    location: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    visible: bool = True

class Uncertainty(BaseModel):
    field: str
    reason: str
    impact: str
    suggested_question: str

class CADBrief(BaseModel):
    title: str
    input_type: InputType = InputType.UNKNOWN
    units: str = "mm"
    object_category: Optional[str] = None
    description: str
    known_dimensions: List[Dimension] = Field(default_factory=list)
    inferred_dimensions: List[Dimension] = Field(default_factory=list)
    primitives: List[Primitive] = Field(default_factory=list)
    features: List[Feature] = Field(default_factory=list)
    symmetries: List[str] = Field(default_factory=list)
    manufacturing_notes: List[str] = Field(default_factory=list)
    uncertainties: List[Uncertainty] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    user_questions: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    source_notes: Optional[str] = None

class ValidationReport(BaseModel):
    ok: bool = False
    syntax_ok: bool = False
    imports_ok: bool = False
    execution_ok: bool = False
    result_object_found: bool = False
    exports: Dict[str, bool] = Field(default_factory=dict)
    bounding_box: Optional[Dict[str, float]] = None
    volume: Optional[float] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    attempts: int = 1

class RepairContext(BaseModel):
    original_text: Optional[str] = None
    brief: Optional[CADBrief] = None
    target_engine: str = "cadquery"
    validation_report: ValidationReport
    traceback: str
