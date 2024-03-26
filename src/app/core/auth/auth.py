from fastapi import HTTPException, status
from app.core.security.ecdsa_auth import validate_signature
from app.schemas.auth_schemas import LoginInput, LoginSuccess
from app.db.engine import sqlalchemy_engine
from app.db.models.user import User
from sqlalchemy.orm import sessionmaker
import datetime
import base64

import logging
logger = logging.getLogger(__name__)


session_maker = sessionmaker(bind=sqlalchemy_engine)
db_session = session_maker()


async def login(login_input: LoginInput):
    address, validate_res = validate_signature(
        login_input.signature, login_input.expire_at)
    if validate_res:
        format_string = "%Y-%m-%d"
        datetime_object = datetime.datetime.strptime(
            login_input.expire_at, format_string)
        db_session.query(User).filter(
            User.address == address).update({User.token_expire_at: datetime_object})
        db_session.commit()
        db_session.flush()
        return LoginSuccess(
            token=base64.b64encode(f"{login_input.signature}:{login_input.expire_at}".encode('ascii')))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Error from server!!!")


async def logout(address: str):
    try:
        db_session.query(User).filter(User.address == address).update(
            {User.token_expire_at: datetime.datetime.now()})
        db_session.commit()
        db_session.flush()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error from server!!!")
    return {"message": "Logout successfully"}
