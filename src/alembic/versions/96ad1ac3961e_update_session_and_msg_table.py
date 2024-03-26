"""update session and msg table

Revision ID: 96ad1ac3961e
Revises: f22a248e601f
Create Date: 2024-03-26 13:45:43.044924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96ad1ac3961e'
down_revision: Union[str, None] = 'f22a248e601f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_chat_session",
        sa.Column("model", sa.String(), nullable=True),
    )
    op.drop_table("session_msg")


def downgrade() -> None:
    op.create_table(
        "session_msg",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("message", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_column("user_chat_session", "model")
