import time
from typing import Literal
from fastapi import APIRouter, Depends, Query

from app.repository.product import ProductRepository
from app.service.product import ProductService
from app.config.database import get_db_connection


def get_product_repository(db=Depends(get_db_connection)) -> ProductRepository:
    return ProductRepository(db)

def get_product_service(user_repository=Depends(get_product_repository)) -> ProductService:
    return ProductService(user_repository)

router = APIRouter()

@router.get("/")
def search_product(
    service: ProductService = Depends(get_product_service),
    search: str | None = Query(default="", max_length=100),
    method: Literal["tsvector", "sbert"] = "tsvector"
):
    tic = time.perf_counter()
    if (method == "tsvector"):
        data = service.get_product_using_tsvector(search)
    else:
        data = service.get_product_using_sbert(search)
    toc = time.perf_counter()

    response = {
        "response_time": toc - tic,
        "data": data,
    }

    return response