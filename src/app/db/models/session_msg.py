from sqlalchemy import ForeignKey
from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .user_session import UserSession


class Base(DeclarativeBase):
    pass


class SessionMsg(Base):
    __tablename__ = "session_msg"

    session_msg_id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_session_id: Mapped[int] = mapped_column(Integer(), ForeignKey(UserSession.user_session_id), nullable=False)
    user_msg_content: Mapped[str] = mapped_column(String(), nullable=False)
    system_msg_content: Mapped[str] = mapped_column(String(), nullable=True)
    create_at: Mapped[str] = mapped_column(DateTime(), nullable=False)
    feedback: Mapped[bool] = mapped_column(Boolean(), nullable=True)
    feedback_content: Mapped[str] = mapped_column(String(), nullable=True)

    def __repr__(self) -> str:
        return f"SessionMsg(session_msg_id={self.session_msg_id!r}, user_session_id={self.user_session_id!r}, user_msg_content={self.user_msg_content!r}, system_msg_content={self.system_msg_content!r}, create_at={self.create_at!r}, feedback={self.feedback!r}, feedback_content={self.feedback_content!r})"
