#!/usr/bin/env python3
import sys
import os
from app import create_app, db
from migrations.migrate_urls import migrate_urls

def main(args):
    print("開始 BookLib URL 數據遷移...")
    
    try:
        print("開始遷移 URL 數據...")
        success = migrate_urls()
        if success:
            print("URL 數據遷移完成")
        else:
            print("URL 數據遷移失敗")
    except Exception as e:
        print(f"URL 數據遷移過程中出現錯誤：{e}")
        import traceback
        traceback.print_exc()
            
    print("遷移程序結束")

if __name__ == "__main__":
    main(sys.argv[1:]) 