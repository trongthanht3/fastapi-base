import os

from app.core.config import settings
from app.core.llm.base_llm import BaseLLMSession
from langchain.chains import ConversationChain

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiChatSession(BaseLLMSession):
    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        self.chat = ConversationChain(llm=self.model)
