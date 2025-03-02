from __future__ import annotations

import importlib
import os
from functools import lru_cache
from logging import getLogger

from anyio import Path
from dotenv import load_dotenv
from msgspec import ValidationError
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

logger = getLogger(__name__)
DEFAULT_MODULE_NAME = "vaait"
version = importlib.metadata.version(DEFAULT_MODULE_NAME)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
    )
    HF_TOKEN: str
    DEVICE: str = "cpu"


class AWSSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AWS_",
        case_sensitive=False,
    )
    S3_BUCKET: str = "ezmednote.com"
    S3_FOLDER: str = "mednoteai"
    SUBMISSION_ID: str
    SUBMISSION_KEY: str
    SUBMISSION_FOLDER: str


@lru_cache
def load_settings() -> (
    tuple[
        AppSettings,
        AWSSettings,
    ]
):
    """Load Settings file.

    As an example, I've commented on how you might go about injecting secrets into the environment for production.

    This fetches a ``.env`` configuration from a Google secret and configures the environment with those variables.

    .. code-block:: python

        secret_id = os.environ.get("ENV_SECRETS", None)
        env_file_exists = os.path.isfile(f"{os.curdir}/.env")
        local_service_account_exists = os.path.isfile(f"{os.curdir}/service_account.json")
        if local_service_account_exists:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"
        project_id = os.environ.get("GOOGLE_PROJECT_ID", None)
        if project_id is None:
            _, project_id = google.auth.default()
            os.environ["GOOGLE_PROJECT_ID"] = project_id
        if not env_file_exists and secret_id:
            secret = secret_manager.get_secret(project_id, secret_id)
            load_dotenv(stream=io.StringIO(secret))

        try:
            settings = ...  # existing code below
        except:
            ...
        return settings

    Returns:
        Settings: application settings
    """
    env_file = Path(f"{os.curdir}/.env")
    if env_file.is_file():
        load_dotenv(env_file)
    try:
        aws: AWSSettings = AWSSettings()
        app: AppSettings = AppSettings()

    except ValidationError:
        logger.exception("Could not load settings")
        raise
    return app, aws


app, aws = load_settings()
