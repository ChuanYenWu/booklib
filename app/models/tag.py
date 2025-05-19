from . import db

# 書籍和標籤的關聯表
book_tag = db.Table('book_tag',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    # 與書籍的多對多關係
    books = db.relationship('Book', 
                          secondary=book_tag,
                          lazy='dynamic',
                          backref=db.backref('tags', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Tag {self.name}>' 