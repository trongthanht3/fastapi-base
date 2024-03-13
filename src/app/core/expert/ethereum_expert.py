import os
from app.core.config import settings
from app.core.llm.base_llm import BaseLLMSession
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from app.utils.constants import PROMPTS
from app.core.tools.rag_tools import EthereumOrgRetrieverTool
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_tool

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
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

# RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")

class ExpertEthereum(BaseLLMSession):
    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.tools = [EthereumOrgRetrieverTool()]
        self.prompt = PROMPTS.RAG_WITH_MESSAGE_TEMPLATE

        self.model = ChatOpenAI(model="gpt-3.5-turbo-0125")
        self.model_with_tools = ChatOpenAI(model="gpt-3.5-turbo-0125").bind(
            tools=[convert_to_openai_tool(tool) for tool in self.tools])
        self.chat = ConversationChain(llm=self.model)
        self.memory = PostgresChatMessageHistory(
            connection_string="postgresql://postgres:123456@localhost:5432/mesgpt",
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
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True, return_intermediate_steps=True)

        self.runable = RunnableWithMessageHistory(
            self.agent_executor,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        # self.document_chain = create_stuff_documents_chain(self.model, self.prompt)
        # self.retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)

    def start_new_session(self, language_code: str):
        pass

        return self

    async def send_message(self, message: str):
        # result = await self.retrieval_chain.ainvoke({"input": message})
        return await self.runable.ainvoke(
            {"input": message},
            config={"configurable": {"session_id": self.session_id}}
        )
        
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

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        return self.memory
    
    