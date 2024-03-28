import binascii
from typing import Optional
from base64 import b64decode
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBasic
from fastapi.security.utils import get_authorization_scheme_param


from app.schemas.auth_schemas import HTTPBasicECDSAToken


class HTTPBasicECDSA(HTTPBasic):
    async def __call__(  # type: ignore
        self, request: Request
    ) -> Optional[HTTPBasicECDSAToken]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if self.realm:
            unauthorized_headers = {
                "WWW-Authenticate": f'Basic realm="{self.realm}"'}
        else:
            unauthorized_headers = {"WWW-Authenticate": "Basic"}
        if not authorization or scheme.lower() != "basic":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers=unauthorized_headers,
                )
            else:
                return None
        invalid_user_credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers=unauthorized_headers,
        )
        try:
            data = b64decode(param).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise invalid_user_credentials_exc  # noqa: B904
        signature, separator, expire_at = data.partition(":")
        if not separator:
            raise invalid_user_credentials_exc
        return HTTPBasicECDSAToken(signature=signature, expire_at=int(expire_at))
