from datetime import datetime
from . import db

# 書籍和作者的關聯表
book_author = db.Table('book_author',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'), primary_key=True)
)

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    #description = db.Column(db.Text)
    
    # 可選欄位
    #birth_date = db.Column(db.Date)
    #death_date = db.Column(db.Date)
    #nationality = db.Column(db.String(50))
    
    # 與書籍的多對多關係
    books = db.relationship('Book', 
                          secondary=book_author,
                          lazy='dynamic',
                          backref=db.backref('authors', lazy='dynamic'))
    
    # 相關網址（一對多關係）
    urls = db.relationship('AuthorURL', backref='author', lazy='dynamic',
                         cascade='all, delete-orphan')
    
    # 時間戳記
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Author {self.name}>'
        
    @property
    def personal_sites(self):
        """返回作者個人網站列表"""
        return self.urls.all() 