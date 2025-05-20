from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models.author import Author
from app.models.url import URL
from app import db

bp = Blueprint('author', __name__)

@bp.route('/authors')
def list_authors():
    authors = Author.query.all()
    return render_template('author/list.html', authors=authors)

@bp.route('/author/<int:id>')
def author_detail(id):
    author = Author.query.get_or_404(id)
    return render_template('author/detail.html', author=author)

@bp.route('/author/add', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        author = Author(
            name=request.form['name'],
            description=request.form.get('description')
        )
        db.session.add(author)
        
        # 如果提供了URL，則創建URL記錄
        url = request.form.get('url')
        if url:
            url_obj = URL(
                url=url,
                description=request.form.get('url_description', url),
                type='author',
                author=author
            )
            db.session.add(url_obj)
        
        db.session.commit()
        flash('作者已成功新增！', 'success')
        return redirect(url_for('author.list_authors'))
    
    return render_template('author/add.html') 