"""test running migrations

Revision ID: 534fa2b8cfc1
Revises: 1ef0eb9e5d15
Create Date: 2024-05-29 07:17:09.941811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '534fa2b8cfc1'
down_revision: Union[str, None] = '1ef0eb9e5d15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
