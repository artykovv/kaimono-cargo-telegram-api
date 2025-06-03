import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Client, Branch


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Client, Branch

async def generate_new_code_async(session: AsyncSession, branch_id: int = None) -> dict:
    """
    Generates a new code combining Branch.code with an incremented number.
    If branch_id is provided, uses that branch's code as prefix.
    """
    # Получаем префикс филиала (если указан)
    branch_prefix = ''
    if branch_id:
        branch_result = await session.execute(
            select(Branch.code).where(Branch.id == branch_id)
        )
        branch = branch_result.scalar()
        if branch:
            branch_prefix = branch

    # Получаем все numeric_code
    result = await session.execute(
        select(Client.numeric_code).where(Client.numeric_code.isnot(None))
    )
    codes = result.scalars().all()

    # Определяем максимальное значение
    max_number = max(codes, default=0)
    numeric_code = max_number + 1
    code = f"{branch_prefix}{numeric_code}"  # Например: 'B0001'

    return {
        "numeric_code": numeric_code,  # сохраняем как число
        "code": code                   # отображаем как строку
    }