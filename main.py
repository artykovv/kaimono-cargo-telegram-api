from fastapi import FastAPI

from routers.routers import routers

app = FastAPI()

@app.get("/")
async def base_url():
    return {
        "message": "hello world from fastapi"
    }

app.include_router(routers)