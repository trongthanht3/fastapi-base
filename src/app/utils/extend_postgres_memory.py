# Implement get last k messages from postgres
from langchain_community.chat_message_histories.postgres import PostgresChatMessageHistory

import json
import datetime
from typing import List
from app.db.engine import sqlalchemy_engine
from app.db.models.message_store import MessageStore
from sqlalchemy.orm import sessionmaker

from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)

import logging
logger = logging.getLogger('uvicorn')


class ExtendPostgresChatMessageHistory(PostgresChatMessageHistory):
    def __init__(
        self,
        session_id: str,
        connection_string: str = ...,
        table_name: str = "message_store",
        k: int = 5,
    ):
        super().__init__(session_id, connection_string, table_name)
        self.k = k
        self.session_maker_extend = sessionmaker(bind=sqlalchemy_engine)
        self.db_session_extend = self.session_maker_extend()

    def _create_table_if_not_exists(self) -> None:
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            message JSONB NOT NULL,
            content_source TEXT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );"""
        self.cursor.execute(create_table_query)
        self.connection.commit()

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from PostgreSQL"""
        query = (
            f"SELECT message FROM {self.table_name} WHERE session_id = %s ORDER BY id;"
        )
        self.cursor.execute(query, (self.session_id,))
        items = [record["message"] for record in self.cursor.fetchall()]
        messages = messages_from_dict(items)
        return messages[-self.k * 2:] if self.k > 0 else []

    def messages_paging(self, page: int, page_size: int) -> List[BaseMessage]:
        """Retrieve the messages from PostgreSQL"""
        # paging query with sqlalchemy to prevent SQL injection
        messages = self.db_session_extend.query(MessageStore).filter(
            MessageStore.session_id == self.session_id).order_by(MessageStore.id.desc()).limit(page_size).offset(page * page_size).all()

        # reseverse order
        return messages[::-1]

    def full_messages(self, detail=False):
        """Retrieve the messages from PostgreSQL"""
        if detail:
            query = (
                f"SELECT id, message, created_at FROM {self.table_name} WHERE session_id = %s ORDER BY id;"
            )
            self.cursor.execute(query, (self.session_id,))
            items = [record for record in self.cursor.fetchall()]
            return items
        else:
            query = (
                f"SELECT message FROM {self.table_name} WHERE session_id = %s ORDER BY id;"
            )
            self.cursor.execute(query, (self.session_id,))
            items = [record["message"] for record in self.cursor.fetchall()]
            messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in PostgreSQL"""
        from psycopg import sql

        query = sql.SQL("INSERT INTO {} (session_id, message, created_at) VALUES (%s, %s, %s);").format(
            sql.Identifier(self.table_name)
        )
        self.cursor.execute(
            query, (self.session_id, json.dumps(
                message_to_dict(message)), datetime.datetime.now())
        )
        self.connection.commit()
