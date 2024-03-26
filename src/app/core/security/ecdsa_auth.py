from fastapi import HTTPException, status
from fastapi.security import APIKeyHeader
from web3 import Web3
from eth_account.messages import encode_defunct
from app.db.models.user import User
# using time module
from typing import Optional
from starlette.requests import Request
import datetime
import base64
from app.db.engine import sqlalchemy_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.auth_schemas import UserSession

import logging
logger = logging.getLogger('uvicorn')

session_maker = sessionmaker(bind=sqlalchemy_engine, autoflush=True)
db_session = session_maker()
w3 = Web3(Web3.HTTPProvider('https://polygon-mumbai-pokt.nodies.app'))
# Inherit from APIKeyHeader and implement the __call__ method
# to validate the API key by using w3.eth.account.recover_message


class ECDSAHeader(APIKeyHeader):
    async def __call__(self, request: Request) -> Optional[UserSession]:
        api_key = request.headers.get(self.model.name)
        if not api_key:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        try:
            api_key = base64.b64decode(api_key).decode("ascii")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Wrong format"
            )
        logger.info(f"api_key: {api_key}")
        address_rec = ""
        signature = ""
        expire_at = ""
        try:
            signature, expire_at = api_key.split(":")
            address_rec = w3.eth.account.recover_message(encode_defunct(
                text=expire_at), signature=signature)
        except Exception as e:
            logger.error("Invalid signature")
            logger.error(f"Error: {e}")
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
                )
            else:
                return None
        logger.info(f"address_rec: {address_rec}")

        address_session = db_session.query(User).filter(
            User.address == address_rec).first()
        db_session.reset()
        if (address_session.is_banned) or (address_session is None):
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Banned address"
                )
            else:
                return None
        try:
            format_string = "%Y-%m-%d"
            token_session_time = datetime.datetime.strptime(
                expire_at, format_string)
        except Exception as e:
            logger.error(f"Error: {e.__str__()}")
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
                )
        logger.info(
            f"server time: {address_session.token_expire_at}, token time: {token_session_time}")
        if address_session.token_expire_at != token_session_time:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
                )
            else:
                return None

        # Recover the message and return the address
        return UserSession(user_id=address_session.user_id,
                           address=address_session.address)


def validate_signature(signature, expire_at):
    address_rec = w3.eth.account.recover_message(encode_defunct(
        text=str(expire_at)), signature=signature)
    logger.info(f"address_rec: {address_rec}")

    address_session = db_session.query(User).filter(
        User.address == address_rec).first()

    if (address_session is None) or (address_session.is_banned):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )
    try:
        format_string = "%Y-%m-%d"
        new_session_time = datetime.datetime.strptime(
            expire_at, format_string)
        current_time = datetime.datetime.now()
        logger.info(
            f"server time: {address_session.token_expire_at}, token time: {new_session_time}, current time: {current_time}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid expire date"
        )

    if current_time > new_session_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid expire date"
        )
    return address_rec, True
