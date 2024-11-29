import time
from typing import Literal
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.repository.product import ProductRepository
from app.config.database import get_db_connection
from app.service.product import ProductService
from app.template.template import get_template


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


@router.get("/{id}")
def get_product_by_id(
    service: ProductService = Depends(get_product_service),
    template: Jinja2Templates = Depends(get_template),
    request: Request = Request,
    id: int = 1,
):
    product = service.get_product_by_id(id)
    if product is None:
        raise HTTPException(status_code=404, detail="Not found")
    
    return template.TemplateResponse(
        request=request,
        name="product.html",
        context=product,
        status_code=200,
    )