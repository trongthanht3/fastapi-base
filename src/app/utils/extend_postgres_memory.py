# Implement get last k messages from postgres
from langchain_community.chat_message_histories.postgres import PostgresChatMessageHistory

import datetime
from typing import List
from app.db.engine import sqlalchemy_engine
from app.db.models.message_store import MessageStore
from langchain.docstore.document import Document
from sqlalchemy.orm import sessionmaker
from app.core.tools.sbert_ret_tools import embedding as sbert_embedding
from langchain_community.vectorstores.pgvector import PGVector
from app.core.config import settings

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
        retrieval_related_messages: bool = False,
    ):
        super().__init__(session_id, connection_string, table_name)
        self.k = k
        self.session_maker_extend = sessionmaker(bind=sqlalchemy_engine)
        self.db_session_extend = self.session_maker_extend()
        self.retrieval_related_messages = retrieval_related_messages
        if self.retrieval_related_messages:
            self.msg_vector_db = PGVector(
                connection_string=settings.POSTGRES_DATABASE_URI.unicode_string(),
                collection_name=self.session_id,
                collection_metadata={"parent_table": self.table_name},
                embedding_function=sbert_embedding,
                use_jsonb=True,
            )
        self.last_message = ""

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
        messages = messages[-self.k * 2:] if self.k > 0 else []

        # add relate message
        related_long_history = self.msg_vector_db.similarity_search_with_relevance_scores(
            self.last_message, k=100)
        logger.info(
            f"Querying relate: {self.last_message} | {related_long_history}")
        # sort by relevance score
        related_long_history = sorted(
            related_long_history, key=lambda x: x[1], reverse=True)

        # remove duplicate
        set_relate_msg = set()
        new_relate_msg = []
        for item, _ in related_long_history:
            if item.page_content not in set_relate_msg:
                set_relate_msg.add(item.page_content)
                new_relate_msg.append(item)
        related_long_history = new_relate_msg[:3]

        # process relate message, add next message if type is human
        relate_message = []
        for item in related_long_history:
            message = self.db_session_extend.query(
                MessageStore).filter_by(id=int(item.metadata["message_id"])).first()
            relate_message.append(message.message)
            if item.metadata["type"] == "human":
                message_ai = self.db_session_extend.query(
                    MessageStore).filter_by(id=int(item.metadata["message_id"]) + 1).first()
                relate_message.append(message_ai.message)

        final_list_msg = messages_from_dict(relate_message) + messages
        return final_list_msg

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
        # from psycopg import sql

        # query = sql.SQL("INSERT INTO {} (session_id, message, created_at) VALUES (%s, %s, %s);").format(
        #     sql.Identifier(self.table_name)
        # )
        # self.cursor.execute(
        #     query, (self.session_id, json.dumps(
        #         message_to_dict(message)), datetime.datetime.now())
        # )
        # self.connection.commit()
        msg_dict = message_to_dict(message)
        msg_store = MessageStore(
            session_id=self.session_id,
            message=msg_dict,
            created_at=datetime.datetime.now()
        )
        self.db_session_extend.commit()
        self.db_session_extend.flush()
        self.db_session_extend.refresh(msg_store)

        # query to check if msg is already exist in vector db
        is_msg_exist = self.msg_vector_db.similarity_search_with_score(
            message.content)
        for item in is_msg_exist:
            if (item[0].page_content == message.content) or (item[1] >= 0.98):
                logger.info(
                    f"Embedded exist, not add to vector db! Relate item: {item[0].page_content}")
                return
        if self.retrieval_related_messages:
            self.msg_vector_db.add_documents(
                documents=[Document(page_content=message.content,
                                    metadata={"message_id": msg_store.id,
                                              "type": msg_dict["data"]["type"], })])
