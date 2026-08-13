"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_files() -> Tuple[str, ...]:
    """Resolve .env locations relative to common working directories."""
    candidates = [
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        Path(__file__).resolve().parents[3] / ".env",
    ]
    existing = [str(path) for path in candidates if path.is_file()]
    return tuple(existing) or (".env",)


class Settings(BaseSettings):
    """Central configuration for the disease risk prediction system."""

    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="MedAI", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    dataset_path: str = Field(
        default="backend/data/raw/disease_dataset.csv",
        alias="DATASET_PATH",
    )
    target_column: str = Field(default="prognosis", alias="TARGET_COLUMN")
    primary_metric: str = Field(default="macro_f1", alias="PRIMARY_METRIC")
    model_path: str = Field(
        default="backend/models/trained/best_model.joblib",
        alias="MODEL_PATH",
    )
    preprocessor_path: str = Field(
        default="backend/models/trained/preprocessor.joblib",
        alias="PREPROCESSOR_PATH",
    )
    model_metadata_path: str = Field(
        default="backend/models/metadata/model_metadata.json",
        alias="MODEL_METADATA_PATH",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    llm_model: str = Field(default="qwen2.5:7b", alias="LLM_MODEL")

    vector_store_path: str = Field(
        default="backend/models/metadata/faiss_index",
        alias="VECTOR_STORE_PATH",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )
    knowledge_base_path: str = Field(
        default="backend/knowledge_base/medical_documents",
        alias="KNOWLEDGE_BASE_PATH",
    )

    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
