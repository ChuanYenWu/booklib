from app import create_app, db
from app.models.author import Author
from app.models.book import Book
from app.models.category import Category
from app.models.tag import Tag
from app.models.url import URL

def create_test_data():
    # 創建作者
    author1 = Author(name='村上春樹')
    author2 = Author(name='東野圭吾')
    author3 = Author(name='劉慈欣')
    
    # 創建分類
    fiction = Category(name='小說')
    scifi = Category(name='科幻', parent=fiction)
    mystery = Category(name='推理', parent=fiction)
    literature = Category(name='文學', parent=fiction)
    
    # 創建標籤
    tag1 = Tag(name='暢銷書')
    tag2 = Tag(name='獲獎作品')
    tag3 = Tag(name='經典')
    
    # 創建書籍
    book1 = Book(
        title='挪威的森林',
        description='一部關於青春、愛情與失落的故事',
        reading_status=2,  # 已讀
        rating=5
    )
    book1.authors.append(author1)
    book1.categories.append(literature)
    book1.tags.extend([tag1, tag3])
    
    book2 = Book(
        title='解憂雜貨店',
        description='溫暖人心的奇幻故事',
        reading_status=2,  # 已讀
        rating=4
    )
    book2.authors.append(author2)
    book2.categories.append(mystery)
    book2.tags.append(tag1)
    
    book3 = Book(
        title='三體',
        description='宏大的科幻史詩',
        reading_status=1,  # 閱讀中
        rating=5
    )
    book3.authors.append(author3)
    book3.categories.append(scifi)
    book3.tags.extend([tag1, tag2])
    
    # 創建相關網址
    url1 = URL(
        url='https://zh.wikipedia.org/wiki/村上春樹',
        description='村上春樹維基百科',
        type='author'
    )
    url2 = URL(
        url='https://book.douban.com/subject/1046265/',
        description='挪威的森林豆瓣頁面',
        type='book'
    )
    
    # 添加到資料庫
    db.session.add_all([
        author1, author2, author3,
        fiction, scifi, mystery, literature,
        tag1, tag2, tag3,
        book1, book2, book3,
        url1, url2
    ])
    
    # 提交更改
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_test_data() 