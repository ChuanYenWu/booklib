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
    #description = db.Column(db.Text)
    
    # 可以建立階層關係（例如：科幻是奇幻的子類別）
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    # 與書籍的多對多關係
    books = db.relationship('Book', 
                          secondary=book_category,
                          lazy='dynamic',
                          backref=db.backref('categories', lazy='dynamic'))
    
    # 時間戳記
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'
        
    @property
    def full_name(self):
        """返回完整的分類路徑（包含父分類）"""
        if self.parent:
            return f'{self.parent.full_name} > {self.name}'
        return self.name 