import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Setting object that set a default configuration
    and override it with the env file specified in the FMDS_ENV_FILE var env.
    """

    upload_directory: str = "/tmp/fmds/upload"

    class Config:
        env_file = os.getenv("FMDS_ENV_FILE", ".env")
