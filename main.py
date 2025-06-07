from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.routers import routers
from front.router import router as site

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)


@app.get("/")
async def base_url():
    return {
        "message": "hello world from fastapi"
    }

app.include_router(routers)
app.include_router(site)