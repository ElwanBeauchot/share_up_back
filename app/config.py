import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    mongo_url: str
    database_name: str
    devices_collection_name: str
    debug: bool
    api_key: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()
