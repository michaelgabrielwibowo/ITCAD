import os
import typer
from pathlib import Path
from datetime import datetime
from typing import Optional

from .llm import get_adapter
from .pipeline import Pipeline

app = typer.Typer(help="Open Image-to-CAD system")

@app.command()
def version():
    """Show package version and available adapters."""
    typer.echo("open-image-to-cad v0.1.0")
    typer.echo("Available adapters: mock (more coming soon)")

@app.command()
def classify(image_path: Path):
    """Classify an input image type."""
    typer.echo(f"Classifying {image_path} (stub)")

@app.command()
def brief(
    image_path: Path,
    notes: Optional[str] = typer.Option(None, help="Additional context"),
    adapter: str = typer.Option("mock", help="Adapter to use")
):
    """Generate a structured CAD brief from an image."""
    llm = get_adapter(adapter)
    b = llm.generate_brief(image_path, notes)
    typer.echo(b.model_dump_json(indent=2))

@app.command()
def generate(
    image_path: Path,
    notes: Optional[str] = typer.Option(None, help="Additional context"),
    adapter: str = typer.Option("mock", help="Adapter to use"),
    engine: str = typer.Option("cadquery", help="Target CAD engine")
):
    """Run the full pipeline from image to CAD code and STEP file."""
    llm = get_adapter(adapter)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(os.getenv("OITC_OUTPUT_DIR", "outputs")) / timestamp

    pipeline = Pipeline(llm, out_dir)
    typer.echo(f"Running generation using adapter '{adapter}', output to {out_dir}")

    res = pipeline.generate_from_image(image_path, notes, engine)

    if res["status"] == "success":
        typer.secho(f"Success! Model exported to {out_dir / 'model.step'}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Failed. See report in {out_dir / 'validation_report.json'}", fg=typer.colors.RED)

@app.command()
def text(
    prompt: str,
    adapter: str = typer.Option("mock", help="Adapter to use"),
    engine: str = typer.Option("cadquery", help="Target CAD engine")
):
    """Generate CAD code directly from a text prompt."""
    llm = get_adapter(adapter)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(os.getenv("OITC_OUTPUT_DIR", "outputs")) / timestamp

    pipeline = Pipeline(llm, out_dir)
    typer.echo(f"Running text generation using adapter '{adapter}', output to {out_dir}")

    res = pipeline.generate_from_text(prompt, engine)

    if res["status"] == "success":
        typer.secho(f"Success! Model exported to {out_dir / 'model.step'}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Failed. See report in {out_dir / 'validation_report.json'}", fg=typer.colors.RED)

@app.command()
def repair(
    code_file: Path,
    adapter: str = typer.Option("mock", help="Adapter to use")
):
    """Attempt to repair a broken CAD code file."""
    typer.echo(f"Repairing {code_file} (stub - use generate/text for automatic repair)")

@app.command()
def serve(
    port: int = typer.Option(8000, help="Port to listen on"),
    host: str = typer.Option("0.0.0.0", help="Host interface")
):
    """Start the FastAPI backend."""
    import uvicorn
    # Delay import so CLI commands don't require FastAPI
    from .api.main import app as fastapi_app
    typer.echo(f"Starting server on {host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port)

if __name__ == "__main__":
    app()
