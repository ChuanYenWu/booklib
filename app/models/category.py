from datetime import datetime
from . import db

# 書籍和題材的關聯表
book_category = db.Table('book_category',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    # 與書籍的多對多關係
    books = db.relationship('Book', 
                          secondary=book_category,
                          lazy='dynamic',
                          backref=db.backref('categories', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Category {self.name}>' 