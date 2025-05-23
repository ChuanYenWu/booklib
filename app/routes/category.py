from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models.category import Category
from app import db

bp = Blueprint('category', __name__)

@bp.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template('category/list.html', categories=categories)

@bp.route('/category/<int:id>')
def category_detail(id):
    category = Category.query.get_or_404(id)
    return render_template('category/detail.html', category=category)

@bp.route('/category/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category = Category(
            name=request.form['name']
        )
        db.session.add(category)
        db.session.commit()
        flash('題材已成功新增！', 'success')
        return redirect(url_for('category.list_categories'))
    
    return render_template('category/add.html')

@bp.route('/category/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # 檢查是否有相關聯的書籍
    if category.books.count() > 0:
        flash(f'無法刪除題材「{category.name}」，因為有 {category.books.count()} 本相關聯的書籍。請先刪除或修改這些書籍的題材資訊。', 'danger')
        return redirect(url_for('category.category_detail', id=category.id))
    
    # 如果沒有相關聯的書籍，則執行刪除
    db.session.delete(category)
    db.session.commit()
    flash(f'題材「{category.name}」已成功刪除。', 'success')
    return redirect(url_for('category.list_categories'))

@bp.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)

    if request.method == 'POST':
        category.name = request.form['name']
        db.session.commit()
        flash('題材資料已成功更新！', 'success')
        return redirect(url_for('category.category_detail', id=category.id))

    return render_template('category/edit.html', category=category) 