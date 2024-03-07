import os
from app.core.config import settings
from app.core.llm.base_llm import BaseLLMSession
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ragatouille import RAGPretrainedModel
from langchain.chains import ConversationChain

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

# RAG = RAGPretrainedModel.from_pretrained("colbert-ir/colbertv2.0")


RAG = RAGPretrainedModel.from_index("app/vectordb/colbert/indexes/ethereum-org-no-split")

class ExpertEthereum(BaseLLMSession):
    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.retriever = RAG.as_langchain_retriever(k=10)
        self.prompt = ChatPromptTemplate.from_template(
            """Answer the following question based only on the provided context:
            <context>
            {context}
            </context>

            Question: {input}"""
        )

        self.model = ChatOpenAI(model="gpt-3.5-turbo-0125")
        self.chat = ConversationChain(llm=self.model)

        self.document_chain = create_stuff_documents_chain(self.model, self.prompt)
        self.retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)

    async def send_message(self, message: str):
        result = await self.retrieval_chain.ainvoke({"input": message})
        return result
