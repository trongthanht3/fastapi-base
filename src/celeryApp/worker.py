from celeryApp.celery_app import celery_app
import datetime

# client_sentry = Client(settings.SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(acks_late=True)
def get_time(word: str) -> str:
    return f"{word}/{datetime.datetime.now()}"