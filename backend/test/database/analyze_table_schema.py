#!/usr/bin/env python3
"""
获取Supabase表结构信息
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_table_schema():
    """获取表结构信息"""
    base_url = os.getenv('SUPABASE_URL')
    api_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 使用特殊的查询来获取表结构
    tables = ['mentorship_relationships', 'user_learning_needs', 'services']
    
    for table_name in tables:
        print(f"\n🔍 表 {table_name} 结构检查:")
        
        # 方法1: 尝试插入空数据来触发字段错误
        url = f"{base_url}/rest/v1/{table_name}"
        try:
            response = requests.post(url, headers=headers, json={})
            if response.status_code in [400, 422]:
                error_info = response.json()
                print(f"  错误信息: {error_info}")
                
                # 从错误信息中提取字段信息
                if 'message' in error_info:
                    message = error_info['message']
                    if 'violates not-null constraint' in message:
                        # 提取必需字段
                        import re
                        match = re.search(r'column "([^"]+)"', message)
                        if match:
                            print(f"  必需字段: {match.group(1)}")
                    elif 'Could not find' in message and 'column' in message:
                        print(f"  表结构信息: {message}")
        except Exception as e:
            print(f"  检查异常: {str(e)}")
        
        # 方法2: 尝试查询获取响应头
        try:
            response = requests.get(f"{url}?limit=0", headers=headers)
            print(f"  查询状态: {response.status_code}")
            if 'content-range' in response.headers:
                print(f"  Content-Range: {response.headers['content-range']}")
        except Exception as e:
            print(f"  查询异常: {str(e)}")

def main():
    print("📊 Supabase 表结构分析")
    print("=" * 60)
    get_table_schema()

if __name__ == "__main__":
    main()
