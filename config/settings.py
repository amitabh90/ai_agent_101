from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    github_token: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ai_agent_db"
    postgres_user: str = "postgres"
    postgres_password: str
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
