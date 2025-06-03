from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from sqlalchemy import select
from fastapi.security.api_key import APIKey
from config.api_config import get_api_key
from models import ChinaAddress

router = APIRouter(prefix="/address", tags=["address"])

@router.get("/")
async def get_branches(
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    query = select(ChinaAddress)
    result = await session.execute(query)
    branches = result.scalars().first()
    return branches
