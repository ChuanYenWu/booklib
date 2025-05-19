from . import db

class URL(db.Model):
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))  # 網址的簡短描述
    
    # 關聯類型（用於區分是書籍網址還是作者網址）
    type = db.Column(db.String(20), nullable=False)  # 'book' 或 'author'
    
    # 外鍵關聯（一個網址只能屬於一本書或一位作者）
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    
    def __repr__(self):
        return f'<URL {self.url}>' 