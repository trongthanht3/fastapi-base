from pydantic import BaseModel
from typing_extensions import Annotated, Doc  # type: ignore [attr-defined]


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
