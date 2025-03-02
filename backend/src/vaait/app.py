"""Minimal Litestar application."""
from __future__ import annotations

import logging

from backend.src.vaait.controllers.mednote import Extract, Reference, Report, Storage, Transcribe

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.logging import LoggingConfig

cors_config = CORSConfig(
    allow_origins=["https://ezmednote.com", "http://localhost:5173"],
    allow_credentials=True,
)
logging_config = LoggingConfig(
    root={"level": logging.getLevelName(logging.INFO), "handlers": ["console"]},
    formatters={"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
)

app = Litestar(
    route_handlers=[Storage, Transcribe, Report, Reference, Extract],
    cors_config=cors_config,
    logging_config=logging_config,
)
