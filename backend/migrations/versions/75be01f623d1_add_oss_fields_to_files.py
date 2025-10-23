"""add_oss_fields_to_files

Revision ID: 75be01f623d1
Revises: c4f2d85e31f8
Create Date: 2025-10-23 18:09:05.846515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75be01f623d1'
down_revision = 'c4f2d85e31f8'
branch_labels = None
depends_on = None


def upgrade():
    # 添加OSS相关字段
    op.add_column('files', sa.Column('is_oss', sa.Boolean(), nullable=True, server_default='0'))
    op.add_column('files', sa.Column('oss_path', sa.String(length=500), nullable=True))
    op.add_column('files', sa.Column('oss_url', sa.String(length=500), nullable=True))


def downgrade():
    # 删除OSS相关字段
    op.drop_column('files', 'oss_url')
    op.drop_column('files', 'oss_path')
    op.drop_column('files', 'is_oss')