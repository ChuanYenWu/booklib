"""Create BookURL and AuthorURL tables

Revision ID: url_tables_split
Revises: 
Create Date: 2023-05-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'url_tables_split'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 創建 BookURL 表
    op.create_table('book_urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('book_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # 創建 AuthorURL 表
    op.create_table('author_urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 從舊的 URLs 表中遷移數據
    op.execute("""
        INSERT INTO book_urls (url, description, book_id)
        SELECT url, description, book_id
        FROM urls
        WHERE type = 'book' AND book_id IS NOT NULL
    """)
    
    op.execute("""
        INSERT INTO author_urls (url, description, author_id)
        SELECT url, description, author_id
        FROM urls
        WHERE type = 'author' AND author_id IS NOT NULL
    """)
    
    # 不要立即刪除舊表，讓管理員確認數據正確性後再刪除
    # op.drop_table('urls')


def downgrade():
    # 刪除新的表格
    op.drop_table('author_urls')
    op.drop_table('book_urls')
    
    # 注意：此操作不會還原已經從 urls 表遷移的數據 