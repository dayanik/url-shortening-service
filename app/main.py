import string
import random


from fastapi import FastAPI, Request,Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from sqlalchemy.exc import IntegrityError

from .models import ShortUrl
from .settings import get_session, select


class Item(BaseModel):
    url: HttpUrl


fake_db = {}

app = FastAPI()

# Подключаем папку со статикой
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настраиваем шаблонизатор Jinja2
templates = Jinja2Templates(directory="app/templates")


# Получаем домашнюю страницу
@app.get('/shorten')
async def create_short_string(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse(request=request, name="index.html")


# Создание короткой ссылки
@app.post('/shorten')
async def create_short_string(request: Request, item: Item | None = None):
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


def is_short_url_unique(short_url: str):
    return short_url in fake_db


async def store_to_db(short_url: str, long_url: str):
    try:
        with get_session() as session:
            new_short_url = ShortUrl(url=long_url, short_code=short_url)
            session.add(new_short_url)
            session.flush()  # Чтобы получить ID до коммита
            # Отсоединяем объект от сессии, чтобы можно было использовать после закрытия
            session.expunge(new_short_url)
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
async def get_origin_url(short_url: str, request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(
            request=request, name="retrieve.html")
    try:
        with get_session() as session:
            short_url_entity = session.scalar(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            if short_url_entity is None:
                raise NotFoundError
            short_url_entity.access_count += 1
            session.add(short_url_entity)
            context = {
                'id': short_url_entity.id,
                'url': short_url_entity.url,
                'shortCode': short_url_entity.short_code,
                'createdAt': short_url_entity.created_at.isoformat() + 'Z',
                'updatedAt': short_url_entity.updated_at.isoformat() + 'Z',
            }
    except NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')

    return JSONResponse(status_code=status.HTTP_200_OK, content=context)


# Изменение оригинальной ссылки
@app.put('/shorten/{short_url}')
async def update_origin_url(short_url: str, item: Item):
    try:
        with get_session() as session:
            short_url_entity = session.scalar(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            if short_url_entity is None:
                raise NotFoundError
            short_url_entity.url = str(item.url)
            session.add(short_url_entity)
            context = {
                'id': short_url_entity.id,
                'url': short_url_entity.url,
                'shortCode': short_url_entity.short_code,
                'createdAt': short_url_entity.created_at.isoformat() + 'Z',
                'updatedAt': short_url_entity.updated_at.isoformat() + 'Z',
            }
    except NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')

    return JSONResponse(
        status_code=status.HTTP_200_OK, content=context)


class NotFoundError(Exception):
    pass


# Удаление короткой ссылки
@app.delete('/shorten/{short_url}')
async def delete_short_url(short_url: str):
    try:
        with get_session() as session:
            short_url_entity = session.scalar(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            if short_url_entity is None:
                raise NotFoundError
            session.delete(short_url_entity)
    except NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        print(type(err))
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')

    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content='')


@app.get('/shorten/{short_url}/stats')
async def get_stats(short_url: str):
    try:
        with get_session() as session:
            short_url_entity = session.scalar(
                select(ShortUrl).where(ShortUrl.short_code==short_url))
            if short_url_entity is None:
                raise NotFoundError
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
    except NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content='Short url not found')
    except Exception as err:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Connection error with database')
