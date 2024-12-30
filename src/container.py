import logging
from os.path import dirname
from pathlib import Path

from celery import Celery

from config import DatabaseSettings, TasksSettings
from src.v1.email.config import EmailSettings
from src.v1.jwt.config import JWTSettings, CookiesSettings

tasks_settings = TasksSettings()
app = Celery(
    main="tasks",
    backend=f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
    broker=f"pyamqp://{tasks_settings.RABBITMQ_HOST}:{tasks_settings.RABBITMQ_PORT}"
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(dirname(__file__))

database_settings = DatabaseSettings()
jwt_settings = JWTSettings()
cookies_settings = CookiesSettings()
email_settings = EmailSettings()
