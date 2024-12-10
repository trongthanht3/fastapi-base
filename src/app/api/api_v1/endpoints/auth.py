from fastapi import APIRouter, Depends, status
from app.core.security.ecdsa_auth import ECDSAHeader
from app.schemas.auth_schemas import LoginInput, RegisterInput, Token, UserSession
from app.core.auth.auth import login, logout, register
from app.db.services.user import UserServices
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated


import logging
logger = logging.getLogger(__name__)


router = APIRouter()

ecdsa_header_auth = ECDSAHeader(name="token")


@router.post("/token", status_code=status.HTTP_200_OK)
async def _authenticate(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return await login(form_data)


@router.post("/login_ecdsa", status_code=status.HTTP_200_OK)
async def _authenticate_ecdsa(login_input: LoginInput):
    return await login(login_input)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def _logout(user_session: UserSession = Depends(ecdsa_header_auth)):
    return await logout(user_session.address)


@router.post("/register", status_code=status.HTTP_200_OK)
async def _logout(register_input: RegisterInput):
    return await register(register_input)
