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
        # 假設模板會提供 multiple inputs for new urls, like new_url[] and new_url_description[]
        new_urls = request.form.getlist('new_url[]')
        new_descriptions = request.form.getlist('new_url_description[]')
        
        # Ensure lists are of the same length, process pairs
        for i in range(min(len(new_urls), len(new_descriptions))):
            url = new_urls[i].strip()
            description = new_descriptions[i].strip()
            if url: # Only add if url is not empty
                 url_obj = URL(url=url, description=description, type='book', book=book)
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
        
        # 處理相關網址 (更新、刪除現有，新增)
        existing_urls_to_keep = []
        for url_obj in book.urls:
            url_id_str = str(url_obj.id)
            # 檢查是否有對應的表單數據，以及是否標記為刪除
            if f'url-{url_id_str}' in request.form and f'delete_url-{url_id_str}' not in request.form:
                # 更新現有網址資訊
                url_obj.url = request.form[f'url-{url_id_str}']
                url_obj.description = request.form.get(f'description-{url_id_str}', '')
                existing_urls_to_keep.append(url_obj)
            else:
                # 如果沒有對應表單數據或標記為刪除，則刪除該網址
                db.session.delete(url_obj)

        # 清空舊的關聯後重新添加保留的URL，確保數據庫同步
        book.urls = existing_urls_to_keep

        # 處理新增網址
        # 假設模板會提供 multiple inputs for new urls, like new_url[] and new_url_description[]
        new_urls = request.form.getlist('new_url[]')
        new_descriptions = request.form.getlist('new_url_description[]')
        
        # Ensure lists are of the same length, process pairs
        for i in range(min(len(new_urls), len(new_descriptions))):
            url = new_urls[i].strip()
            description = new_descriptions[i].strip()
            if url: # Only add if url is not empty
                 url_obj = URL(url=url, description=description, type='book', book=book)
                 db.session.add(url_obj)

        db.session.commit()
        flash('書籍資訊及相關網站已更新！', 'success')
        return redirect(url_for('book.book_detail', id=id))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    # 傳遞 url 資訊到模板
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