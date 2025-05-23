from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
        title = request.form['title']

        # 處理作者及相關網站
        # 使用request.form.to_dict(flat=False)來解析嵌套的表單數據
        form_data = request.form.to_dict(flat=False)

        # 將數據轉換為更易於處理的結構
        processed_authors_data = {}

        # 迭代form_data，解析作者和URL數據
        import re
        author_name_pattern = re.compile(r'authors\[(\d+)\]\[name\]')
        author_url_pattern = re.compile(r'authors\[(\d+)\]\[urls\]\[(\d+)\]\[url\]')
        author_description_pattern = re.compile(r'authors\[(\d+)\]\[urls\]\[(\d+)\]\[description\]')

        for key, value_list in form_data.items():
            # 處理作者姓名
            match = author_name_pattern.match(key)
            if match:
                author_index = int(match.group(1))
                if author_index not in processed_authors_data:
                    processed_authors_data[author_index] = {'name': '', 'urls': {}}
                processed_authors_data[author_index]['name'] = value_list[0] if isinstance(value_list, list) else value_list
                continue

            # 處理作者網站URL
            match = author_url_pattern.match(key)
            if match:
                author_index = int(match.group(1))
                url_index = int(match.group(2))
                if author_index not in processed_authors_data:
                    processed_authors_data[author_index] = {'name': '', 'urls': {}}
                if url_index not in processed_authors_data[author_index]['urls']:
                     processed_authors_data[author_index]['urls'][url_index] = {'url': '', 'description': ''}
                processed_authors_data[author_index]['urls'][url_index]['url'] = value_list[0] if isinstance(value_list, list) else value_list
                continue

            # 處理作者網站描述
            match = author_description_pattern.match(key)
            if match:
                author_index = int(match.group(1))
                url_index = int(match.group(2))
                if author_index not in processed_authors_data:
                    processed_authors_data[author_index] = {'name': '', 'urls': {}}
                if url_index not in processed_authors_data[author_index]['urls']:
                     processed_authors_data[author_index]['urls'][url_index] = {'url': '', 'description': ''}
                processed_authors_data[author_index]['urls'][url_index]['description'] = value_list[0] if isinstance(value_list, list) else value_list
                continue

        # 將processed_authors_data轉換為列表，並處理URL字典到列表
        final_authors_list = []
        for author_index in sorted(processed_authors_data.keys()):
            author_data = processed_authors_data[author_index]
            author_name = author_data['name'].strip()

            if author_name:
                 urls_list = []
                 for url_index in sorted(author_data['urls'].keys()):
                      url_entry = author_data['urls'][url_index]
                      # 只添加網址不為空的URL
                      if url_entry['url'].strip():
                           urls_list.append({'url': url_entry['url'].strip(), 'description': url_entry['description'].strip()})

                 final_authors_list.append({'name': author_name, 'urls': urls_list})

        # 從 final_authors_list 中提取作者姓名列表用於重複檢查
        new_book_author_names = [author_data['name'] for author_data in final_authors_list]

        # Check for existing books with the same title
        existing_books = Book.query.filter_by(title=title).all()

        is_duplicate = False
        if existing_books:
            # If books with the same title exist, check if the new book's author list is a subset
            for existing_book in existing_books:
                # Get author names from the existing book
                existing_author_names = [author.name for author in existing_book.authors]

                # Check if all authors from the new book are present in the existing book's authors
                # This checks if the new book's author list is a subset of the existing book's author list
                all_authors_included = all(name in existing_author_names for name in new_book_author_names)

                if all_authors_included:
                    is_duplicate = True
                    break # Found a duplicate, no need to check further

        if is_duplicate:
            flash(f'書名為 "{title}" 且作者包含於資料庫中同名書作者的書籍已存在，不重複新增。', 'warning')
            return redirect(url_for('book.index'))

        # If not a duplicate, proceed with adding the new book
        book = Book(
            title=title,
            description=request.form.get('description'),
            reading_status=int(request.form.get('reading_status', 0)),
            rating=int(request.form.get('rating')) if request.form.get('rating') else None
        )

        # 處理每個作者及其相關網址
        for author_data in final_authors_list:
            author_name = author_data['name']
            # 檢查作者是否已存在
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                # 如果作者不存在，創建新作者
                author = Author(name=author_name)
                db.session.add(author)
            # 將作者關聯到書籍
            book.authors.append(author)

            # 處理作者的相關網址
            for url_entry in author_data['urls']:
                url = url_entry['url']
                description = url_entry['description']
                # 再次檢查URL是否為空，雖然之前已經檢查過，但作為保險
                if url:
                    url_obj = URL(
                        url=url,
                        description=description,
                        type='author', # 設置type為author
                        author=author # 將URL關聯到作者
                    )
                    db.session.add(url_obj)

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

        # --- 開始處理書籍本身的相關網站 (新增) ---
        # 從 request.form 中獲取新增的書籍 URL 數據
        new_book_urls = request.form.getlist('new_url[]')
        new_book_descriptions = request.form.getlist('new_url_description[]')

        # 迭代並新增 URL
        for i in range(len(new_book_urls)):
            url_str = new_book_urls[i].strip()
            description_str = new_book_descriptions[i].strip() if i < len(new_book_descriptions) else ''

            if url_str:
                url_obj = URL(
                    url=url_str,
                    description=description_str,
                    type='book', # 設置type為book
                    book=book # 將URL關聯到書籍
                )
                db.session.add(url_obj)

        # --- 書籍本身的相關網站處理結束 ---

        db.session.add(book)
        db.session.commit()
        flash('書籍及作者相關網站已成功新增！', 'success')
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
        
        # 使用request.form.to_dict(flat=False)來解析嵌套的表單數據
        form_data = request.form.to_dict(flat=False)

        # --- 開始處理作者的更新、新增和刪除 ---

        # 獲取現有作者及其 URL 的映射
        existing_authors_map = {author.id: author for author in book.authors}
        existing_author_urls_map = {url_obj.id: url_obj for url_obj in book.urls if url_obj.author_id is not None}

        # 要在提交後保留的作者 ID 列表 (不包括被標記刪除的)
        submitted_author_ids_to_keep = []

        # 遍歷提交的作者數據，構建一個用於更新/新增的列表，並收集要保留的ID
        import re

        # 構建提交的作者數據結構 (類似於 add_book 中的 processed_authors_data)
        submitted_authors_data = {}
        for key, value_list in form_data.items():
            # 處理作者 ID 和姓名
            match = re.match(r'authors\[(\d+)\]\[(name|id)\]', key)
            if match:
                author_index = int(match.group(1))
                field = match.group(2)
                if author_index not in submitted_authors_data:
                    submitted_authors_data[author_index] = {'id': None, 'name': '', 'urls': {}}
                if field == 'id':
                    submitted_authors_data[author_index]['id'] = int(value_list[0]) if value_list[0].isdigit() else None
                elif field == 'name':
                    submitted_authors_data[author_index]['name'] = value_list[0]
                continue

            # 處理作者 URL ID, URL, 描述, 刪除標記
            match_url = re.match(r'authors\[(\d+)\]\[urls\]\[(\d+)\]\[(url|description|id|delete)\]', key)
            if match_url:
                author_index = int(match_url.group(1))
                url_index = int(match_url.group(2))
                field = match_url.group(3)
                if author_index not in submitted_authors_data:
                    submitted_authors_data[author_index] = {'id': None, 'name': '', 'urls': {}}
                if url_index not in submitted_authors_data[author_index]['urls']:
                     submitted_authors_data[author_index]['urls'][url_index] = {'id': None, 'url': '', 'description': '', 'delete': False}

                if field == 'id':
                     submitted_authors_data[author_index]['urls'][url_index]['id'] = int(value_list[0]) if value_list[0].isdigit() else None
                elif field == 'url':
                     submitted_authors_data[author_index]['urls'][url_index]['url'] = value_list[0]
                elif field == 'description':
                     submitted_authors_data[author_index]['urls'][url_index]['description'] = value_list[0]
                elif field == 'delete':
                     submitted_authors_data[author_index]['urls'][url_index]['delete'] = True # 如果delete_author_url-XX存在，其值不重要，標記為True
                continue

        # 將提交的作者數據字典轉換為列表，並過濾掉被標記刪除的 URL
        processed_submitted_authors_list = []
        for author_index in sorted(submitted_authors_data.keys()):
            author_data = submitted_authors_data[author_index]
            author_name = author_data['name'].strip()
            author_id = author_data['id']

            # 檢查作者是否被標記為刪除
            delete_author = f'delete_author-{author_id}' in request.form if author_id is not None else False

            if author_name and not delete_author: # 只處理有名字且未被標記刪除的作者
                 # 收集要保留的作者 ID
                 if author_id is not None:
                      submitted_author_ids_to_keep.append(author_id)

                 urls_list = []
                 for url_index in sorted(author_data['urls'].keys()):
                      url_entry = author_data['urls'][url_index]
                      # 只添加網址不為空且未被標記刪除的URL
                      if url_entry['url'].strip() and not url_entry['delete']:
                           urls_list.append({'id': url_entry['id'], 'url': url_entry['url'].strip(), 'description': url_entry['description'].strip()})

                 processed_submitted_authors_list.append({'id': author_id, 'name': author_name, 'urls': urls_list})

        # --- 開始處理作者的刪除 ---
        # 刪除在資料庫中存在但未在提交數據中（且未被標記刪除）的作者關聯
        # 這裡我們遍歷現有作者，如果它的 ID 不在 submitted_author_ids_to_keep 中，則解除關聯
        authors_to_remove_association = []
        for existing_author in book.authors:
             if existing_author.id not in submitted_author_ids_to_keep:
                  authors_to_remove_association.append(existing_author)

        for author_to_remove in authors_to_remove_association:
             book.authors.remove(author_to_remove)
             # 注意：這裡我們只解除書籍與作者的關聯，不刪除作者本身，因為同一個作者可能屬於多本書。
             # 如果需要刪除不再關聯任何書籍的作者，需要額外的邏輯來檢查。這裡暫不實現此複雜邏輯。
             # 但是，如果作者被明確標記為刪除（通過 checkbox），我們應該刪除該作者的 URL
             if f'delete_author-{author_to_remove.id}' in request.form:
                  for url_obj in author_to_remove.urls:
                       db.session.delete(url_obj)


        # --- 開始處理作者的更新或新增以及其 URL ---
        # 這裡我們根據 processed_submitted_authors_list 來新增或更新作者，並處理其 URL

        # 創建一個新的列表來存放要與書籍關聯的作者
        updated_book_authors = []

        for author_data in processed_submitted_authors_list:
            author_id = author_data['id']
            author_name = author_data['name']
            author_urls = author_data['urls']

            if author_id is not None:
                # 更新現有作者
                author = existing_authors_map.get(author_id)
                if author: # 確保作者存在於資料庫中
                    author.name = author_name # 可以在這裡選擇是否允許編輯作者姓名
                else:
                     # 如果找不到現有作者 (可能已被手動刪除)，則視為新增
                     author = Author(name=author_name)
                     db.session.add(author)
            else:
                # 新增作者
                # 檢查是否已存在同名作者
                author = Author.query.filter_by(name=author_name).first()
                if not author:
                     author = Author(name=author_name)
                     db.session.add(author)

            # 將作者添加到更新列表 (避免重複添加)
            if author not in updated_book_authors:
                 updated_book_authors.append(author)

            # --- 開始處理此作者相關網站的更新、新增和刪除 ---

            # 獲取此作者目前已有的 URL ID 列表 (在本次請求處理開始時的狀態)
            # 注意：這裡需要使用 author.urls 而不是 book.urls，因為我們要處理的是特定作者的 URL
            existing_author_current_url_ids = [url_obj.id for url_obj in author.urls]
            # 獲取提交數據中此作者的 URL ID 列表 (已經過濾掉刪除的)
            submitted_author_url_ids = [url_entry['id'] for url_entry in author_urls]

            # 刪除不再提交的 URL
            urls_to_remove_from_author = []
            # 遍歷作者當前關聯的 URL
            for existing_url in author.urls:
                 # 如果這個 URL 的 ID 不在提交的 URL ID 列表中，且這個 URL 的作者 ID 與當前作者匹配
                 # 並且這個 URL 在全局 existing_author_urls_map 中存在 (確保不是在本次請求中新增後又刪除的)
                 if existing_url.id is not None and existing_url.id not in submitted_author_url_ids and existing_url.author_id == author.id:
                      urls_to_remove_from_author.append(existing_url)
            
            for url_to_remove in urls_to_remove_from_author:
                 db.session.delete(url_to_remove)
                 # 從作者的 urls 關聯中移除 (SQLAlchemy 通常會自動處理，但明確寫出更安全)
                 if url_to_remove in author.urls:
                      author.urls.remove(url_to_remove)

            # 更新或新增 URL
            for url_entry in author_urls:
                url_id = url_entry['id']
                url_str = url_entry['url']
                description = url_entry['description']

                if url_str.strip(): # 只處理非空的網址
                    if url_id is not None:
                        # 更新現有 URL
                        # 從原始映射中獲取 URL 物件
                        url_obj = existing_author_urls_map.get(url_id)
                        if url_obj: # 確保 URL 存在於原始資料中 (且未在前面被刪除)
                             # 再次檢查是否已被標記刪除（作者層級的URL刪除已處理）或是在全局刪除列表中
                             # 這裡主要處理未被標記刪除的 URL 的更新
                             if url_obj.author_id == author.id: # 確保 URL 確實屬於當前作者
                                  url_obj.url = url_str
                                  url_obj.description = description
                             # else: 如果 URL 存在但作者ID不匹配，說明數據有問題或邏輯需要調整，暫不處理

                        else:
                             # 如果找不到現有 URL (可能已被手動刪除，或不屬於這個作者，或新的帶ID的URL)，則視為新增
                             # 在這裡，帶有ID但找不到對應物件的情況，我們也視為新增，但這可能導致重複，需要謹慎。
                             # 更安全的做法是：如果帶ID但找不到物件，說明數據有問題，可以忽略或報錯。
                             # 暫時按照新增處理，如果前端發送了帶無效ID的URL數據。
                             url_obj = URL(
                                url=url_str,
                                description=description,
                                type='author',
                                author=author
                            )
                             db.session.add(url_obj)

                    else:
                        # 新增 URL (沒有ID的都是新增)
                        url_obj = URL(
                            url=url_str,
                            description=description,
                            type='author',
                            author=author
                        )
                        db.session.add(url_obj)
                    
                    # 將 URL 添加到作者的 urls 關聯 (避免重複添加)
                    # 注意：SQLAlchemy 通常會通過 url_obj.author = author 自動建立關聯
                    # 這裡的 append 主要是為了確保在當前會話中關聯關係的同步，但可能不是必須的
                    # if url_obj not in author.urls: # 這個檢查可能無效，因為 author.urls 可能還未更新
                    #      author.urls.append(url_obj)
                    pass # 依賴 url_obj.author = author 建立關聯

            # --- 此作者相關網站處理結束 ---

        # 更新書籍的作者關聯為處理後的列表
        book.authors = updated_book_authors

        # --- 作者處理結束 ---

        # --- 開始處理提交的新增書籍 URL ---
        # 從 request.form 中獲取新增的書籍 URL 數據
        new_book_urls = request.form.getlist('new_url[]')
        new_book_descriptions = request.form.getlist('new_url_description[]')

        # 將獲取的數據轉換為 submitted_new_book_urls_data 結構
        submitted_new_book_urls_data = []
        for i in range(len(new_book_urls)):
            url_str = new_book_urls[i].strip()
            description_str = new_book_descriptions[i].strip() if i < len(new_book_descriptions) else ''
            if url_str:
                submitted_new_book_urls_data.append({'url': url_str, 'description': description_str})
        # --- 處理提交的新增書籍 URL 結束 ---

        # --- 開始處理現有書籍 URL 的更新和刪除 ---
        # 獲取提交的現有書籍 URL ID 列表
        submitted_existing_book_url_ids = request.form.getlist('existing_book_url_id[]')

        # 遍歷現有書籍 URL，判斷是否需要刪除或更新
        existing_book_urls_to_keep = []
        urls_to_remove_from_book = []

        for url_id_str in submitted_existing_book_url_ids:
            url_id = int(url_id_str)
            # 檢查是否明確標記為刪除
            is_marked_for_deletion = f'delete_url-{url_id_str}' in request.form

            # 根據 ID 獲取 URL 物件
            url_obj = URL.query.get(url_id)

            if url_obj and url_obj.book_id == book.id: # 確保 URL 存在且屬於當前書籍
                if is_marked_for_deletion:
                    # 如果標記為刪除，添加到待刪除列表
                    urls_to_remove_from_book.append(url_obj)
                else:
                    # 如果未標記為刪除，更新其信息並添加到保留列表
                    # 注意：這裡只處理刪除，更新邏輯需要另外實現或確認現有邏輯是否足夠
                    # 目前 edit.html 中現有 URL 的 input 名稱是 url-{{ url_obj.id }} 和 description-{{ url_obj.id }}
                    # 後端會自動根據這些名稱更新對應的 URL 物件，所以這裡只需要處理刪除
                    existing_book_urls_to_keep.append(url_obj)

        # 執行刪除操作
        for url_to_remove in urls_to_remove_from_book:
            db.session.delete(url_to_remove)

        # 清空舊的書籍 URL (type='book') 關聯後重新添加保留的 URL，確保數據庫同步
        # 過濾掉已經標記為刪除的書籍 URL
        # Note: SQLAlchemy will automatically remove deleted objects from the relationship upon commit
        # However, explicitly managing the list can make logic clearer or handle specific cases.
        # Given the previous logic was trying to manage the list, let's adapt it.
        # We need to ensure book.urls only contains non-book URLs and the ones we decided to keep.
        
        # Get all current URLs associated with the book, excluding those marked for deletion
        # and those with type != 'book'
        updated_book_urls_list = [url_obj for url_obj in book.urls if url_obj.type != 'book' and url_obj not in urls_to_remove_from_book] + existing_book_urls_to_keep
        
        # Assign the updated list to book.urls relationship. SQLAlchemy handles the diff.
        book.urls = updated_book_urls_list

        # --- 處理現有書籍 URL 的更新和刪除結束 ---


        # 新增書籍 URL
        for url_entry in submitted_new_book_urls_data:
            url_str = url_entry['url']
            description = url_entry['description']
            if url_str.strip():
                 url_obj = URL(
                    url=url_str,
                    description=description,
                    type='book',
                    book=book
                 )
                 db.session.add(url_obj)
                 # 將新創建的 URL 物件添加到書籍的 urls 關聯中
                 book.urls.append(url_obj)

        # --- 書籍相關網站處理結束 ---


        # 處理題材
        # 先移除所有現有題材關聯
        book.categories = []
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
                # 將題材關聯到書籍 (避免重複添加)
                if category not in book.categories:
                    book.categories.append(category)
        
        # 處理標籤
        # 先移除所有現有標籤關聯
        book.tags = []
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
                # 將標籤關聯到書籍 (避免重複添加)
                if tag not in book.tags:
                     book.tags.append(tag)
        
        db.session.commit()
        flash('書籍資訊及相關網站已更新！', 'success')
        return redirect(url_for('book.book_detail', id=id))
    
    categories = Category.query.all()
    tags = Tag.query.all()

    # 將 book 物件及其關聯的作者和 URL 轉換為字典以便 JSON 序列化
    book_data = {
        'id': book.id,
        'title': book.title,
        'description': book.description,
        'reading_status': book.reading_status,
        'rating': book.rating,
        'authors': [],
        'urls': [],
        'categories': book.categories,
        'tags': book.tags
    }

    # 獲取所有作者及其 URL，以便構建前端所需的結構
    # 注意：這裡我們需要獲取所有與這本書籍關聯的 URL，並區分是作者的還是書籍本身的
    
    # 處理作者及其 URL
    for author in book.authors:
        author_data = {
            'id': author.id,
            'name': author.name,
            'urls': []
        }
        # 過濾出屬於此作者的 URL
        author_urls = [url for url in book.urls if url.author_id == author.id]
        for url_obj in author_urls:
             author_data['urls'].append({
                 'id': url_obj.id,
                 'url': url_obj.url,
                 'description': url_obj.description,
                 'type': url_obj.type # 包含 type 資訊
             })
        book_data['authors'].append(author_data)

    # 處理書籍本身的 URL (type 為 'book')
    book_only_urls = [url for url in book.urls if url.type == 'book']
    for url_obj in book_only_urls:
         book_data['urls'].append({
             'id': url_obj.id,
             'url': url_obj.url,
             'description': url_obj.description,
             'type': url_obj.type # 包含 type 資訊
         })

    # 傳遞字典化的書籍數據到模板
    return render_template('book/edit.html', book=book_data, categories=categories, tags=tags)

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

# 新增題材 (AJAX)
@bp.route('/book/add_category_ajax', methods=['POST'])
def add_category_ajax():
    name = request.form.get('name')
    if not name:
        return jsonify({'success': False, 'message': '名稱不能為空'}), 400

    category = Category.query.filter_by(name=name.strip()).first()
    if category:
        return jsonify({'success': True, 'id': category.id, 'name': category.name, 'message': '題材已存在，已選取'}), 200

    try:
        new_category = Category(name=name.strip())
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'success': True, 'id': new_category.id, 'name': new_category.name, 'message': '題材已成功新增'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'新增題材失敗: {e}'}), 500

# 新增標籤 (AJAX)
@bp.route('/book/add_tag_ajax', methods=['POST'])
def add_tag_ajax():
    name = request.form.get('name')
    if not name:
        return jsonify({'success': False, 'message': '名稱不能為空'}), 400

    tag = Tag.query.filter_by(name=name.strip()).first()
    if tag:
        return jsonify({'success': True, 'id': tag.id, 'name': tag.name, 'message': '標籤已存在，已選取'}), 200

    try:
        new_tag = Tag(name=name.strip())
        db.session.add(new_tag)
        db.session.commit()
        return jsonify({'success': True, 'id': new_tag.id, 'name': new_tag.name, 'message': '標籤已成功新增'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'新增標籤失敗: {e}'}), 500 