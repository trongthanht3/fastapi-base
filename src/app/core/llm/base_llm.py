import json
from typing import Iterable
from app.schemas.stream_schemas import CompletionChoice, CompletionStreamResponse
from app.utils.constants import LANGUAGES, PROMPTS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai import ChatOpenAI
from app.core.config import settings
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
import uuid
import time
from app.utils.extend_postgres_memory import ExtendPostgresChatMessageHistory
from fastapi.responses import StreamingResponse
import logging
logger = logging.getLogger('uvicorn')


class BaseLLMSession:
    def __init__(self, session_id: str, model_name: str = 'gpt-3.5-turbo-0125', language_code: str = LANGUAGES.ENGLISH.value):
        self.session_id = None
        self.language_code = None

        self.model = ChatOpenAI(
            model=model_name, streaming=True, temperature=0)
        self.prompt = self.get_prompt(language_code)
        self.memory = ExtendPostgresChatMessageHistory(
            connection_string=settings.POSTGRES_DATABASE_URI.unicode_string(),
            session_id=session_id,
            k=5
        )
        self.chain = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | self.prompt
            | self.model
            | OpenAIToolsAgentOutputParser()
        )
        self.agent_executor = AgentExecutor(
            agent=self.chain, tools=[], verbose=True)

        self.runable = RunnableWithMessageHistory(
            self.agent_executor,
            get_session_history=self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

    def get_prompt(self, language_code: str):
        """
        Start a new chat session
        :param language_code:
        :return:
        """
        if language_code == LANGUAGES.ENGLISH.value:
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        PROMPTS.INSTRUCT_ENGLISH,
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}"),
                ]
            )
            self.language_code = LANGUAGES.ENGLISH.value
        elif language_code == LANGUAGES.JAPANESE.value:
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        PROMPTS.INSTRUCT_JAPANESE,
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}"),
                ]
            )
            self.language_code = LANGUAGES.JAPANESE.value

        return self.prompt

    async def send_message(self, message: str):
        return await self.runable.ainvoke(
            {"input": message},
            config={"configurable": {"session_id": self.session_id}}
        )

    def end_session(self):
        self.chat.end_session(self.session_id)
        self.session_id = None

    def get_session_full_history(self):
        return self.memory.full_messages()

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        # logger.info(
        #     f"WINDOWS LENGTH: {len(self.windowsMem.buffer_as_messages)}")
        logger.info(
            f"POSGRES LENGTH: {len(self.memory.messages)}")
        return self.memory

    async def send_message_stream(self, message: str):
        async for event in self.runable.astream_events(
            {"input": message},
            config={"configurable": {"session_id": self.session_id}},
            version="v1",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # Empty content in the context of OpenAI means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content
                    yield content

    async def send_message_stream_v2(self, message: str):
        base_chunk = CompletionStreamResponse(
            id=str(uuid.uuid4()),
            created=int(time.time()),
            model=self.model.model_name,
            choices=[]
        )
        return StreamingResponse((response async for response in self.stream_completion(self.stream_handle(message), base_chunk)),
                                 media_type="text/event-stream")

    async def stream_handle(self, message: str):
        async for event in self.runable.astream_events(
            {"input": message},
            config={"configurable": {"session_id": self.session_id}},
            version="v1",
        ):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    # Empty content in the context of OpenAI means
                    # that the model is asking for a tool to be invoked.
                    # So we only print non-empty content
                    yield content

    async def stream_completion(self, output: Iterable, base_response: CompletionStreamResponse):
        """
        Streams a GPT4All output to the client.

        Args:
            output: The output of GPT4All.generate(), which is an iterable of tokens.
            base_response: The base response object, which is cloned and modified for each token.

        Returns:
            A Generator of CompletionStreamResponse objects, which are serialized to JSON Event Stream format.
        """
        async for token in output:
            chunk = base_response.copy()
            chunk.choices = [dict(CompletionChoice(
                text=token,
                index=0,
                logprobs=-1,
                finish_reason=''
            ))]
            yield f"data: {json.dumps(dict(chunk))}\n\n"

    def __del__(self):
        if self.session_id is not None:
            self.end_session()
