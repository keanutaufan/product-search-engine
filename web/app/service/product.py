from sentence_transformers import SentenceTransformer

from app.repository.product import ProductRepository

minilm_embedder = SentenceTransformer("all-MiniLM-L6-v2")

class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def get_product_by_id(self, id: int) -> dict | None:
        return self.product_repository.get_product_by_id(id)

    def get_product_using_tsvector(self, search: str) -> list[dict]:
        return self.product_repository.get_product_using_tsvector(search)
    
    def get_product_using_sbert(self, search: str):
        vector = minilm_embedder.encode(search, convert_to_tensor=False).tolist()
        return self.product_repository.get_product_using_sbert(vector)
    
    def get_product_using_realmen_bm25(self, search: str):
        return self.product_repository.get_product_using_realmen_bm25(search)