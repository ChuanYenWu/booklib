from app import create_app, db
from app.test_data import create_test_data
import sys
import os

app = create_app()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            # 確保 instance 目錄存在
            instance_path = os.path.join(os.path.dirname(__file__), 'instance')
            if not os.path.exists(instance_path):
                os.makedirs(instance_path)
            
            # 創建新的資料庫和表
            db.create_all()
            print('已創建資料庫表')
            
            # 添加測試數據
            create_test_data()
            print('測試數據已創建完成！')
    else:
        app.run(debug=True) 