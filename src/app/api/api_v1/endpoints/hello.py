from fastapi import APIRouter
from celeryApp.worker import get_time
from celeryApp.celery_app import celery_app

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/hello")
def hello():
    return {"hello": "world"}


@router.get("/hello/{name}")
def hello_name(name: str):
    logger.info("hello_name")
    return {"hello": name}


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
