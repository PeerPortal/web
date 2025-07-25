#!/usr/bin/env python3
"""
通过插入操作获取表结构信息
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def discover_table_structure(table_name: str):
    """通过尝试插入来发现表结构"""
    base_url = os.getenv('SUPABASE_URL')
    api_key = os.getenv('SUPABASE_KEY')
    
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    print(f"\n🔍 探测 {table_name} 表结构:")
    
    # 尝试插入最少字段
    test_data = {"title": "test_structure"}
    
    url = f"{base_url}/rest/v1/{table_name}"
    
    try:
        response = requests.post(url, headers=headers, json=test_data)
        print(f"  插入测试状态: {response.status_code}")
        
        if response.status_code == 201:
            # 插入成功，获取数据然后删除
            result = response.json()
            if result:
                print(f"  成功! 字段: {list(result[0].keys())}")
                # 删除试测数据
                item_id = result[0].get('id')
                if item_id:
                    delete_response = requests.delete(f"{url}?id=eq.{item_id}", headers=headers)
                    print(f"  清理测试数据: {delete_response.status_code}")
                return result[0]
        else:
            error_info = response.json() if response.content else response.text
            print(f"  错误信息: {error_info}")
            
            # 分析错误信息来推测字段
            if isinstance(error_info, dict) and 'message' in error_info:
                message = error_info['message']
                if 'violates not-null constraint' in message:
                    # 提取必需字段
                    import re
                    match = re.search(r'column "([^"]+)"', message)
                    if match:
                        required_field = match.group(1)
                        print(f"  发现必需字段: {required_field}")
                        
                        # 尝试包含该字段再次插入
                        if required_field not in test_data:
                            test_data[required_field] = "test_value"
                            response2 = requests.post(url, headers=headers, json=test_data)
                            print(f"  二次测试状态: {response2.status_code}")
                            
                            if response2.status_code == 201:
                                result = response2.json()
                                if result:
                                    print(f"  成功! 字段: {list(result[0].keys())}")
                                    # 删除测试数据
                                    item_id = result[0].get('id')
                                    if item_id:
                                        delete_response = requests.delete(f"{url}?id=eq.{item_id}", headers=headers)
                                        print(f"  清理测试数据: {delete_response.status_code}")
                                    return result[0]
    except Exception as e:
        print(f"  异常: {str(e)}")
    
    return None

def main():
    print("🕵️ 表结构探测工具")
    print("=" * 50)
    
    tables = ['mentorship_relationships', 'services']
    
    for table in tables:
        structure = discover_table_structure(table)
        if structure:
            print(f"  ✅ {table} 结构已确定")
        else:
            print(f"  ❌ {table} 结构探测失败")

if __name__ == "__main__":
    main()
