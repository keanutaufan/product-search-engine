from app.repository.product import ProductRepository

class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def get_product_using_tsvector(self, search: str) -> list[dict]:
        return self.product_repository.get_product_using_tsvector(search)