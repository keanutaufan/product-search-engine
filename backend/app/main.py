from fastapi import FastAPI

from app.routers.html import html_router

app = FastAPI()

app.include_router(html_router, prefix="")