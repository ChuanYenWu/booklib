import os

class Config:
    # 資料庫設定
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'booklib.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全設定
    SECRET_KEY = 'your-secret-key-here'  # 在實際應用中應該使用環境變數
    
    # 應用設定
    DEBUG = True 