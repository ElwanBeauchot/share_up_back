from fastapi import APIRouter
from app.api import routes

router = APIRouter()

# Inclusion des routes
router.include_router(routes.router, tags=["general"])
