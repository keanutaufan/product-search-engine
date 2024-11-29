from fastapi import APIRouter

from app.routers.root import router as root_router
from app.routers.healthz import router as healthz_router
from app.routers.product import router as product_router

html_router = APIRouter()

html_router.include_router(root_router, prefix="")
html_router.include_router(healthz_router, prefix="/healthz")
html_router.include_router(product_router, prefix="/product")