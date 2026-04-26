from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.devices import router as devices_router
from app.routes.p2p import router as p2p_router
from app import logging_config  # Import pour configurer le logging

app = FastAPI()
app.include_router(devices_router)
app.include_router(p2p_router)

# CORS pour Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_data():
    return {"message": "Connecté à l'API yahou", "data": []}
