"""update type of field created_at

Revision ID: ee15ca92987c
Revises: 5acab52183fa
Create Date: 2023-12-22 16:00:08.993860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DateTime


# revision identifiers, used by Alembic.
revision: str = 'ee15ca92987c'
down_revision: Union[str, None] = '5acab52183fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # update type of field create_at to DateTime
    op.alter_column('user_session', 'create_at', existing_type=sa.Date(), type_=DateTime())
    op.alter_column('session_msg', 'create_at', existing_type=sa.Date(), type_=DateTime())


def downgrade() -> None:
    # downgrade type of field create_at to Date
    op.alter_column('user_session', 'create_at', existing_type=sa.DateTime(), type_=sa.Date())
    op.alter_column('session_msg', 'create_at', existing_type=sa.DateTime(), type_=sa.Date())
