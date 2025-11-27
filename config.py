from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

import os


def get_app_env():
    app_env = os.getenv("APP_ENV", "dev")
    
    if (app_env == "prod"):
        return ".env.prod"
    else:
        return ".env"
     
class Settings(BaseSettings):
    app_name:str = "RAG Search API"
    DB_NAME:str
    DB_USERNAME:str
    DB_PASSWORD:str
    SECRET_KEY:str
    DB_HOST:str
    MEDIA_ROOT:str = "media"
    UPLOAD_DIR:str = "media/raw"
    DATA_ROOT:str = "data"
    CHROMA_DB_PATH:str = "data/chroma_db"
    OPENAI_API_KEY:str
    OPENAI_MODEL:str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL:str = "text-embedding-3-small"
    CHROMA_COLLECTION_NAME:str = "documents"
    RAG_N_RESULTS:int = 5  # Número de chunks similares a recuperar en búsqueda RAG
    model_config = SettingsConfigDict(env_file=get_app_env())
        
@lru_cache()        
def get_settings() -> Settings:
    return Settings()
    