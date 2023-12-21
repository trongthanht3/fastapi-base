"""session_msg: add language

Revision ID: e148023ae1e1
Revises: 06b186126593
Create Date: 2023-12-21 14:50:30.468650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e148023ae1e1'
down_revision: Union[str, None] = '06b186126593'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('session_msg', sa.Column('language_code', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('session_msg', 'language_code')
