"""add_draft_tables

Revision ID: 20251130102953
Revises: 43e1959dff52
Create Date: 2025-11-30 10:29:53

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251130102953'
down_revision = '43e1959dff52'
branch_labels = None
depends_on = None


def upgrade():
    # 创建 drafts 表
    op.create_table(
        'drafts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('current_version_id', sa.Integer(), nullable=True),
        sa.Column('editing_stage', sa.String(length=32), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_drafts_template_user', 'drafts', ['template_id', 'user_id'], unique=True)

    # 创建 draft_versions 表
    op.create_table(
        'draft_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('draft_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('format', sa.String(length=50), nullable=False, server_default='markdown'),
        sa.Column('change_summary', sa.String(length=500), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['draft_id'], ['drafts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_draft_versions_draft_id', 'draft_versions', ['draft_id'])
    op.create_index('ix_draft_versions_version_number', 'draft_versions', ['draft_id', 'version_number'], unique=True)

    # 添加外键约束：drafts.current_version_id -> draft_versions.id
    # 注意：这个外键需要在 draft_versions 表创建后添加
    op.create_foreign_key(
        'fk_drafts_current_version',
        'drafts', 'draft_versions',
        ['current_version_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    # 删除外键约束
    op.drop_constraint('fk_drafts_current_version', 'drafts', type_='foreignkey')
    
    # 删除索引和表
    op.drop_index('ix_draft_versions_version_number', 'draft_versions')
    op.drop_index('ix_draft_versions_draft_id', 'draft_versions')
    op.drop_table('draft_versions')
    
    op.drop_index('ix_drafts_template_user', 'drafts')
    op.drop_table('drafts')
