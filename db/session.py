from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import settings

#############################
# блок взаимодействия с бд
#############################

engine = create_async_engine(
    settings.REAL_DATABASE_URL, 
    future=True, 
    echo=True,
    execution_options={"isolation_level": "AUTOCOMMIT"},
    )

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncGenerator: # type: ignore
    # создаем объект ассинхронной сессии
    try:
        session: AsyncSession = async_session()
        yield session # сохранение контекста
    finally:
        await session.close()