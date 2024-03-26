import os
from app.core.config import settings
from langchain_openai import ChatOpenAI
from app.core.llm.base_llm import BaseLLMSession
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


class OpenAIChatSession(BaseLLMSession):
    def __init__(self, session_id: str, model_name="gpt-3.5-turbo-0125"):
        super().__init__(session_id, model_name)
        self.model = ChatOpenAI(
            model=model_name, convert_system_message_to_human=True)
