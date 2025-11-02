import os

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


# Настраиваем шаблонизатор Jinja2
templates = Jinja2Templates(directory="templates")


# функция которая будет выполняться при старте и стопе приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


load_dotenv()

DB_DRIVER = os.getenv('DB_DRIVER')
DB_USER_NAME = os.getenv('DB_USER_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')

# сборка строки для подключения к бд
DATABASE_URL = URL.create(
    DB_DRIVER,
    username=DB_USER_NAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,    
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# фабрика создания сессий
async_session_local = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False)


@asynccontextmanager
async def get_session():
    async with async_session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
