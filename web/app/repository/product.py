from collections import defaultdict

from psycopg.connection import Connection
from psycopg.rows import dict_row
import numpy as np
from numpy.typing import ArrayLike
import pandas as pd

class ProductRepository:
    df: pd.DataFrame
    tokenized_titles: pd.Series
    ids: ArrayLike
    titles: ArrayLike
    descriptions = ArrayLike
    idf: dict
    avgdl: float

    def __init__(self, db: Connection, csv_path: str = ""):
        self.db = db
        self.df = pd.read_csv(csv_path)
        self.titles = self.df["TITLE"].values
        self.ids = self.df["PRODUCT_ID"].values
        self.descriptions = self.df["DESCRIPTION"].values
        self.tokenized_titles = [doc.lower().split(" ") for doc in self.titles]

        N = len(self.tokenized_titles)
        word_doc_count = defaultdict(int)
        for doc in self.tokenized_titles:
            unique_words = set(doc)
            for word in unique_words:
                word_doc_count[word] += 1

        self.idf = {word: np.log(((N - count + 0.5) / (count + 0.5)) + 1) for word, count in word_doc_count.items()}
        self.avgdl = sum(len(sentence) for sentence in self.tokenized_titles) / N

    def __realmen_bm25(self, word: str, sentence: str, idf: dict, avgdl: float, k=1.2, b=0.75) -> float:
        freq = sentence.count(word)
        tf = (freq * (k + 1)) / (freq + k * (1 - b + b * len(sentence) / avgdl))
        return tf * idf.get(word, 0)

    def get_product_by_id(self, id: int) -> dict | None:
        query = "SELECT product_id AS id, title, bullet_points, description FROM product WHERE product_id = %s"
        with self.db.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (id,))
            return cursor.fetchone()

    def get_product_using_tsvector(self, search: str) -> list[dict]:
        query = "SELECT * FROM search_tsvector(%s) LIMIT 50"
        with self.db.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (search,))
            return cursor.fetchall()

    def get_product_using_sbert(self, vector: list) -> list[dict]:
        query = "SELECT * FROM search_sbert(50, %s::VECTOR) LIMIT 50"
        with self.db.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, (vector,))
            return cursor.fetchall()
        
    def get_product_using_realmen_bm25(self, search: str) -> list[dict]:
        tokenized_query = search.lower().split(" ")
        scores = []

        for tokenized_title, id, title, description in zip(self.tokenized_titles, self.ids, self.titles, self.descriptions):
            score = sum(self.__realmen_bm25(word, tokenized_title, self.idf, self.avgdl) for word in tokenized_query)
            scores.append({
                "id": id,
                "title": title,
                "description": description,
                "rank": score,
            })
        
        return sorted(scores, key=lambda x: x["rank"], reverse=True)[:50]