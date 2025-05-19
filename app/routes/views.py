from flask import render_template, redirect, url_for, flash, request, jsonify
from . import main
from ..models import db
from ..models.book import Book
from ..models.author import Author
from ..models.category import Category
from ..models.tag import Tag
from ..models.url import URL

@main.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@main.route('/book/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # 創建新書籍
        book = Book(
            title=request.form['title'],
            description=request.form.get('description'),
            reading_status=int(request.form.get('reading_status', 0)),
            rating=request.form.get('rating')
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
        
        db.session.add(book)
        db.session.commit()
        flash('書籍已成功添加！', 'success')
        return redirect(url_for('main.index'))
    
    # GET 請求：顯示表單
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('book/add.html', categories=categories, tags=tags)

@main.route('/authors')
def list_authors():
    authors = Author.query.all()
    return render_template('author/list.html', authors=authors)

@main.route('/author/<int:id>')
def author_detail(id):
    author = Author.query.get_or_404(id)
    return render_template('author/detail.html', author=author)

@main.route('/categories')
def list_categories():
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('category/list.html', categories=categories)

@main.route('/category/<int:id>')
def category_detail(id):
    category = Category.query.get_or_404(id)
    return render_template('category/detail.html', category=category)

@main.route('/category/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        parent_id = request.form.get('parent_id')
        category = Category(
            name=request.form['name'],
            parent_id=parent_id if parent_id else None
        )
        db.session.add(category)
        db.session.commit()
        flash('題材已成功添加！', 'success')
        return redirect(url_for('main.list_categories'))
    
    # GET 請求：顯示表單
    categories = Category.query.all()
    return render_template('category/add.html', categories=categories)

@main.route('/tags')
def list_tags():
    tags = Tag.query.all()
    return render_template('tag/list.html', tags=tags)

@main.route('/tag/<int:id>')
def tag_detail(id):
    tag = Tag.query.get_or_404(id)
    return render_template('tag/detail.html', tag=tag)

@main.route('/tag/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        tag = Tag(name=request.form['name'])
        db.session.add(tag)
        db.session.commit()
        flash('標籤已成功添加！', 'success')
        return redirect(url_for('main.list_tags'))
    return render_template('tag/add.html')

@main.route('/book/<int:id>/add_url', methods=['POST'])
def add_book_url():
    book_id = request.form.get('book_id')
    url = request.form.get('url')
    description = request.form.get('description', '')
    
    if not url:
        return jsonify({'error': '網址不能為空'}), 400
        
    book = Book.query.get_or_404(book_id)
    new_url = URL(
        url=url,
        description=description,
        type='book',
        book_id=book_id
    )
    
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({'message': '網址已成功添加'})

@main.route('/author/<int:id>/add_url', methods=['POST'])
def add_author_url():
    author_id = request.form.get('author_id')
    url = request.form.get('url')
    description = request.form.get('description', '')
    
    if not url:
        return jsonify({'error': '網址不能為空'}), 400
        
    author = Author.query.get_or_404(author_id)
    new_url = URL(
        url=url,
        description=description,
        type='author',
        author_id=author_id
    )
    
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({'message': '網址已成功添加'})

@main.route('/url/<int:id>/delete', methods=['POST'])
def delete_url():
    url = URL.query.get_or_404(id)
    db.session.delete(url)
    db.session.commit()
    return jsonify({'message': '網址已成功刪除'}) 