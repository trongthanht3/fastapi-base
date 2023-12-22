"""add column language code to user_session

Revision ID: 7e50bc2dabed
Revises: ee15ca92987c
Create Date: 2023-12-22 17:31:34.083431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e50bc2dabed'
down_revision: Union[str, None] = 'ee15ca92987c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_session', sa.Column('language_code', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_session', 'language_code')
    # ### end Alembic commands ###
