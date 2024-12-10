from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.security.oauth2_auth import get_current_active_user
from app.db.models.user import User
from celeryApp.worker import get_time
from celeryApp.celery_app import celery_app

import logging
logger = logging.getLogger(__name__)


router = APIRouter()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/hello")
def hello(current_user: Annotated[User, Depends(get_current_active_user)]):
    return {"hello": "world"}


def validate_token(token: str):
    return token == "valid_token"


# @app.get("/items/")
# async def read_items(key: str = Depends(header_scheme)):
#     return {"key": key}

@router.get("/hello/{name}")
def hello_name():
    logger.info("hello_name")
    return {"hello": "name"}


@router.post("/get_time")
def _get_time(word: str):
    task = get_time.delay(word)
    return {"task_id": task.id}


@router.get("/get_time/{task_id}")
async def get_time_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.ready():
        return {"result": result.get()}
    else:
        return {"result": "not ready"}
