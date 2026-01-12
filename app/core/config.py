from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS - peut être une liste ou "*" pour tout autoriser
    CORS_ORIGINS: Union[str, List[str]] = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convertit CORS_ORIGINS en liste"""
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
