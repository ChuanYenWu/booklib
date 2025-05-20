# 開發提醒事項

## 資料庫操作
1. 初始化資料庫使用 `python run.py init-db` 命令
2. 資料庫重置流程：
   - 刪除 instance/booklib.db
   - 刪除 migrations 目錄
   - 執行 flask db init
   - 執行 flask db migrate
   - 執行 flask db upgrade
   - 執行 python run.py init-db

## 模型關係注意事項
1. 在定義多對多關係時，避免重複定義 backref：
   - 如果在 Book 模型中已定義了 authors 關係
   - 則在 Author 模型中不應再使用 backref 定義相同的關係
2. **注意：** 在 `app/models/book.py` 中，與作者、題材和標籤的多對多關聯目前被註釋掉了，需要與其他模型中的定義進行核對並啟用。

## 代碼風格
1. 保持一致的註釋風格：
   - 使用中文註釋
   - 未實作的功能使用註釋標記
   - 重要的配置項添加說明註釋

## 開發流程
1. 先實作核心功能，再添加擴展功能
2. 每個功能完成後進行測試
3. 定期更新 workflow.md 追蹤進度 