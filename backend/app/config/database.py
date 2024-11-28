import os
from psycopg.connection import Connection
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "rsbp"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

db_pool = ConnectionPool(
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}",
    min_size=1,
    max_size=10,
    timeout=10,
)

def get_db_connection() -> Connection:
    conn = db_pool.getconn()
    try:
        return conn
    finally:
        db_pool.putconn(conn)