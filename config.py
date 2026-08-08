# Centralized Configuration Management using Pydantic Settings
# Reference: Pydantic BaseSettings Documentation (https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "info"
    PRIMARY_CAMERA_ID: int = 0
    SECONDARY_CAMERA_ID: int = 1
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    STORAGE_DIR: str = "/app/data"

    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"

settings = Settings()
