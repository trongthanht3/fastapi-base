from ragatouille import RAGPretrainedModel
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import os
import logging
logger = logging.getLogger('uvicorn')

# Check if pretrained is already downloaded
if not os.path.exists("app/vectordb/colbert/indexes/"):
    os.makedirs("app/vectordb/colbert/indexes")
if not os.path.exists("app/vectordb/colbert/indexes/ethereum-org-no-split"):
    import zipfile
    import gdown
    logger.info("Downloading the pretrained model")
    gdown.download(id="1-5VrYz1w0rVAfz_0UulhkNu1isNL7OP9",
                   output="app/vectordb/colbert/indexes/ethereum-org.zip", quiet=False)
    with zipfile.ZipFile("app/vectordb/colbert/indexes/ethereum-org.zip", 'r') as zip_ref:
        zip_ref.extractall("app/vectordb/colbert/indexes/")

RAG = RAGPretrainedModel.from_index(
    "app/vectordb/colbert/indexes/ethereum-org-no-split")
retriever = RAG.as_langchain_retriever(k=10)


class RetrievalInput(BaseModel):
    query: str = Field(description="should be a search query")


class EthereumOrgRetrieverTool(BaseTool):
    name = "search_ethereum_network_information"
    description = "Searches and returns only information relate to blockchain, \
      especially information about Ethereum or EVM-based network (EIP/ERC standards, layer 1, layer 2, etc.). \
      If the question is not about the blockchain, do not use this tool."
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
