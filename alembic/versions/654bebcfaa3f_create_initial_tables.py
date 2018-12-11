"""Create initial tables

Revision ID: 654bebcfaa3f
Revises:
Create Date: 2018-12-10 15:17:51.256434

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '654bebcfaa3f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('hash_sha512_hex', sa.String(length=128), nullable=False),
        sa.Column(
            'file_type',
            sa.Enum('other', 'video', 'audio', 'photo', 'text', name='filetypeenum'),
            nullable=False
        ),
        sa.Column(
            'date_added_to_collection',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'medias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column(
            'media_type',
            sa.Enum('HDD', 'CD', 'DVD', 'BR', 'CLOUD', 'TAPE', name='mediatypeenum'),
            nullable=False
        ),
        sa.Column('capacity_bytes', sa.BigInteger(), nullable=False),
        sa.Column(
            'date_added_to_collection',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False
        ),
        sa.Column('desc_location', sa.String(), nullable=True),
        sa.Column('desc_make_model', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'media_file_associations',
        sa.Column('medias_id', sa.Integer(), nullable=False),
        sa.Column('files_id', sa.Integer(), nullable=False),
        sa.Column('date_copied_to_media', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['files_id'], ['files.id'], ),
        sa.ForeignKeyConstraint(['medias_id'], ['medias.id'], ),
        sa.PrimaryKeyConstraint('medias_id', 'files_id')
    )

def downgrade():
    op.drop_table('media_file_associations')
    op.drop_table('medias')
    op.drop_table('files')
