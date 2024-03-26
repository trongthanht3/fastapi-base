"""update user chat session table

Revision ID: f22a248e601f
Revises: 16f2311615d0
Create Date: 2024-03-21 18:01:27.245070

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f22a248e601f'
down_revision: Union[str, None] = '16f2311615d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # rename table user_session to user_chat_session
    op.rename_table('user_session', 'user_chat_session')


def downgrade() -> None:
    op.rename_table('user_chat_session', 'user_session')
