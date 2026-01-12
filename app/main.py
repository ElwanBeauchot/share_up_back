from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import router

app = FastAPI(
    title="Share Up API",
    description="API backend pour l'application Share Up",
    version="1.0.0"
)

# Configuration CORS pour permettre les connexions depuis Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(router, prefix=settings.API_V1_PREFIX)
