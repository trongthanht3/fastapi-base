from celeryApp.celery_app import celery_app
import datetime
import redis
# client_sentry = Client(settings.SENTRY_DSN)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(acks_late=True)
def get_time(word: str) -> str:
    # redis_client.set(f"{word}/{datetime.datetime.now()}")
    return f"{word}/{datetime.datetime.now()}"