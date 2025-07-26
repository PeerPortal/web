#!/usr/bin/env python3
"""
获取有数据表的字段结构
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_table_fields(table_name: str):
    """获取表的实际字段"""
    base_url = os.getenv('SUPABASE_URL')
    api_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"{base_url}/rest/v1/{table_name}?limit=1"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"\n📋 {table_name} 表字段:")
                fields = list(data[0].keys())
                for i, field in enumerate(fields, 1):
                    value = data[0][field]
                    print(f"  {i:2d}. {field:25} = {value}")
                print(f"\n总字段数: {len(fields)}")
                return fields
            else:
                print(f"\n📋 {table_name} 表无数据")
        else:
            print(f"\n📋 {table_name} 表查询失败: {response.status_code}")
            if response.content:
                print(f"  错误: {response.json()}")
    except Exception as e:
        print(f"\n📋 {table_name} 表查询异常: {str(e)}")
    
    return []

def main():
    print("🔍 获取关键表的字段结构")
    print("=" * 60)
    
    # 有数据的表
    tables_with_data = [
        'user_learning_needs',
        'users',
        'profiles', 
        'skill_categories',
        'skills'
    ]
    
    # 空表但需要了解结构的
    empty_tables = [
        'mentorship_relationships',
        'services'
    ]
    
    for table in tables_with_data:
        get_table_fields(table)
    
    print("\n" + "=" * 60)
    print("🔍 空表结构推测 (通过错误信息):")
    
    for table in empty_tables:
        print(f"\n📋 {table} 表:")
        # 尝试插入数据获取错误信息
        base_url = os.getenv('SUPABASE_URL')
        api_key = os.getenv('SUPABASE_KEY')
        
        headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{base_url}/rest/v1/{table}"
        
        # 尝试插入一些常见字段
        test_data = {
            "title": "test",
            "description": "test",
            "user_id": 1
        }
        
        try:
            response = requests.post(url, headers=headers, json=test_data)
            if response.status_code in [400, 422]:
                error_info = response.json()
                if 'message' in error_info:
                    message = error_info['message']
                    print(f"  错误信息: {message}")
                    
                    # 如果是字段不存在错误，说明表结构不同
                    if 'Could not find' in message and 'column' in message:
                        print(f"  结构问题: 字段不匹配")
            elif response.status_code == 201:
                print(f"  插入成功，删除测试数据...")
                # 删除测试数据
                delete_response = requests.delete(f"{url}?title=eq.test", headers=headers)
                print(f"  删除状态: {delete_response.status_code}")
        except Exception as e:
            print(f"  测试异常: {str(e)}")

if __name__ == "__main__":
    main()
