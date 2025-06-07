from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from config.config import API_KEY

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register")
async def page(request: Request):
   
    return templates.TemplateResponse(
        "register.html",
        {
            "title": "Регистрация",
            "API_KEY": API_KEY,
            "request": request
        }
    )