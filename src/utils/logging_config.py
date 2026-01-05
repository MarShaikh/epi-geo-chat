import logging
import os
from pathlib import Path


def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO")

    # Use absolute path relative to the project root
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    # Get the root logger
    root_logger = logging.getLogger()

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Set level
    root_logger.setLevel(getattr(logging, log_level))

    # Create formatters and handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)

    # Stream handler (console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
