from flask_login import UserMixin
from datetime import datetime

# 所有模型都會用到的共用導入
from .. import db

# 導入所有模型
from .book import Book
from .author import Author
from .category import Category
from .tag import Tag
from .url import BookURL, AuthorURL

# 確保所有模型都被導入
__all__ = ['Book', 'Author', 'Category', 'Tag', 'BookURL', 'AuthorURL'] 