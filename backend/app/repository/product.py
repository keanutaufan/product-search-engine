from psycopg.connection import Connection
from psycopg.rows import dict_row

class ProductRepository:
    def __init__(self, db: Connection):
        self.db = db

    def get_product_using_tsvector(self, search: str) -> list[dict]:
        query = "SELECT * FROM search_products(%s) LIMIT 50"
        with self.db.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (search,))
            return cursor.fetchall()

