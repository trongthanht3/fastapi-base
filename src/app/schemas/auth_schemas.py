from pydantic import BaseModel
from typing_extensions import Annotated, Doc  # type: ignore [attr-defined]


class User(BaseModel):
    username: str
    address: str = "0x000000000000000000000000000000000000000000"

# Login


class LoginInput(BaseModel):
    signature: Annotated[str, Doc("The ECDSA signed signature.")]
    expire_at: Annotated[str, Doc("The expire time.")] = "2022-12-31"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "signature": "0x123456",
                    "expire_at": "2022-12-31"
                },
            ]
        }
    }


class LoginSuccess(BaseModel):
    token: str


class UserSession(BaseModel):
    user_id: int
    username: str
    address: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 123456,
                    "username": "john_doe_1412",
                    "address": "0x123456"
                },
            ]
        }
    }


class UserSessionECDSA(BaseModel):
    user_id: int
    address: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 123456,
                    "address": "0x123456"
                },
            ]
        }
    }


# OAuth2 part

class LoginInputOAuth2(BaseModel):
    username: Annotated[str, Doc("Username")] = "johnDoe1412"
    password: Annotated[str, Doc("Password")] = "iL0v3y0u"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "abcdef",
                    "token_type": "HS256"
                },
            ]
        }
    }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# Register
class RegisterInput(User):
    password: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe_1412",
                    "password": "iL0v3y0u",
                    "address": "0x000000000000000000000000000000000000000000"
                },
            ]
        }
    }


class RegiterSuccess(Token):
    pass
