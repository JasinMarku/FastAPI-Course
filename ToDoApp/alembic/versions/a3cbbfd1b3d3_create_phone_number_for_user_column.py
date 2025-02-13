"""Create phone number for user column

Revision ID: a3cbbfd1b3d3
Revises: 
Create Date: 2025-02-07 14:32:40.627217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3cbbfd1b3d3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

# Removes the phone_number column from the users table if we downgrade.
def downgrade() -> None:
    op.drop_column('users', 'phone_number')
