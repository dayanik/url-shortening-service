import string
import random


from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from sqlalchemy.exc import IntegrityError

from .models import ShortUrl
from .settings import get_session, select


class LongUrl(BaseModel):
    """Long url validation model"""
    url: HttpUrl


app = FastAPI()

# Подключаем папку со статикой
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настраиваем шаблонизатор Jinja2
templates = Jinja2Templates(directory="app/templates")


# Получаем домашнюю страницу
@app.get('/shorten')
async def create_short_string(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


# Создание короткой ссылки
@app.post('/shorten')
async def create_short_string(request: Request, item: LongUrl | None = None):
    # сохраняем если только уникальный short_string
    short_string = generate_short_string()
    context = await store_to_db(short_string, str(item.url))
    while not context:
        short_string = generate_short_string()
        context = await store_to_db(short_string, str(item.url))

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=context)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": exc.body})


def generate_short_string(length: int=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


async def store_to_db(short_url: str, long_url: str):
    try:
        async with get_session() as session:
            new_short_url = ShortUrl(url=long_url, short_code=short_url)
            session.add(new_short_url)
            await session.flush()  # Чтобы получить ID до коммита
            # Отсоединяем объект от сессии, чтобы можно было использовать после закрытия
            await session.refresh(new_short_url)
            context = {
                'id': new_short_url.id,
                'url': new_short_url.url,
                'shortCode': new_short_url.short_code,
                'createdAt': new_short_url.created_at.isoformat() + 'Z',
                'updatedAt': new_short_url.updated_at.isoformat() + 'Z',
            }
            return context
    except IntegrityError:
        return False
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')


# Получение оригинальной ссылки
@app.get('/shorten/{short_url}')
async def get_origin_url(
    short_url: str,
    request: Request):
    
    # if client is browser
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(
            request=request, name="retrieve.html")
    try:
        async with get_session() as session:
            result = await session.execute(
            select(ShortUrl).where(ShortUrl.short_code==short_url))
            short_url_entity = result.scalar_one_or_none()
            if short_url_entity is None:
                raise HTTPException(status_code=404, detail="short url not found")

            # инкерментирование счетчика запросов короткой ссылки
            short_url_entity.access_count += 1
        
            context = {
                'id': short_url_entity.id,
                'url': short_url_entity.url,
                'shortCode': short_url_entity.short_code,
                'createdAt': short_url_entity.created_at.isoformat() + 'Z',
                'updatedAt': short_url_entity.updated_at.isoformat() + 'Z',
            }
            return JSONResponse(status_code=status.HTTP_200_OK, content=context)
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')


# Изменение оригинальной ссылки
@app.put('/shorten/{short_url}')
async def update_origin_url(short_url: str, item: LongUrl):
    try:
        async with get_session() as session:
            result = await session.execute(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            short_url_entity = result.scalar_one_or_none()
            if short_url_entity is None:
                raise HTTPException(status_code=404, detail="short url not found")
            short_url_entity.url = str(item.url)
            context = {
                'id': short_url_entity.id,
                'url': short_url_entity.url,
                'shortCode': short_url_entity.short_code,
                'createdAt': short_url_entity.created_at.isoformat() + 'Z',
                'updatedAt': short_url_entity.updated_at.isoformat() + 'Z',
            }
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=context)


# Удаление короткой ссылки
@app.delete('/shorten/{short_url}')
async def delete_short_url(short_url: str):
    try:
        async with get_session() as session:
            result = await session.execute(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            short_url_entity = result.scalar_one_or_none()
            if short_url_entity is None:
                raise HTTPException(status_code=404, detail="short url not found")
            await session.delete(short_url_entity)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')


@app.get('/shorten/{short_url}/stats')
async def get_stats(short_url: str):
    try:
        async with get_session() as session:
            result = await session.execute(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            short_url_entity = result.scalar_one_or_none()
            if short_url_entity is None:
                raise HTTPException(status_code=404, detail="short url not found")
            context = {
                'id': short_url_entity.id,
                'url': short_url_entity.url,
                'shortCode': short_url_entity.short_code,
                'createdAt': short_url_entity.created_at.isoformat() + 'Z',
                'updatedAt': short_url_entity.updated_at.isoformat() + 'Z',
                'accessCount': short_url_entity.access_count
            }
            return JSONResponse(
                status_code=status.HTTP_200_OK, content=context)
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')
