from celery import Celery

from src.config import tasks_settings

app = Celery(
    main="tasks",
    backend=f"redis://{tasks_settings.REDIS_HOST}:{tasks_settings.REDIS_PORT}",
    broker=f"pyamqp://{tasks_settings.RABBITMQ_HOST}:{tasks_settings.RABBITMQ_PORT}"
)
app.autodiscover_tasks(['src.v1.email.tasks'])
