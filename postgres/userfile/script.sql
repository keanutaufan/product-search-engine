CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE product (
	product_id INT PRIMARY KEY,
	title text,
	bullet_points text,
	description text,
	product_type_id int,
	product_length double precision,
	embeddings vector(384)
);

COPY product(product_id, title, bullet_points, description, product_type_id, product_length, embeddings)
FROM '/usr/share/postgresql/embeddings.csv'
DELIMITER ','
CSV HEADER;

ALTER TABLE product ADD COLUMN textsearchable_index_col tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(bullet_points, '')), 'C')
) STORED;

CREATE INDEX textsearch_idx ON product USING gin (textsearchable_index_col);

CREATE INDEX ON product USING hnsw (embeddings vector_l2_ops);

CREATE OR REPLACE FUNCTION search_tsvector(
    search_query text,
    min_rank float DEFAULT 0.0,
    weights float4[] DEFAULT '{0.1,0.2,0.4,1.0}'
)
RETURNS TABLE (
    id int,
    title text,
    description text,
    rank real
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.product_id,
        p.title,
		left(p.description, 500),
        ts_rank(weights, p.textsearchable_index_col, q) as rank
    FROM 
        product p,
        phraseto_tsquery('english', search_query) q
    WHERE 
        p.textsearchable_index_col @@ q
        AND ts_rank(weights, p.textsearchable_index_col, q) >= min_rank
    ORDER BY 
        rank DESC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION search_sbert(
	k int,
    query_embedding vector
)
RETURNS TABLE (
    id int,
	title text,
	description text,
    rank float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.product_id,
        p.title,
		p.description,
        1 - (embeddings <-> query_embedding) AS similarity
    FROM product p
    ORDER BY embeddings <-> query_embedding
    LIMIT k;
end;
$$ LANGUAGE plpgsql;