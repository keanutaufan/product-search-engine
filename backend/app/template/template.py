from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/template")

def get_template() -> Jinja2Templates:
    return templates