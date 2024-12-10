from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.core.security.ecdsa_auth import validate_signature
from app.db.services.user import UserServices
from app.schemas.auth_schemas import LoginInput, LoginSuccess, LoginInputOAuth2, RegisterInput, Token
from app.db.engine import sqlalchemy_engine
from app.db.models.user import User
from sqlalchemy.orm import sessionmaker
import datetime
import base64


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security.oauth2_auth import authenticate_user, timedelta, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

import logging
logger = logging.getLogger(__name__)


session_maker = sessionmaker(bind=sqlalchemy_engine)
db_session = session_maker()
userServices = UserServices()


async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def login_ECDSA(login_input: LoginInput):
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


async def register(register_input: RegisterInput):
    try:
        userServices.add_user(register_input=register_input)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": register_input.username}, expires_delta=access_token_expires
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error from server!!!")
    return Token(access_token=access_token, token_type="bearer")
