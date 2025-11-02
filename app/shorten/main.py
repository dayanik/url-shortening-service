from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

from .settings import get_session, templates, engine, lifespan
from .utilities import get_short_url_entity, store_to_db, generate_short_string


class LongUrl(BaseModel):
    url: HttpUrl


app = FastAPI(lifespan=lifespan)

# Подключаем папку со статикой
app.mount("/static", StaticFiles(directory="static"), name="static")


# общий обработчик исключения валидации длинной ссылки
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors(), "body": exc.body})


# Получаем домашнюю страницу
@app.get('/shorten')
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


# Создание короткой ссылки
@app.post('/shorten')
async def create_short_url(item: LongUrl):
    # так как уникальность короткой ссылки проверяется базой данных,
    # будем создавать короткие ссылки до тех пор,
    # пока проверка на уникальность не пройдет
    short_string = generate_short_string()
    new_short_url = await store_to_db(short_string, str(item.url))
    while not new_short_url:
        short_string = generate_short_string()
        new_short_url = await store_to_db(short_string, str(item.url))

    context = new_short_url.to_dict()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=context)


# Получение оригинальной ссылки
@app.get('/shorten/{short_url}')
async def get_origin_url(short_url: str, request: Request):
    # if client is browser
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(request, name="retrieve.html")

    async with get_session() as session:
        short_url_entity = await get_short_url_entity(session, short_url)

        # инкерментирование счетчика запросов короткой ссылки
        short_url_entity.access_count += 1
    
        context = short_url_entity.to_dict()
        return JSONResponse(status_code=status.HTTP_200_OK, content=context)


# Изменение оригинальной ссылки
@app.put('/shorten/{short_url}')
async def update_origin_url(short_url: str, item: LongUrl):
    async with get_session() as session:
        short_url_entity = await get_short_url_entity(session, short_url)

        short_url_entity.url = str(item.url)
        
        context = short_url_entity.to_dict()
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=context)


# Удаление короткой ссылки
@app.delete('/shorten/{short_url}')
async def delete_short_url(short_url: str):
    async with get_session() as session:
        short_url_entity = await get_short_url_entity(session, short_url)
        
        await session.delete(short_url_entity)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Получение статисики по запросам короткой ссылки
@app.get('/shorten/{short_url}/stats')
async def get_stats(short_url: str):
    async with get_session() as session:
        short_url_entity = await get_short_url_entity(session, short_url)
        
        context = short_url_entity.to_dict(access_count=True)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=context)
