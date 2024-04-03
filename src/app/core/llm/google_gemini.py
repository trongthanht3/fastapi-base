import os

from app.core.config import settings
from app.utils.constants import LANGUAGES
from app.core.llm.base_llm import BaseLLMSession


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiChatSession(BaseLLMSession):
    def __init__(self, session_id: str, language_code: str = LANGUAGES.ENGLISH.value):
        super().__init__(session_id=session_id, language_code=language_code)
        self.model = ChatGoogleGenerativeAI(
            model="gemini-pro", convert_system_message_to_human=True)
