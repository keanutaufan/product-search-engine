from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
def get_index():
    return FileResponse("app/template/index.html")