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