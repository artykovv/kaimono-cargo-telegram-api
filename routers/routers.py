from fastapi import APIRouter

from .telegram.router import router as telegram
from .branch.router import router as branch
from .address.router import router as address
from .textes.router import router as textes

routers = APIRouter()

routers.include_router(telegram)
routers.include_router(branch)
routers.include_router(address)
routers.include_router(textes)