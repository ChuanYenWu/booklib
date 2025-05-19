from datetime import datetime
from . import db

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    #isbn = db.Column(db.String(13), unique=True)
    #publisher = db.Column(db.String(100))
    #publish_date = db.Column(db.Date)
    description = db.Column(db.Text)
    
    # 閱讀狀態：0=未讀, 1=閱讀中, 2=已讀
    reading_status = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer)  # 1-5 星評分
    #notes = db.Column(db.Text)
    
    # 時間戳記
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 相關網址（一對多關係）
    urls = db.relationship('URL', backref='book', lazy='dynamic',
                         foreign_keys='URL.book_id',
                         cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Book {self.title}>'
        
    @property
    def author_names(self):
        """返回作者名稱列表的字串表示"""
        return ', '.join([author.name for author in self.authors]) if self.authors.count() > 0 else '未知作者'
        
    @property
    def category_names(self):
        """返回題材名稱列表的字串表示"""
        return ', '.join([category.name for category in self.categories]) if self.categories.count() > 0 else '未分類'
        
    @property
    def tag_names(self):
        """返回標籤名稱列表的字串表示"""
        return ', '.join([tag.name for tag in self.tags]) if self.tags.count() > 0 else '無標籤'
        
    @property
    def site_urls(self):
        """返回書籍相關網址列表"""
        return self.urls.filter_by(type='book').all() 