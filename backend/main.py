"""Backend entry point: `uvicorn main:app`."""

from modules.main.app import create_app

app = create_app()
