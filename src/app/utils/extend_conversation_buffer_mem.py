from langchain.memory import ConversationBufferWindowMemory
from typing import List

from langchain_core.messages import BaseMessage


class ExtendedConversationBufferWindowMemory(ConversationBufferWindowMemory):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()

    @property
    def messages(self) -> List[BaseMessage]:
        return self.chat_memory.messages[-self.k * 2:] if self.k > 0 else []
