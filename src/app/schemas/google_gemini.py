from pydantic import BaseModel
from .base_schemas import BaseInput
# Input
class GoogleGeminiInput(BaseInput):
    pass

class ListGoogleGeminiMessage(BaseModel):
    user_messages: list
    system_messages: list