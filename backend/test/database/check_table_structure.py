#!/usr/bin/env python3
"""
数据库表结构检查脚本
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_table_structure(table_name: str):
    """检查表的字段结构"""
    base_url = os.getenv('SUPABASE_URL')
    api_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 查询表数据，获取字段信息
    url = f"{base_url}/rest/v1/{table_name}?limit=1"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"\n📋 表 {table_name}:")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"   字段: {list(data[0].keys())}")
                print(f"   示例数据: {data[0]}")
            else:
                print("   无数据，尝试查询字段...")
                # 使用OPTIONS请求获取字段信息
                headers_req = requests.options(url, headers=headers)
                print(f"   OPTIONS状态: {headers_req.status_code}")
        else:
            error_info = response.json() if response.content else response.text
            print(f"   错误: {error_info}")
            
    except Exception as e:
        print(f"   异常: {str(e)}")

def main():
    print("🔍 检查关键表结构")
    print("=" * 50)
    
    # 检查关键表
    tables_to_check = [
        'mentorship_relationships',
        'user_learning_needs', 
        'users',
        'profiles',
        'services'
    ]
    
    for table in tables_to_check:
        check_table_structure(table)
    
    print("\n" + "=" * 50)
    print("检查完成")

if __name__ == "__main__":
    main()
