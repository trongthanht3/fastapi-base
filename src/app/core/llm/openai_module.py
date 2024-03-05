import os
from app.core.config import settings
from langchain_openai import ChatOpenAI
from app.core.llm.base_llm import BaseLLMSession
from langchain.chains import ConversationChain

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


class OpenAIChatSession(BaseLLMSession):
    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.model = ChatOpenAI(model="gpt-3.5-turbo-0125", convert_system_message_to_human=True)
        self.chat = ConversationChain(llm=self.model)
