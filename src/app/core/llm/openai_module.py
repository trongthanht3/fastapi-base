import os
from langchain.chains import ConversationChain
from app.core.config import settings
from app.utils.constants import LANGUAGES, PROMPTS
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


class OpenAIChatSession:
    def __init__(self, session_id: str):
        self.session_id = None
        self.language_code = None
        self.memory = ConversationBufferMemory()
        self.model = ChatOpenAI(model="gpt-3", convert_system_message_to_human=True)
        self.chat = ConversationChain(llm=self.model)

    def start_new_session(self, language_code: str):
        """
        Start a new chat session
        :param language_code:
        :return:
        """
        if language_code == LANGUAGES.ENGLISH.value:
            self.language_code = LANGUAGES.ENGLISH.value
            self.memory.chat_memory.add_user_message(PROMPTS.INSTRUCT_ENGLISH)
            self.memory.chat_memory.add_ai_message(PROMPTS.INSTRUCT_ENGLISH)
            self.chat.prompt = PROMPTS.ENGLISH_PROMPT
        elif language_code == LANGUAGES.JAPANESE.value:
            self.language_code = LANGUAGES.JAPANESE.value
            self.memory.chat_memory.add_user_message(PROMPTS.INSTRUCT_JAPANESE)
            self.memory.chat_memory.add_ai_message(PROMPTS.INSTRUCT_JAPANESE)
            self.chat.prompt = PROMPTS.JAPANESE_PROMPT

        self.chat.memory = self.memory

        return self

    def send_message(self, message: str):
        result = self.chat.run(message)
        return result

    def end_session(self):
        self.chat.end_session(self.session_id)
        self.session_id = None

    def load_message(self, messages):
        for mes_pair in messages:
            self.chat.memory.chat_memory.add_user_message(mes_pair[0])
            self.chat.memory.chat_memory.add_ai_message(mes_pair[1])

    def __del__(self):
        if self.session_id is not None:
            self.end_session()
