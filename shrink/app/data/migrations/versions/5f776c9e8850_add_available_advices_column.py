"""Add available advices column

Revision ID: 5f776c9e8850
Revises: fd6804a0a1c9
Create Date: 2024-04-27 17:00:22.974918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f776c9e8850'
down_revision: Union[str, None] = 'fd6804a0a1c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email_settings', sa.Column('advice_for_frequency', sa.Integer(), nullable=True))
    op.add_column('email_settings', sa.Column('advice_for_quantity', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('email_settings', 'advice_for_quantity')
    op.drop_column('email_settings', 'advice_for_frequency')
    # ### end Alembic commands ###
