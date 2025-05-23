from . import db

class BookURL(db.Model):
    __tablename__ = 'book_urls'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))  # 網址的簡短描述
    
    # 外鍵關聯（一個網址只能屬於一本書）
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    
    def __repr__(self):
        return f'<BookURL {self.url}>'

class AuthorURL(db.Model):
    __tablename__ = 'author_urls'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))  # 網址的簡短描述
    
    # 外鍵關聯（一個網址只能屬於一位作者）
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    
    def __repr__(self):
        return f'<AuthorURL {self.url}>' 