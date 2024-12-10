from sqlalchemy import select, String, Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.engine import sqlalchemy_engine

from app.schemas.auth_schemas import LoginInput, LoginSuccess, LoginInputOAuth2, RegisterInput
from app.db.models.user import User
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

import logging
logger = logging.getLogger(__name__)


session_maker = sessionmaker(bind=sqlalchemy_engine)


class UserServices():
    def __init__(self):
        self.db_session = session_maker
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_user(self, username):
        with self.db_session() as session:
            user_query = select(User).where(User.username == username)
            user = session.scalars(user_query).first()
            return user

    def add_user(self, register_input: RegisterInput):
        with self.db_session() as session:
            try:
                if self.get_user(register_input.username) is not None:
                    return None
                else:
                    new_user = User(
                        username=register_input.username,
                        password_hash=self.get_password_hash(
                            register_input.password),
                        address=register_input.address
                    )
                    session.add(new_user)
                    session.commit()
                    session.flush()
            except Exception as e:
                logger.error("Error while registering: ", e)
            finally:
                session.rollback()

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
