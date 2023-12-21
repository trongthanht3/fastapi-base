from typing import Annotated, Any, List
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException
from app.core.llm.google_gemini import GeminiChatSession
from app.schemas.google_gemini import GoogleGeminiInput
from app.schemas.base_schemas import BaseInput, SuccessResponse, SessionCreateResponse
from app.db.models.session_msg import SessionMsg
from app.db.models.user_session import UserSession
from datetime import datetime
from app.utils.constants import LANGUAGES
from fastapi.encoders import jsonable_encoder
from app.core.config import settings
from celeryApp.worker import get_time
from celery.result import AsyncResult
from celeryApp.celery_app import celery_app
from celeryApp.worker import commit_to_db

import logging
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start_new_session", status_code=200)
def _start_new_session(item: GoogleGeminiInput):
    """
    Start a new chat session
    :param item:
    :return: SessionCreateResponse object with session_id and create_at fields
    """
    temporary_user_session_id = str(uuid.uuid4())
    create_time = datetime.today().strftime("%d-%b-%Y-%H:%M:%S")
    # Sync DB
    user_session_db = UserSession(user_id=temporary_user_session_id,
                                  transcribe_id=item.session_id,
                                  create_at=create_time)

    commit_task = commit_to_db.delay(user_session_db)
    # user_session_db_id = celery_app.AsyncResult(commit_task.id).get()
    # # user_session_db_id = user_session_db_id.user_session_id
    # print(user_session_db_id)
    # # Create chat session
    # session = GeminiChatSession(str(user_session_db_id))
    # session.start_new_session(str(user_session_db_id))
    #
    # return SessionCreateResponse(
    #     session_id=str(user_session_db_id),
    #     create_at=create_time,
    # )
    return True



