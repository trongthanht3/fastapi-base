import json
from typing import Iterable
from app.schemas.stream_schemas import CompletionChoice, CompletionStreamResponse
from app.utils.constants import LANGUAGES, PROMPTS
from langchain.memory import ConversationBufferMemory


# if "GOOGLE_API_KEY" not in os.environ:
#     os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

# This class must be implemented in the derived class
class BaseLLMSession:
    def __init__(self, session_id: str):
        self.session_id = None
        self.language_code = None
        self.memory = ConversationBufferMemory()
        self.model = None
        self.chat = None

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

    def stream_completion(self, output: Iterable, base_response: CompletionStreamResponse):
        """
        Streams a GPT4All output to the client.

        Args:
            output: The output of GPT4All.generate(), which is an iterable of tokens.
            base_response: The base response object, which is cloned and modified for each token.

        Returns:
            A Generator of CompletionStreamResponse objects, which are serialized to JSON Event Stream format.
        """
        for token in output:
            chunk = base_response.copy()
            chunk.choices = [dict(CompletionChoice(
                text=token,
                index=0,
                logprobs=-1,
                finish_reason=''
            ))]
            yield f"data: {json.dumps(dict(chunk))}\n\n"

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
