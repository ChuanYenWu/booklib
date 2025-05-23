from app import create_app, db
from app.models.url import BookURL, AuthorURL
from sqlalchemy import text, inspect

def migrate_urls():
    """
    遷移腳本：將舊的 URLs 表中的數據遷移到新的 BookURL 和 AuthorURL 表中
    """
    app = create_app()

    with app.app_context():
        inspector = inspect(db.engine)
        
        # 檢查新的表是否已經建立
        book_urls_exists = inspector.has_table('book_urls')
        author_urls_exists = inspector.has_table('author_urls')
        
        if not book_urls_exists or not author_urls_exists:
            print("錯誤：新的表格尚未建立")
            print(f"book_urls 表存在: {book_urls_exists}")
            print(f"author_urls 表存在: {author_urls_exists}")
            return False

        # 檢查舊的表是否存在
        if not inspector.has_table('urls'):
            print("警告：找不到舊的 URLs 表，可能已經被移除")
            return False
            
        # 查找現有的 BookURL 和 AuthorURL 記錄數
        book_urls_count = db.session.query(BookURL).count()
        author_urls_count = db.session.query(AuthorURL).count()
        
        if book_urls_count > 0 or author_urls_count > 0:
            print(f"警告：新表中已存在數據")
            print(f"book_urls 表中有 {book_urls_count} 條記錄")
            print(f"author_urls 表中有 {author_urls_count} 條記錄")
            
            proceed = input("是否繼續遷移？這可能會導致數據重複。(y/n): ")
            if proceed.lower() != 'y':
                print("遷移已取消")
                return False

        # 從舊表中獲取所有 URL 數據
        old_urls = db.session.execute(text('SELECT * FROM urls')).fetchall()
        print(f"找到 {len(old_urls)} 個舊 URL 記錄需要遷移")

        # 遷移書籍 URL
        book_urls_migrated = 0
        for url in old_urls:
            if hasattr(url, 'type') and hasattr(url, 'book_id') and url.type == 'book' and url.book_id is not None:
                new_book_url = BookURL(
                    url=url.url,
                    description=url.description,
                    book_id=url.book_id
                )
                db.session.add(new_book_url)
                book_urls_migrated += 1

        # 遷移作者 URL
        author_urls_migrated = 0
        for url in old_urls:
            if hasattr(url, 'type') and hasattr(url, 'author_id') and url.type == 'author' and url.author_id is not None:
                new_author_url = AuthorURL(
                    url=url.url,
                    description=url.description,
                    author_id=url.author_id
                )
                db.session.add(new_author_url)
                author_urls_migrated += 1

        # 提交變更
        db.session.commit()
        
        print(f"遷移完成！")
        print(f"- 遷移了 {book_urls_migrated} 個書籍 URL")
        print(f"- 遷移了 {author_urls_migrated} 個作者 URL")
        
        return True

if __name__ == "__main__":
    migrate_urls() 