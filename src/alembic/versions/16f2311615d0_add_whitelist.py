"""add user

Revision ID: 16f2311615d0
Revises: 58544855b2cf
Create Date: 2024-03-21 10:32:46.144224

"""
from typing import Sequence, Union
import datetime
from alembic import op
import sqlalchemy as sa
# from app.core.config import settings


# revision identifiers, used by Alembic.
revision: str = '16f2311615d0'
down_revision: Union[str, None] = '58544855b2cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("address", sa.String(), nullable=False, unique=True),
        sa.Column("create_at", sa.DateTime(), nullable=True),
        sa.Column("token_expire_at", sa.DateTime(), nullable=True),
        sa.Column("is_banned", sa.Boolean(), nullable=True),
        sa.Column("ban_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.drop_column("user_session", "user_id")
    op.add_column(
        "user_session",
        sa.Column("user_id", sa.Integer(), nullable=False),
    )
    # set user_id as foreign key of user_session
    op.create_foreign_key(
        "fk_user_session_user_id",
        "user_session",
        "user",
        ["user_id"],
        ["user_id"],
    )

    # add super addmin address
    op.execute(
        f"""
        INSERT INTO "user" (address, create_at, token_expire_at, is_banned, ban_at)
        VALUES ('0x962A931ec80473C6D75653c0cB0713aeE90e3Ed2', '{str(datetime.datetime.now())}', '3024-03-22 10:32:46.144224', false, null)
        """
    )


def downgrade() -> None:
    op.drop_constraint("fk_user_session_user_id",
                       "user_session", type_="foreignkey")
    op.drop_table("user")
    op.drop_column("user_session", "user_id")
    op.add_column(
        "user_session",
        sa.Column("user_id", sa.String(), nullable=False),
    )
