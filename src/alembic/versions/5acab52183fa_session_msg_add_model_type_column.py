"""session_msg: add model type column

Revision ID: 5acab52183fa
Revises: e148023ae1e1
Create Date: 2023-12-21 15:00:37.564496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5acab52183fa'
down_revision: Union[str, None] = 'e148023ae1e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('session_msg', sa.Column('model_type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('session_msg', 'model_type')
