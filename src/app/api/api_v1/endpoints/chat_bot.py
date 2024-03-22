from app.core.security.ecdsa_auth import ECDSAHeader

from fastapi import APIRouter, HTTPException, status, Depends
from app.core.llm.google_gemini import GeminiChatSession
from app.core.expert.ethereum_expert import ExpertEthereum
from app.schemas.base_schemas import BaseInput, BaseSessionCreateInput, MessageSuccessResponse, \
    SessionCreateSuccessResponse, BaseResponse
from app.db.models.session_msg import SessionMsg
from app.db.models.user_chat_session import UserChatSession
from datetime import datetime
from app.core.config import settings
from celeryApp.celery_app import celery_app
from celeryApp.worker import commit_to_db
from app.db.engine import sqlalchemy_engine
from sqlalchemy.orm import sessionmaker
from fastapi.responses import StreamingResponse
from app.schemas.auth_schemas import UserSession

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
    # Write comment in markdown
    """
    Start a new chat session
    :param item:
    :return:
    """
    create_time = datetime.today()
    # Sync DB
    user_chat_session_db = UserChatSession(user_id=user_session.user_id,
                                           create_at=create_time,
                                           language_code=item.language)
    commit_task = commit_to_db.delay(user_chat_session_db)
    user_chat_session_db = celery_app.AsyncResult(commit_task.id).get()
    user_session_db_id = user_chat_session_db.user_session_id
    logger.info(
        f"User session ID created: {user_session_db_id} with temp ID: {user_session.user_id}")

    return SessionCreateSuccessResponse(session_id=str(user_session_db_id),
                                        created_at=str(create_time.strftime("%Y-%m-%d %H:%M:%S")))


@router.post("/send_message", status_code=status.HTTP_200_OK, response_model=MessageSuccessResponse)
def _send_message(item: BaseInput,
                  user_session: UserSession = Depends(ecdsa_header_auth)) -> MessageSuccessResponse:
    """
    Send message to chat
    :param item:
    :return:
    """
    # Load data from db
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=item.session_id).first()
    if user_chat_session_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session ID not found")
    if user_chat_session_db.user_id != user_session.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Session ID not match")
    old_messages = db_session.query(SessionMsg).filter_by(
        user_session_id=item.session_id).all()
    # Sort old messages by create_at
    old_messages.sort(key=lambda x: x.create_at)

    # Load old messages to chat session by using user_msg_content and system_msg_content
    chat_session = GeminiChatSession(item.session_id)
    chat_session.start_new_session(
        language_code=user_chat_session_db.language_code)
    chat_session.load_message(
        [(msg.user_msg_content, msg.system_msg_content) for msg in old_messages])

    # Append new message to DB
    new_message = SessionMsg(user_session_id=item.session_id,
                             user_msg_content=item.message,
                             system_msg_content="",
                             create_at=datetime.today())
    system_response = chat_session.send_message(str(item.message))
    new_message.system_msg_content = system_response
    commit_task = commit_to_db.delay(new_message)
    new_message = celery_app.AsyncResult(commit_task.id).get()
    logger.info(f"New message created: {new_message}")

    return MessageSuccessResponse(version=settings.API_VERSION,
                                  success=True,
                                  created_at=str(datetime.today().strftime(
                                      "%Y-%m-%d %H:%M:%S")),
                                  data=BaseResponse(status=200,
                                                    session_id=item.session_id,
                                                    content=system_response))


@router.post("/send_message_eth_expert", status_code=status.HTTP_200_OK, response_model=MessageSuccessResponse)
async def _send_message_eth_expert(item: BaseInput,
                                   user_session: UserSession = Depends(ecdsa_header_auth)):
    """
    Send message to chat
    :param item:
    :return:
    """
    # Load data from db
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=item.session_id).first()
    if user_chat_session_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session ID not found")
    if user_chat_session_db.user_id != user_session.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Session ID not match")
    old_messages = db_session.query(SessionMsg).filter_by(
        user_session_id=item.session_id).all()
    # Sort old messages by create_at
    old_messages.sort(key=lambda x: x.create_at)

    # Load old messages to chat session by using user_msg_content and system_msg_content
    chat_session = ExpertEthereum(item.session_id)
    chat_session.start_new_session(
        language_code=user_chat_session_db.language_code)
    chat_session.load_message(
        [(msg.user_msg_content, msg.system_msg_content) for msg in old_messages])

    # Append new message to DB
    new_message = SessionMsg(user_session_id=item.session_id,
                             user_msg_content=item.message,
                             system_msg_content="",
                             create_at=datetime.today())
    if item.streaming:
        return StreamingResponse(content=chat_session.send_message_stream(str(item.message)), status_code=status.HTTP_200_OK, media_type='text/event-stream')
    else:
        system_response = await chat_session.send_message(str(item.message))
        logger.info(f"System response: {system_response}")
        content_source = []
        if len(system_response['intermediate_steps']) > 0:
            for item_content in system_response['intermediate_steps']:
                for source_item in item_content[-1]:
                    content_source.append(source_item['metadata']['source'])
        new_message.system_msg_content = system_response['output']
        commit_task = commit_to_db.delay(new_message)
        new_message = celery_app.AsyncResult(commit_task.id).get()
        logger.info(f"New message created: {new_message}")

        return MessageSuccessResponse(version=settings.API_VERSION,
                                      success=True,
                                      created_at=str(datetime.today().strftime(
                                          "%Y-%m-%d %H:%M:%S")),
                                      data=BaseResponse(status=200,
                                                        session_id=item.session_id,
                                                        content=system_response['output'],
                                                        content_source=content_source))


@router.post("/beta_format", status_code=status.HTTP_200_OK, response_model=MessageSuccessResponse)
async def _beta_format(item: BaseInput,
                       user_session: UserSession = Depends(ecdsa_header_auth)):
    """
    Send message to chat
    :param item:
    :return:
    """
    # Load data from db
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=item.session_id).first()
    if user_chat_session_db is None:
        raise HTTPException(status_code=404, detail="Session ID not found")
    old_messages = db_session.query(SessionMsg).filter_by(
        user_session_id=item.session_id).all()
    # Sort old messages by create_at
    old_messages.sort(key=lambda x: x.create_at)

    # Load old messages to chat session by using user_msg_content and system_msg_content
    chat_session = ExpertEthereum(item.session_id)
    chat_session.start_new_session(
        language_code=user_chat_session_db.language_code)
    chat_session.load_message(
        [(msg.user_msg_content, msg.system_msg_content) for msg in old_messages])

    # Append new message to DB
    new_message = SessionMsg(user_session_id=item.session_id,
                             user_msg_content=item.message,
                             system_msg_content="",
                             create_at=datetime.today())
    if item.streaming:
        # base_chunk = CompletionStreamResponse(
        #     id=str(uuid.uuid4()),
        #     created=time.time(),
        #     model='gpt-3.5-turbo-0125',
        #     choices=[]
        # )
        # return StreamingResponse((response for response in chat_session.stream_completion(chat_session.stream_handle(item.message), base_chunk)),
        #                             media_type="text/event-stream")
        return await chat_session.send_message_stream_v2(str(item.message))
    else:
        system_response = await chat_session.send_message(str(item.message))
        logger.info(f"System response: {system_response}")
        content_source = []
        if len(system_response['intermediate_steps']) > 0:
            for item_content in system_response['intermediate_steps']:
                for source_item in item_content[-1]:
                    content_source.append(source_item['metadata']['source'])
        new_message.system_msg_content = system_response['output']
        commit_task = commit_to_db.delay(new_message)
        new_message = celery_app.AsyncResult(commit_task.id).get()
        logger.info(f"New message created: {new_message}")

        return MessageSuccessResponse(version=settings.API_VERSION,
                                      success=True,
                                      created_at=str(datetime.today().strftime(
                                          "%Y-%m-%d %H:%M:%S")),
                                      data=BaseResponse(status=200,
                                                        session_id=item.session_id,
                                                        content=system_response['output'],
                                                        content_source=content_source))


@router.get("/chat_history", status_code=200)
def _get_chat_history(session_id: str):
    """
    Get chat history
    :param session_id:
    :return:
    """
    # Load data from db
    user_chat_session_db = db_session.query(UserChatSession).filter_by(
        user_session_id=session_id).first()

    if user_chat_session_db is None:
        raise HTTPException(status_code=404, detail="Session ID not found")
    old_messages = db_session.query(SessionMsg).filter_by(
        user_session_id=session_id).all()
    # Sort old messages by create_at
    old_messages.sort(key=lambda x: x.create_at)

    chat_history = []
    for pair_msg in old_messages:
        chat_history.append(MessageSuccessResponse(version=settings.API_VERSION,
                                                   success=True,
                                                   created_at=str(datetime.today().strftime(
                                                       "%Y-%m-%d %H:%M:%S")),
                                                   data=BaseResponse(status=200,
                                                                     session_id=session_id,
                                                                     content=pair_msg.user_msg_content)))
        chat_history.append(MessageSuccessResponse(version=settings.API_VERSION,
                                                   success=True,
                                                   created_at=str(datetime.today().strftime(
                                                       "%Y-%m-%d %H:%M:%S")),
                                                   data=BaseResponse(status=200,
                                                                     session_id=session_id,
                                                                     content=pair_msg.system_msg_content)))

    return chat_history
