"""add_likes_count_to_resources

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2023-05-25 23:16:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None  # 如果这是第一个迁移，设为None，否则应该设置为前一个迁移的ID
branch_labels = None
depends_on = None


def upgrade():
    # 添加likes_count列到resources表，设置默认值为0
    op.add_column('resources', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))
    
    # 创建索引以优化按喜欢数量排序的查询
    op.create_index('ix_resources_likes_count', 'resources', ['likes_count'], unique=False)


def downgrade():
    # 删除索引
    op.drop_index('ix_resources_likes_count', table_name='resources')
    
    # 删除likes_count列
    op.drop_column('resources', 'likes_count') 