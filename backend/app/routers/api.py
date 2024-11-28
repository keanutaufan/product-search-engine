from fastapi import APIRouter

from app.routers.healthz import router as healthz_router
from app.routers.product import router as product_router

api_router = APIRouter()

api_router.include_router(healthz_router, prefix="/healthz")
api_router.include_router(product_router, prefix="/product")