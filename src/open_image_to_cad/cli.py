from __future__ import annotations

import json

import typer

from open_image_to_cad.pipeline import run
from open_image_to_cad.schemas import RunRequest

app = typer.Typer(help="Open Image to CAD CLI")


@app.command()
def process(
    text: str = typer.Option("", help="Natural language description"),
    image: str = typer.Option("", help="Image path"),
    output_dir: str = typer.Option("outputs", help="Output directory"),
) -> None:
    if not text and not image:
        raise typer.BadParameter("Provide --text and/or --image")
    req = RunRequest(text=text or None, image_path=image or None, output_dir=output_dir)
    result = run(req)
    typer.echo(json.dumps(result.model_dump(), indent=2))


@app.command()
def desktop() -> None:
    from open_image_to_cad.desktop_app import launch

    launch()


if __name__ == "__main__":
    app()
