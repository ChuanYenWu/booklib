from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from .models import db

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 註冊藍圖
    from .routes import main
    app.register_blueprint(main)
    
    return app 