from pydantic import BaseModel

# Request
class BaseInput(BaseModel):
    session_id: str
    message: str
    language: str = "jp"


# Response
class BaseResponse(BaseModel):
    status: int
    session_id: str
    content: str


class SuccessResponse(BaseModel):
    version: str
    success: bool
    created_at: str
    data: BaseResponse

class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: str