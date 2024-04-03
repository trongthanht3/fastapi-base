import os
from app.core.config import settings
from app.core.llm.base_llm import BaseLLMSession
from langchain_openai import ChatOpenAI
from app.utils.constants import PROMPTS, LANGUAGES
from app.core.tools.rag_tools import EthereumOrgRetrieverTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_community.chat_message_histories import (
    PostgresChatMessageHistory,
)
from langchain.agents import AgentExecutor

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY


class ExpertEthereum(BaseLLMSession):
    def __init__(self, session_id: str, language_code="en"):
        super().__init__(session_id=session_id, language_code=language_code)
        self.tools = [EthereumOrgRetrieverTool()]
        self.prompt = self.get_prompt(language_code)

        self.model = ChatOpenAI(
            model="gpt-3.5-turbo-0125", streaming=True, temperature=0)
        self.model_with_tools = ChatOpenAI(model="gpt-3.5-turbo-0125").bind(
            tools=[convert_to_openai_tool(tool) for tool in self.tools])
        self.memory = PostgresChatMessageHistory(
            connection_string=settings.POSTGRES_DATABASE_URI.unicode_string(),
            session_id=session_id,
        )
        self.agent = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
            }
            | self.prompt
            | self.model_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True, return_intermediate_steps=True)

        self.runable = RunnableWithMessageHistory(
            self.agent_executor,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def get_prompt(self, language_code: str):
        """
        Start a new chat session
        :param language_code:
        :return:
        """
        if language_code == LANGUAGES.ENGLISH.value:
            self.prompt = PROMPTS.RAG_WITH_MESSAGE_TEMPLATE
            self.language_code = LANGUAGES.ENGLISH.value
        elif language_code == LANGUAGES.JAPANESE.value:
            self.prompt = PROMPTS.RAG_WITH_MESSAGE_TEMPLATE_JAPANESE
            self.language_code = LANGUAGES.JAPANESE.value

        return self.prompt
