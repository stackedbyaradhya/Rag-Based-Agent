from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG Knowledgebase API"
    environment: str = "development"
    port: int = 8000

    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/ragkb", alias="DATABASE_URL")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_token_exp_minutes: int = 60 * 24

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384
    llm_model: str = Field(default="openai/gpt-oss-120b:free", alias="LLM_MODEL")

    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    max_file_size_mb: int = 20
    allowed_file_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt", ".md")
    chunk_size: int = 1200
    chunk_overlap: int = 200
    top_k: int = 5
    similarity_threshold: float = 0.45

    cors_origins: list[str] = ["*"]
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
