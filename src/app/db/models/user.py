from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(
        Integer(), primary_key=True, autoincrement=True, nullable=False)
    address: Mapped[str] = mapped_column(String(), nullable=False)
    create_at: Mapped[str] = mapped_column(DateTime(), nullable=True)
    token_expire_at: Mapped[str] = mapped_column(DateTime(), nullable=True)
    is_banned: Mapped[bool] = mapped_column(Boolean(), nullable=True)
    ban_at: Mapped[str] = mapped_column(DateTime(), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, address={self.address!r}, create_at={self.create_at!r}, token_expire_at={self.token_expire_at!r}, is_banned={self.is_banned!r}, ban_at={self.ban_at!r})"
