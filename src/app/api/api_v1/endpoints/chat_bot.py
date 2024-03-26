from app.core.security.ecdsa_auth import ECDSAHeader

from fastapi import APIRouter, HTTPException, status, Depends
from app.core.llm.google_gemini import GeminiChatSession
from app.core.expert.ethereum_expert import ExpertEthereum
from app.schemas.base_schemas import BaseInput, BaseSessionCreateInput, MessageSuccessResponse, \
    SessionCreateSuccessResponse, BaseResponse
from app.db.models.user_chat_session import UserChatSession
from datetime import datetime
from app.core.config import settings
from celeryApp.celery_app import celery_app
from celeryApp.worker import commit_to_db
from app.db.engine import sqlalchemy_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.auth_schemas import UserSession
from app.utils.extend_postgres_memory import ExtendPostgresChatMessageHistory

import logging

logger = logging.getLogger('uvicorn')
router = APIRouter()

session_maker = sessionmaker(bind=sqlalchemy_engine)
db_session = session_maker()

ecdsa_header_auth = ECDSAHeader(name="token")


@router.post("/start_new_session",
             response_model=SessionCreateSuccessResponse,
             status_code=status.HTTP_201_CREATED)
def _start_new_session(item: BaseSessionCreateInput,
                       user_session: UserSession = Depends(ecdsa_header_auth)) -> SessionCreateSuccessResponse:
    """
    **Start a new chat session.**

    *Start a new chat session with the specified language and model.*

    Parameters:
    - `item` (`BaseSessionCreateInput`): The input for the chat session, containing the language and model.
    - `user_session` (`UserSession`): The user session information obtained from the authentication header.

    Returns:
    - `SessionCreateSuccessResponse`: The response containing the session ID and the creation time.
    """
    create_time = datetime.today()
    # Sync DB
    user_chat_session_db = UserChatSession(user_id=user_session.user_id,
                                           create_at=create_time,
                                           language_code=item.language,
                                           model=item.model)
    commit_task = commit_to_db.delay(user_chat_session_db)
    user_chat_session_db = celery_app.AsyncResult(commit_task.id).get()
    user_session_db_id = user_chat_session_db.user_session_id
    logger.info(
        f"User session ID created: {user_session_db_id} with temp ID: {user_session.user_id}")

    return SessionCreateSuccessResponse(session_id=str(user_session_db_id),
                                        created_at=str(create_time.strftime("%Y-%m-%d %H:%M:%S")))


@router.post("/chat", status_code=status.HTTP_200_OK)
async def _chat(item: BaseInput,
                user_session: UserSession = Depends(ecdsa_header_auth)):
    """
    **Chat API**

    *Chat with AI model*

    Parameters:
    - `item` (`BaseInput`): The input for the chat session, containing the session ID and message.
    - `user_session` (`UserSession`): The user session information obtained from the authentication header.

    Returns:
    - `BaseResponse` or `StreamingResponse`: The response from the chat session. If the input item has the streaming flag set to True, a StreamingResponse is returned. Otherwise, a BaseResponse is returned.
    """
    # Load data from db
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=item.session_id).first()
    if (user_chat_session_db is None) or (user_chat_session_db.user_id != user_session.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session ID not found or not match user ID")

    chat_session = GeminiChatSession(item.session_id)
    if item.streaming:
        return await chat_session.send_message_stream_v2(str(item.message))

    system_response = await chat_session.send_message(str(item.message))
    logger.info(f"System response: {system_response}")

    return MessageSuccessResponse(version=settings.API_VERSION,
                                  created_at=str(datetime.today().strftime(
                                      "%Y-%m-%d %H:%M:%S")),
                                  data=BaseResponse(msg_type='ai',
                                                    session_id=item.session_id,
                                                    content=system_response['output']))


@router.post("/chat_eth_expert", status_code=status.HTTP_200_OK, response_model=MessageSuccessResponse)
async def _chat_eth_expert(item: BaseInput,
                           user_session: UserSession = Depends(ecdsa_header_auth)):
    """
    **Chat with an Ethereum expert.**

    *Ethereum expert plugin, answer any question about Ethereum.*

    Parameters:
    - `item` (`BaseInput`): The input for the chat session, containing the session ID and message.
    - `user_session` (`UserSession`): The user session information obtained from the authentication header.

    Returns:
    - `BaseResponse` or `StreamingResponse`: The response from the chat session. If the input item has the streaming flag set to True, a StreamingResponse is returned. Otherwise, a BaseResponse is returned.
    """
    # Load data from db
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=item.session_id).first()
    if (user_chat_session_db is None) or (user_chat_session_db.user_id != user_session.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session ID not found or not match user ID")

    # Load old messages to chat session by using user_msg_content and system_msg_content
    chat_session = ExpertEthereum(item.session_id)

    if item.streaming:
        return await chat_session.send_message_stream_v2(str(item.message))
    else:
        system_response = await chat_session.send_message(str(item.message))
        logger.info(f"System response: {system_response}")
        content_source = []
        if len(system_response['intermediate_steps']) > 0:
            for item_content in system_response['intermediate_steps']:
                for source_item in item_content[-1]:
                    content_source.append(source_item['metadata']['source'])

        return MessageSuccessResponse(version=settings.API_VERSION,
                                      created_at=str(datetime.today().strftime(
                                          "%Y-%m-%d %H:%M:%S")),
                                      data=BaseResponse(msg_type='ai',
                                                        session_id=item.session_id,
                                                        content=system_response['output'],
                                                        content_source=content_source))


@router.get("/history/{session_id}", status_code=200)
def _get_history(session_id,
                 user_session: UserSession = Depends(ecdsa_header_auth)):
    """
    **Get chat history**

    *Get chat history of a session*

    Parameters:
    - `session_id` (`str`): The session ID.
    - `user_session` (`UserSession`): The user session information obtained from the authentication header.

    Returns:
    - `List[MessageSuccessResponse]`: The list of chat history messages.
    """
    # Load data from db
    session_id = str(session_id)
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=session_id).first()
    if (user_chat_session_db is None) or (user_chat_session_db.user_id != user_session.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session ID not found")
    chat_history_session = ExtendPostgresChatMessageHistory(
        session_id=session_id, connection_string=settings.POSTGRES_DATABASE_URI.unicode_string())
    old_messages = chat_history_session.full_messages(detail=True)
    chat_history = []
    print(old_messages)
    for msg in old_messages:
        chat_history.append(MessageSuccessResponse(version=settings.API_VERSION,
                                                   created_at=msg['created_at'].strftime(
                                                       "%Y-%m-%d %H:%M:%S"),
                                                   data=BaseResponse(msg_type=msg['message']['type'],
                                                                     session_id=session_id,
                                                                     content=msg['message']['data']['content'],)))

    return chat_history
