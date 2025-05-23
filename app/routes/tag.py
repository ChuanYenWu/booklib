from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models.tag import Tag
from app import db

bp = Blueprint('tag', __name__)

@bp.route('/tags')
def list_tags():
    tags = Tag.query.all()
    return render_template('tag/list.html', tags=tags)

@bp.route('/tag/<int:id>')
def tag_detail(id):
    tag = Tag.query.get_or_404(id)
    return render_template('tag/detail.html', tag=tag)

@bp.route('/tag/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        tag = Tag(name=request.form['name'])
        db.session.add(tag)
        db.session.commit()
        flash('標籤已成功新增！', 'success')
        return redirect(url_for('tag.list_tags'))
    
    return render_template('tag/add.html')

@bp.route('/tag/<int:id>/delete', methods=['POST'])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    # 檢查是否有相關聯的書籍
    if tag.books.count() > 0:
        flash(f'無法刪除標籤「{tag.name}」，因為有 {tag.books.count()} 本相關聯的書籍。請先刪除或修改這些書籍的標籤資訊。', 'danger')
        return redirect(url_for('tag.tag_detail', id=tag.id))
    
    # 如果沒有相關聯的書籍，則執行刪除
    db.session.delete(tag)
    db.session.commit()
    flash(f'標籤「{tag.name}」已成功刪除。', 'success')
    return redirect(url_for('tag.list_tags'))

@bp.route('/tag/<int:id>/edit', methods=['GET', 'POST'])
def edit_tag(id):
    tag = Tag.query.get_or_404(id)

    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        flash('標籤資料已成功更新！', 'success')
        return redirect(url_for('tag.tag_detail', id=tag.id))

    return render_template('tag/edit.html', tag=tag) 