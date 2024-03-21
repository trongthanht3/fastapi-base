from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class UserChatSession(Base):
    __tablename__ = "user_chat_session"

    user_session_id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(), nullable=False)
    create_at: Mapped[str] = mapped_column(DateTime(), nullable=True)
    language_code: Mapped[str] = mapped_column(String(), nullable=False)

    def __repr__(self) -> str:
        return f"UserChatSession(user_session_id={self.user_session_id!r}, user_id={self.user_id!r}, create_at={self.create_at!r})"
