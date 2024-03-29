from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, JSON, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .user_chat_session import UserChatSession


class Base(DeclarativeBase):
    pass


class MessageStore(Base):
    __tablename__ = "message_store"

    id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, autoincrement=True, nullable=False)
    session_id: Mapped[str] = mapped_column(
        String(), ForeignKey(UserChatSession.user_session_id), nullable=False)
    message: Mapped[str] = mapped_column(JSON, nullable=False)
    content_source: Mapped[str] = mapped_column(String(), nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(), nullable=False)

    def __repr__(self) -> str:
        return f"MessageStore(id={self.id}, session_id={self.session_id}, message={self.message}, created_at={self.created_at})"
