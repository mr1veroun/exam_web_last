"""Добавлены подборки книг

Revision ID: 80ba8c97500e
Revises: 64345ac0ab86
Create Date: 2025-05-26 22:30:50.996349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80ba8c97500e'
down_revision = '64345ac0ab86'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('collection',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('collection_book',
        sa.Column('collection_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('collection_id', 'book_id')
    )
    # УДАЛИ оба блока batch_alter_table

def downgrade():
    # УДАЛИ оба блока batch_alter_table
    op.drop_table('collection_book')
    op.drop_table('collection')
