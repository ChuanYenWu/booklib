from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models.author import Author
from app.models.url import AuthorURL
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
            name=request.form['name']
        )
        db.session.add(author)
        
        # 如果提供了URL，則創建URL記錄
        url = request.form.get('url')
        if url:
            url_obj = AuthorURL(
                url=url,
                description=request.form.get('url_description', url),
                author=author
            )
            db.session.add(url_obj)
        
        db.session.commit()
        flash('作者已成功新增！', 'success')
        return redirect(url_for('author.list_authors'))
    
    return render_template('author/add.html')

@bp.route('/author/<int:id>/edit', methods=['GET', 'POST'])
def edit_author(id):
    author = Author.query.get_or_404(id)

    if request.method == 'POST':
        author.name = request.form['name']
        
        # 處理相關網站 (URLs)
        urls_data = request.form.getlist('urls') # 獲取 urls 的列表
        
        # 由於前端使用了索引命名，直接獲取 urls 的列表可能無法正確解析結構
        # 我們需要迭代索引來獲取每個網址的資料
        i = 0
        while True:
            url_id = request.form.get(f'urls[{i}][id]')
            url_value = request.form.get(f'urls[{i}][url]')
            description = request.form.get(f'urls[{i}][description]', '')
            delete_flag = request.form.get(f'urls[{i}][delete]', '0')

            # 如果找不到当前索引的url值，表示已经遍历完所有url
            if url_value is None:
                break

            if delete_flag == '1' and url_id:
                # 刪除現有網址
                url_to_delete = AuthorURL.query.get(url_id)
                if url_to_delete:
                    db.session.delete(url_to_delete)
            elif delete_flag == '0':
                if url_id:
                    # 更新現有網址
                    url_to_update = AuthorURL.query.get(url_id)
                    if url_to_update:
                        url_to_update.url = url_value
                        url_to_update.description = description
                else:
                    # 新增網址
                    if url_value: # 確保網址不為空
                         new_url = AuthorURL(
                            url=url_value,
                            description=description,
                            author=author
                        )
                         db.session.add(new_url)

            i += 1
        
        db.session.commit()
        flash('作者資料已成功更新！', 'success')
        return redirect(url_for('author.author_detail', id=author.id))

    return render_template('author/edit.html', author=author)

@bp.route('/author/<int:id>/delete', methods=['POST'])
def delete_author(id):
    author = Author.query.get_or_404(id)
    
    # 檢查是否有相關聯的書籍
    if author.books.count() > 0:
        flash(f'無法刪除作者「{author.name}」，因為有 {author.books.count()} 本相關聯的書籍。請先刪除或修改這些書籍的作者資訊。', 'danger')
        return redirect(url_for('author.author_detail', id=author.id))
    
    # 如果沒有相關聯的書籍，則執行刪除
    db.session.delete(author)
    db.session.commit()
    flash(f'作者「{author.name}」已成功刪除。', 'success')
    return redirect(url_for('author.list_authors')) 