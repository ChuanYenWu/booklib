from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# 創建擴展實例
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 註冊藍圖
    from .routes.views import main as main_bp
    from .routes.book import bp as book_bp
    from .routes.author import bp as author_bp
    from .routes.category import bp as category_bp
    from .routes.tag import bp as tag_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(book_bp, url_prefix='/books')
    app.register_blueprint(author_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(tag_bp)
    
    # 在應用上下文中創建所有數據表
    with app.app_context():
        db.create_all()
    
    return app

# 確保其他模組可以導入 db
from . import models 