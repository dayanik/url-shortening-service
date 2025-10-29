from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

# Подключаем папку со статикой
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настраиваем шаблонизатор Jinja2
templates = Jinja2Templates(directory="templates")


@app.get('/shorten', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
