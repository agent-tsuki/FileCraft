from typing import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config.settings import settings

# Creating db url and db engine
DB_URL = URL.create(
    "postgresql+asyncpg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOSTNAME,
    port=settings.DB_PORT,
    database=settings.DB_DATABASE,
)
DB_ENGINE = create_async_engine(
    DB_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # prevent "connection closed" errors
)

# Creating db session and base to create table
DBSession = async_sessionmaker(bind=DB_ENGINE, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    create database session for fastapi dependency injection
    """
    async with DBSession() as session:
        yield session
