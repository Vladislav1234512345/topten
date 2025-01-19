FROM python:3.12-alpine

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

# Копирование исходного кода
COPY . .

# Создадим папки env_files/, certs/
RUN mkdir -p env_files certs

# Устанавливаем зависимости из base.txt
RUN pip install -r requirements/dev.txt --verbose

# Обновление pip
RUN pip install --upgrade pip

# Запуск main.py файла
CMD ["sh", "-c", "python3 src/main.py"]

