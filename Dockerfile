FROM python:3.12-alpine

# Установим системные зависимости
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    python3-dev \
    postgresql-dev \
    openssl-dev \
    gmp \
    gmp-dev

# Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установим Python-зависимости
WORKDIR /usr/src/app
# Создадим папки env_files/, certs/
RUN mkdir -p env_files certs

# Копирование исходного кода
COPY . .
# Создаем виртуальное окружение
RUN python -m venv venv

# Активируем виртуальное окружение и устанавливаем зависимости из requirements.txt
RUN . venv/bin/activate && pip install -r requirements.txt --verbose

# Обновление pip
RUN pip install --upgrade pip

# Указываем, что при запуске контейнера будет активироваться виртуальное окружение
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000"]

