from app import create_app
from app.test_data import create_test_data
import sys

app = create_app()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        with app.app_context():
            create_test_data()
            print('測試數據已創建完成！')
    else:
        app.run(debug=True) 