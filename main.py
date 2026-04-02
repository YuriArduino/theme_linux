"""Run themectl local web application."""

import uvicorn

from app.main import app
from app.utils.config import Settings


def main() -> None:
    """CLI entrypoint for package script."""
    uvicorn.run(app, host=Settings.HOST, port=Settings.PORT)


if __name__ == "__main__":
    main()
