import pickle

from celeryApp.celery_app import celery_app
import datetime
import redis
from sqlalchemy.orm import sessionmaker
from app.db.engine import sqlalchemy_engine
from app.db.models.user_session import UserSession
# client_sentry = Client(settings.SENTRY_DSN)

redis_client = redis.Redis(host='localhost', port=6379, db=0)
session_maker = sessionmaker(bind=sqlalchemy_engine)
session = session_maker()

@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(acks_late=True)
def get_time(word: str) -> str:
    # redis_client.set(f"{word}/{datetime.datetime.now()}")
    return f"{word}/{datetime.datetime.now()}"

@celery_app.task(acks_late=True)
def commit_to_db(sql_obj):
    try:
        session.add(sql_obj)
        session.commit()
        session.flush()
        session.refresh(sql_obj)
        return sql_obj
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()