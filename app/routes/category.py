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