# Базовый образ Python 3.13 slim
FROM python:3.13-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml requirements.txt ./

# Устанавливаем зависимости через pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем остальной код проекта
COPY . .

# Указываем порт
EXPOSE 8000

# Запуск FastAPI (dev)
CMD ["uvicorn", "shorten.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
