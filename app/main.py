from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.devices import router as devices_router

app = FastAPI()
app.include_router(devices_router)

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
    return {"message": "Coonecté à l'API", "data": []}
