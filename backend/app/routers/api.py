from fastapi import APIRouter

from app.routers.healthz import router as healthz_router

api_router = APIRouter()

api_router.include_router(healthz_router, prefix="/healthz")