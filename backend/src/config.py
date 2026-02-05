from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    cohere_api_key: Optional[str]
    qdrant_url: Optional[str]
    qdrant_cluster_id: Optional[str]
    neon_db_url: Optional[str]
    qdrant_api_key: Optional[str]  

    class Config:
        env_file = ".env"
        case_sensitive = False  

settings = Settings()
