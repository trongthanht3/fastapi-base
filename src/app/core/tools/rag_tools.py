from ragatouille import RAGPretrainedModel
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


RAG = RAGPretrainedModel.from_index("app/vectordb/colbert/indexes/ethereum-org-no-split")
retriever = RAG.as_langchain_retriever(k=10)

class RetrievalInput(BaseModel):
  query: str = Field(description="should be a search query")


class RetrievalInput(BaseModel):
  query: str = Field(description="should be a search query")

class EthereumOrgRetrieverTool(BaseTool):
    name = "search_ethereum_network_information"
    description = "Searches and returns only information relate to blockchain, especially Ethereum or EVM-based network. If the question is not about the blockchain, do not use this tool."
    args_schema: Type[BaseModel] = RetrievalInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        return self.search_function(query)

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        return await self.search_function_async(query)
      
    def search_function(self, query: str):
      docs = retriever.invoke(query)
      docs_json = []
      for doc in docs:
        docs_json.append(
            {
                'page_content': doc.page_content,
                'metadata': doc.metadata
            }
        )
      return docs_json

    async def search_function_async(self, query: str):
      docs = await retriever.ainvoke(query)
      docs_json = []
      for doc in docs:
        docs_json.append(
            {
                'page_content': doc.page_content,
                'metadata': doc.metadata
            }
        )
      return docs_json