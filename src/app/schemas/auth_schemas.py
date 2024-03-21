from pydantic import BaseModel
from typing_extensions import Annotated, Doc  # type: ignore [attr-defined]


class HTTPBasicECDSAToken(BaseModel):
    """
    The HTTP Basic credendials given as the result of using `HTTPBasic` in a
    dependency.

    Read more about it in the
    [FastAPI docs for HTTP Basic Auth](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/).
    """

    token: Annotated[str, Doc(
        "The ECDSA signed signature and expire_at time.")] = "signature:expire_at"

# Request


class LoginInput(BaseModel):
    signature: Annotated[str, Doc("The ECDSA signed signature.")]
    expire_at: Annotated[str, Doc("The expire time.")] = "2022-12-31"


class LoginSuccess(BaseModel):
    token: str


class UserSession(BaseModel):
    user_id: int
    address: str
