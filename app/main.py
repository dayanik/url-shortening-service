import string
import random

from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from sqlalchemy.exc import IntegrityError

from .models import ShortUrl
from .settings import get_session


class Item(BaseModel):
    url: HttpUrl


fake_db = {}

app = FastAPI()

# Подключаем папку со статикой
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настраиваем шаблонизатор Jinja2
templates = Jinja2Templates(directory="app/templates")


@app.get('/shorten', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


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

            return new_short_url
    except IntegrityError:
        return False
    except Exception as err:
        raise ConnectionError


@app.post('/shorten')
async def create_short_string(item: Item):
    # сохраняем если только уникальный short_string
    short_string = generate_short_string()
    new_short_url = await store_to_db(short_string, str(item.url))
    while not new_short_url:
        short_string = generate_short_string()
        new_short_url = await store_to_db(short_string, str(item.url))

    context = {
        'id': new_short_url.id,
        'url': new_short_url.url,
        'shortCode': new_short_url.short_code,
        'createdAt': new_short_url.created_at.isoformat() + 'Z',
        'updatedAt': new_short_url.updated_at.isoformat() + 'Z',
    }

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=context)


@app.get('/shorten/{short_url}')
async def get_origin_url(short_url: str):
    try:
        with get_session() as session:
            short_url_entity = session.get(ShortUrl, short_code=short_url)
            print(short_url_entity)
    except Exception as err:
        raise ConnectionError
    

    return JSONResponse(status_code=status.HTTP_200_OK, content={})
