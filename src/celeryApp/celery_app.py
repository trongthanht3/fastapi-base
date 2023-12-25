from celery import Celery
from kombu.serialization import registry
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.RABBITMQ_URI.unicode_string() + "//",
    backend=settings.REDIS_URI.unicode_string()
)
# registry.enable("pickle")  # celery accept pickle
# registry.enable("application/x-python-serialize")  # celery accept pickle
# registry.enable("application/json")  # celery accept json

# celery_app.conf.event_serializer = "pickle"
celery_app.conf.task_serializer = "pickle"
celery_app.conf.result_serializer = "pickle"
celery_app.conf.accept_content = ["pickle", "application/json", "application/x-python-serialize"]
celery_app.conf.task_routes = {"celeryApp.worker.test_celery": "main-queue"}
celery_app.conf.task_routes = {"celeryApp.worker.get_time": "main-queue"}
celery_app.conf.task_routes = {"celeryApp.worker.commit_to_db": "main-queue"}
celery_app.autodiscover_tasks()
