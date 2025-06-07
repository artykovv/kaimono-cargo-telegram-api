from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from sqlalchemy import select
from fastapi.security.api_key import APIKey
from config.api_config import get_api_key
from models import Text

router = APIRouter(prefix="/textes", tags=["textes"])

@router.get("/{key}")
async def get_text(
    key: str,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    query = select(Text).where(Text.key == key)
    result = await session.execute(query)
    text = result.scalars().first()
    return text
