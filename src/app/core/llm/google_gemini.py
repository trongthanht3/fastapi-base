import getpass
import os
from langchain.chains import ConversationChain
from app.core.config import settings
from app.utils.constants import LANGUAGES, PROMPTS
from langchain.memory import ConversationBufferMemory

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiChatSession:
    def __init__(self, session_id: str):
        self.session_id = None
        self.language_code = None
        self.memory = ConversationBufferMemory()
        self.model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        self.chat = ConversationChain(llm=self.model)

    def start_new_session(self, language_code: str):
        """
        Start a new chat session
        :param language_code:
        :return:
        """
        if language_code == LANGUAGES.ENGLISH.value:
            self.language_code = LANGUAGES.ENGLISH
            self.memory.add_user_message(PROMPTS.INSTRUCT_ENGLISH.value)
            self.memory.add_system_message(PROMPTS.INSTRUCT_ENGLISH.value)
        elif language_code == LANGUAGES.JAPANESE.value:
            self.language_code = LANGUAGES.JAPANESE
            self.memory.add_user_message(PROMPTS.INSTRUCT_JAPANESE.value)
            self.memory.add_system_message(PROMPTS.INSTRUCT_JAPANESE.value)

        return self

    def send_message(self, message: str):
        result = self.chat.run(message)
        return result

    def end_session(self):
        self.chat.end_session(self.session_id)
        self.session_id = None

    def __del__(self):
        if self.session_id is not None:
            self.end_session()
