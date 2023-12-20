from celery import Celery
from app.core.config import settings

print("Connecting to RabbitMQ:", settings.RABBITMQ_URI.unicode_string())
celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URI.unicode_string() + "//",
    backend="redis://localhost:6379/0"
)
celery_app.conf.task_routes = {"celeryApp.worker.test_celery": "main-queue"}
celery_app.conf.task_routes = {"celeryApp.worker.get_time": "main-queue"}
celery_app.autodiscover_tasks()
