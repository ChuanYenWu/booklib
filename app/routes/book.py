from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.book import Book
from app import db
from datetime import datetime

bp = Blueprint('book', __name__)

@bp.route('/')
def index():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('index.html', books=books)

@bp.route('/book/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form.get('isbn'),
            status=request.form.get('status', '未讀'),
            tags=request.form.get('tags'),
            notes=request.form.get('notes')
        )
        
        if request.form.get('rating'):
            book.rating = int(request.form['rating'])
            
        if request.form.get('start_date'):
            book.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            
        if request.form.get('end_date'):
            book.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        db.session.add(book)
        db.session.commit()
        flash('書籍已成功新增！')
        return redirect(url_for('book.index'))
        
    return render_template('add.html')

@bp.route('/book/<int:id>')
def book_detail(id):
    book = Book.query.get_or_404(id)
    return render_template('detail.html', book=book)

@bp.route('/book/<int:id>/edit', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form.get('isbn')
        book.status = request.form.get('status', '未讀')
        book.tags = request.form.get('tags')
        book.notes = request.form.get('notes')
        
        if request.form.get('rating'):
            book.rating = int(request.form['rating'])
            
        if request.form.get('start_date'):
            book.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            
        if request.form.get('end_date'):
            book.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        db.session.commit()
        flash('書籍資訊已更新！')
        return redirect(url_for('book.book_detail', id=id))
        
    return render_template('edit.html', book=book)

@bp.route('/book/<int:id>/delete', methods=['POST'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('書籍已刪除！')
    return redirect(url_for('book.index')) 