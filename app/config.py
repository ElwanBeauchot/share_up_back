import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str
    database_name: str
    devices_collection_name: str
    debug: bool

    class Config:
        env_file = ".env"


settings = Settings()
