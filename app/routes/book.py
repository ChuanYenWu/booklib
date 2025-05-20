from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Book, Author, Category, Tag, URL

bp = Blueprint('book', __name__)

@bp.route('/')
def index():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('book/index.html', books=books)

@bp.route('/book/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # 創建新書籍
        book = Book(
            title=request.form['title'],
            description=request.form.get('description'),
            reading_status=int(request.form.get('reading_status', 0)),
            rating=int(request.form.get('rating')) if request.form.get('rating') else None
        )
        
        # 處理作者
        author_names = request.form.get('authors', '').split(',')
        for name in author_names:
            name = name.strip()
            if name:
                # 檢查作者是否已存在
                author = Author.query.filter_by(name=name).first()
                if not author:
                    # 如果作者不存在，創建新作者
                    author = Author(name=name)
                    db.session.add(author)
                # 將作者關聯到書籍
                book.authors.append(author)
        
        # 處理題材
        category_names = request.form.get('categories', '').split(',')
        for name in category_names:
            name = name.strip()
            if name:
                # 檢查題材是否已存在
                category = Category.query.filter_by(name=name).first()
                if not category:
                    # 如果題材不存在，創建新題材
                    category = Category(name=name)
                    db.session.add(category)
                # 將題材關聯到書籍
                book.categories.append(category)
                
        # 處理標籤
        tag_names = request.form.get('tags', '').split(',')
        for name in tag_names:
            name = name.strip()
            if name:
                # 檢查標籤是否已存在
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    # 如果標籤不存在，創建新標籤
                    tag = Tag(name=name)
                    db.session.add(tag)
                # 將標籤關聯到書籍
                book.tags.append(tag)
        
        # 處理相關網址
        url = request.form.get('url')
        if url:
            url_obj = URL(
                url=url,
                description=request.form.get('url_description', url),
                type='book',
                book=book
            )
            db.session.add(url_obj)
        
        db.session.add(book)
        db.session.commit()
        flash('書籍已成功新增！', 'success')
        return redirect(url_for('book.index'))
    
    # GET 請求：顯示表單
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('book/add.html', categories=categories, tags=tags)

@bp.route('/book/<int:id>')
def book_detail(id):
    book = Book.query.get_or_404(id)
    return render_template('book/detail.html', book=book)

@bp.route('/book/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.description = request.form.get('description')
        book.reading_status = int(request.form.get('reading_status', 0))
        book.rating = int(request.form.get('rating')) if request.form.get('rating') else None
        
        # 處理作者
        book.authors = []
        author_names = request.form.get('authors', '').split(',')
        for name in author_names:
            name = name.strip()
            if name:
                author = Author.query.filter_by(name=name).first()
                if not author:
                    author = Author(name=name)
                    db.session.add(author)
                book.authors.append(author)
        
        # 處理題材
        book.categories = []
        category_names = request.form.get('categories', '').split(',')
        for name in category_names:
            name = name.strip()
            if name:
                category = Category.query.filter_by(name=name).first()
                if not category:
                    category = Category(name=name)
                    db.session.add(category)
                book.categories.append(category)
        
        # 處理標籤
        book.tags = []
        tag_names = request.form.get('tags', '').split(',')
        for name in tag_names:
            name = name.strip()
            if name:
                tag = Tag.query.filter_by(name=name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.session.add(tag)
                book.tags.append(tag)
        
        db.session.commit()
        flash('書籍資訊已更新！', 'success')
        return redirect(url_for('book.book_detail', id=id))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('book/edit.html', book=book, categories=categories, tags=tags)

@bp.route('/book/<int:id>/delete', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('書籍已刪除！', 'success')
    return redirect(url_for('book.index'))

@bp.route('/book/<int:id>/add_url', methods=['POST'])
def add_book_url(id):
    book = Book.query.get_or_404(id)
    url = request.form.get('url')
    description = request.form.get('description', '')
    
    if not url:
        flash('網址不能為空', 'error')
        return redirect(url_for('book.book_detail', id=id))
        
    url_obj = URL(
        url=url,
        description=description,
        type='book',
        book=book
    )
    
    db.session.add(url_obj)
    db.session.commit()
    
    flash('相關網站已成功新增！', 'success')
    return redirect(url_for('book.book_detail', id=id)) 