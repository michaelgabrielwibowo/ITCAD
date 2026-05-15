from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pathlib import Path
from pydantic import BaseModel
import os
import shutil

from ..pipeline import Pipeline
from ..llm import get_adapter

app = FastAPI(title="Open Image-to-CAD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateTextRequest(BaseModel):
    prompt: str
    adapter: str = "mock"
    engine: str = "cadquery"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/adapters")
def list_adapters():
    return {
        "adapters": [
            {"id": "mock", "name": "Mock Adapter (No AI)", "status": "available"}
            # other adapters
        ]
    }

@app.post("/text")
def generate_from_text(req: GenerateTextRequest):
    import uuid
    run_id = str(uuid.uuid4())
    out_dir = Path(os.getenv("OITC_OUTPUT_DIR", "outputs")) / run_id

    adapter = get_adapter(req.adapter)
    pipeline = Pipeline(adapter, out_dir)
    res = pipeline.generate_from_text(req.prompt, req.engine)

    return {
        "run_id": run_id,
        "status": res["status"],
        "attempts": res["attempts"],
        "output_dir": str(out_dir)
    }

@app.post("/generate")
def generate_from_image(
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    adapter: str = Form("mock"),
    engine: str = Form("cadquery")
):
    import uuid
    run_id = str(uuid.uuid4())
    out_dir = Path(os.getenv("OITC_OUTPUT_DIR", "outputs")) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    image_path = out_dir / "input.png"
    with open(image_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    llm = get_adapter(adapter)
    pipeline = Pipeline(llm, out_dir)
    res = pipeline.generate_from_image(image_path, notes, engine)

    return {
        "run_id": run_id,
        "status": res["status"],
        "attempts": res["attempts"],
        "output_dir": str(out_dir)
    }

# Serve web frontend if dist exists
web_dist = Path(__file__).parent.parent.parent.parent / "web" / "dist"
if web_dist.exists() and web_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(web_dist), html=True), name="web")
