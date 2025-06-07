import asyncio
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from sqlalchemy.orm import selectinload, joinedload
from fastapi.security.api_key import APIKey

from config.api_config import get_api_key
from models import Client, Product, Branch
from schemas.telegram import CreateClient
from functions.generate_code import generate_new_code_async
from config.status import ProductStatus
from functions.registration_success import send_registration_success_message

router = APIRouter(prefix="/telegram", tags=["telegram"])

@router.post("/register/clients")
async def register_client(
    query: CreateClient,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    
    # Проверяем, существует ли клиент с такими же параметрами
    existing_client = await session.execute(select(Client).filter_by(
        name=query.name, 
        number=query.number, 
        city=query.city, 
        telegram_chat_id=query.telegram_chat_id
        )
    )
    existing_client = existing_client.scalar()

    if existing_client:
        # Возвращаем информацию о существующем клиенте
        return {"client": existing_client}

    # Если клиент не существует, создаем нового
    gen_code = await generate_new_code_async(session, query.branch_id)

    stmt = insert(Client).values(
        name=query.name,
        code=gen_code["code"],
        number=query.number,
        city=query.city,
        telegram_chat_id=query.telegram_chat_id,
        registered_at=datetime.now(timezone(timedelta(hours=6))).replace(tzinfo=None),
        branch_id=query.branch_id,
        numeric_code=int(gen_code["numeric_code"])
    )
    await session.execute(stmt)
    await session.commit()

    # После сохранения клиента делаем запрос к базе данных, чтобы получить только что созданный объект
    created_client = await session.execute(select(Client).filter_by(
        name=query.name, 
        number=query.number, 
        city=query.city
        )
    )
    created_client = created_client.scalar()
    asyncio.create_task(send_registration_success_message(created_client))

    return created_client

@router.get("/bool/{telegram_chat_id}")
async def get_client_chat_id(
    telegram_chat_id: str, 
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
) -> bool:
    query = select(Client).where(Client.telegram_chat_id == telegram_chat_id)
    result = await session.execute(query)
    client = result.scalars().first()
    return client is not None

@router.get("/{telegram_chat_id}")
async def for_telegram_get_client(
    telegram_chat_id: str,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key),
):
    query = (
        select(Client)
        .options(joinedload(Client.branch))
        .where(Client.telegram_chat_id == telegram_chat_id)
    )
    result = await session.execute(query)
    client = result.scalars().all()
    return client

@router.get("/products/status/inwarehouse/{telegram_chat_id}")
async def foo_telegram_main_test(
    telegram_chat_id: str,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    # Запрашиваем клиента по telegram_chat_id с подгрузкой продуктов (joinedload)
    query = (
    select(Client)
        .options(
            joinedload(Client.products)          # жадная загрузка продуктов
            .joinedload(Product.status)          # жадная загрузка статуса у каждого продукта
        )
        .where(Client.telegram_chat_id == telegram_chat_id)
    )
    result = await session.execute(query)
    client = result.scalars().first()
    # return client

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # Фильтруем продукты по условию "product.status == ProductStatus.STOCK" 
    non_picked_up_products = [product for product in client.products if product.status.name == ProductStatus.STOCK]

    if not non_picked_up_products:
        return {"message": "No products found for this client"}

    # Считаем суммарную цену
    total_price = sum(product.price for product in non_picked_up_products if product.price is not None)

    # Считаем суммарный вес
    total_weight = sum(product.weight for product in non_picked_up_products if product.weight is not None)

    # Готовим структуру ответа
    client_data = {
        "id": client.id,
        "name": client.name,
        "number": client.number,
        "city": client.city,
        "total_price": total_price,
        "total_weight": total_weight,
        "products": [
            {
                "id": product.id,
                "product_code": product.product_code,
                "weight": product.weight,
                "price": product.price,
                "date": product.date.isoformat() if product.date else None,
                "status": product.status.name
            }
            for product in non_picked_up_products
        ]
    }

    return client_data


@router.get("/products/status/inchina/{telegram_chat_id}")
async def foo_telegram_main_test(
    telegram_chat_id: str,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    # Query the client by their ID with related products
    query = (
    select(Client)
        .options(
            joinedload(Client.products)          # жадная загрузка продуктов
            .joinedload(Product.status)          # жадная загрузка статуса у каждого продукта
        )
        .where(Client.telegram_chat_id == telegram_chat_id)
    )
    result = await session.execute(query)
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # Filter out products with status "PICKED_UP"
    non_picked_up_products = [product for product in client.products if product.status.name == ProductStatus.CHINA]

    if not non_picked_up_products:
        return {"message": "No products found for this client"}

    # Prepare client and product data
    client_data = {
        "id": client.id,
        "name": client.name,
        "number": client.number,
        "city": client.city,
        "products": [
            {
                "id": product.id,
                "product_code": product.product_code,
                "date": product.date.isoformat() if product.date else None,  # Assuming date is a datetime object
                "status": product.status.name
            }
            for product in non_picked_up_products
        ]
    }

    return client_data

@router.get("/products/status/intransit/{telegram_chat_id}")
async def foo_telegram_main_test(
    telegram_chat_id: str,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    # Query the client by their ID with related products
    query = (
    select(Client)
        .options(
            joinedload(Client.products)          # жадная загрузка продуктов
            .joinedload(Product.status)          # жадная загрузка статуса у каждого продукта
        )
        .where(Client.telegram_chat_id == telegram_chat_id)
    )
    result = await session.execute(query)
    client = result.scalars().first()
    result = await session.execute(query)
    client = result.scalars().first()

    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # Filter out products with status "PICKED_UP"
    non_picked_up_products = [product for product in client.products if product.status.name == ProductStatus.TRANSIT]

    if not non_picked_up_products:
        return {"message": "No products found for this client"}

    # Prepare client and product data
    client_data = {
        "id": client.id,
        "name": client.name,
        "number": client.number,
        "city": client.city,
        "products": [
            {
                "id": product.id,
                "product_code": product.product_code,
                "date": product.date.isoformat() if product.date else None,  # Assuming date is a datetime object
                "status": product.status.name
            }
            for product in non_picked_up_products
        ]
    }

    return client_data

@router.get("/product/{product_code}")
async def get_product_on_track_code(
    product_code: str,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    query = select(Product).where(Product.product_code == product_code)
    query = (
    select(Product)
        .options(
            joinedload(Product.status)          # жадная загрузка продуктов
        )
        .where(Product.product_code == product_code)
    )
    result = await session.execute(query)
    product = result.scalars().first()

    if product is None:
            raise HTTPException(status_code=404, detail="Client not found")
    
    data = {
        "weight": product.weight if product.weight is not None else None,
        "product_code": product.product_code,
        "price": product.price,
        "status": product.status.name,
        "client_id": product.client_id,
        "id": product.id,
        "date": product.date
    }
    
    return data

@router.get("/get/clients/telegram_chat_ids")
async def get_client_telegram_chat_ids(
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
    ):
    query = select(Client)
    result = await session.execute(query)
    users = result.scalars().all()
    telegram_chat_ids = [user.telegram_chat_id for user in users if user.telegram_chat_id is not None]
    return telegram_chat_ids


@router.post("/update/branch")
async def udpate_cient_branch(
    telegram_chat_id: str,
    branch_id: int,
    session: AsyncSession = Depends(get_async_session),
    api_key: APIKey = Depends(get_api_key)
):
    # 1. Находим клиента по telegram_chat_id
    query = select(Client).where(Client.telegram_chat_id == telegram_chat_id)
    result = await session.execute(query)
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=404, detail="Клиент с таким telegram_chat_id не найден")
    
    # 2. Находим новый филиал по branch_id
    branch_query = select(Branch).where(Branch.id == branch_id)
    branch_result = await session.execute(branch_query)
    new_branch = branch_result.scalar_one_or_none()

    if not new_branch:
        raise HTTPException(status_code=404, detail="Филиал с таким ID не найден")

    # 3. Обновляем branch_id и пересчитываем code
    client.branch_id = branch_id
    client.code = f"{new_branch.code}{client.numeric_code}"  # Новый code = branch.code + numeric_code

    # 4. Сохраняем изменения в базе
    await session.commit()
    await session.refresh(client)  # Обновляем объект для возврата актуальных данных

    # 5. Возвращаем обновлённого клиента (опционально)
    return {
        "id": client.id,
        "name": client.name,
        "telegram_chat_id": client.telegram_chat_id,
        "branch_id": client.branch_id,
        "code": client.code
    }