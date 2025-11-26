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
    app_name:str = "My App"
    DB_NAME:str
    DB_USERNAME:str
    DB_PASSWORD:str
    SECRET_KEY:str
    DB_HOST:str
    OPENAI_API_KEY:str
    OPENAI_MODEL:str = "gpt-4o-mini"
    model_config = SettingsConfigDict(env_file=get_app_env())
        
@lru_cache()        
def get_settings() -> Settings:
    return Settings()
    