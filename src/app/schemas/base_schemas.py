from pydantic import BaseModel
from typing_extensions import Annotated, Doc
from typing import List, Optional


# Request
class BaseInput(BaseModel):
    session_id: Annotated[str, Doc("User session ID")]
    message: str
    streaming: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "123456",
                    "message": "Hello, how are you?",
                    "streaming": False
                },
            ]
        }
    }


class BaseSessionCreateInput(BaseModel):
    language: str = "en"
    model: str = "gpt-3.5-turbo-0125"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "language": "en",
                    "model": "gpt-3.5-turbo-0125"
                },
            ]
        }
    }


# Response
class BaseResponse(BaseModel):
    msg_type: str
    session_id: str
    content: str
    content_source: Optional[List[str]] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "msg_type": "ai",
                    "session_id": "123456",
                    "content": "Hello, how are you?",
                    "content_source": ["gpt-3.5-turbo-0125"]
                },
            ]
        }
    }


class MessageSuccessResponse(BaseModel):
    version: str
    created_at: str
    data: BaseResponse

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version": "1.0",
                    "created_at": "2022-01-01 00:00:00",
                    "data": {
                        "msg_type": "ai",
                        "session_id": "123456",
                        "content": "Hello, how are you?",
                        "content_source": ["gpt-3.5-turbo-0125"]
                    }
                },
            ]
        }
    }


class SessionCreateSuccessResponse(BaseModel):
    session_id: str
    created_at: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "123456",
                    "created_at": "2022-01-01 00:00:00"
                },
            ]
        }
    }
