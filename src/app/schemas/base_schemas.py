from pydantic import BaseModel
from typing import List, Optional


# Request
class BaseInput(BaseModel):
    session_id: str
    message: str
    language: str = "jp"


class BaseSessionCreateInput(BaseModel):
    language: str = "jp"


# Response
class BaseResponse(BaseModel):
    status: int
    session_id: str
    content: str
    content_source: Optional[List[str]] = []


class MessageSuccessResponse(BaseModel):
    version: str
    success: bool
    created_at: str
    data: BaseResponse


class SessionCreateSuccessResponse(BaseModel):
    session_id: str
    created_at: str
