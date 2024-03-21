from fastapi import APIRouter, Depends, status
from app.core.security.ecdsa_auth import ECDSAHeader
from app.schemas.auth_schemas import LoginInput, UserSession
from app.core.auth.auth import login, logout


import logging
logger = logging.getLogger(__name__)


router = APIRouter()

ecdsa_header_auth = ECDSAHeader(name="token")


@router.post("/login", status_code=status.HTTP_200_OK)
async def _authenticate(login_input: LoginInput):
    return await login(login_input)


@router.post("/logout", status_code=200)
async def _logout(user_session: UserSession = Depends(ecdsa_header_auth)):
    return await logout(user_session.address)


# @router.post("/add_user")
