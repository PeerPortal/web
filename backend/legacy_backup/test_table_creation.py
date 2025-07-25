import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase
from datetime import datetime

def test_create_user():
    """测试创建用户"""
    try:
        # 创建测试用户
        test_user = {
            "username": f"test_user_{int(datetime.now().timestamp())}",
            "password_hash": "test_hash_123"
        }
        
        response = supabase.table("users").insert(test_user).execute()
        print("✅ 用户创建成功:", response.data)
        return response.data[0] if response.data else None
        
    except Exception as e:
        print("❌ 用户创建失败:", e)
        return None

def test_get_users():
    """测试获取用户列表"""
    try:
        response = supabase.table("users").select("*").limit(5).execute()
        print("✅ 用户查询成功，获取到", len(response.data), "条记录")
        for user in response.data:
            print(f"  - 用户ID: {user['id']}, 用户名: {user['username']}")
        return response.data
        
    except Exception as e:
        print("❌ 用户查询失败:", e)
        return []

def test_create_message():
    """测试创建消息"""
    try:
        # 首先获取一些用户作为发送者和接收者
        users = test_get_users()
        if len(users) < 2:
            print("⚠️  需要至少2个用户才能测试消息功能")
            return None
            
        test_message = {
            "sender_id": users[0]["id"],
            "receiver_id": users[1]["id"],
            "content": f"测试消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = supabase.table("messages").insert(test_message).execute()
        print("✅ 消息创建成功:", response.data)
        return response.data[0] if response.data else None
        
    except Exception as e:
        print("❌ 消息创建失败:", e)
        return None

def test_get_messages():
    """测试获取消息列表"""
    try:
        response = supabase.table("messages").select("*").limit(5).execute()
        print("✅ 消息查询成功，获取到", len(response.data), "条记录")
        for msg in response.data:
            print(f"  - 消息ID: {msg['id']}, 发送者: {msg['sender_id']}, 内容: {msg['content'][:30]}...")
        return response.data
        
    except Exception as e:
        print("❌ 消息查询失败:", e)
        return []

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始数据库表操作测试...")
    print("=" * 50)
    
    # 测试用户相关操作
    print("\n📝 测试用户表操作:")
    test_create_user()
    test_get_users()
    
    # 测试消息相关操作
    print("\n📩 测试消息表操作:")
    test_create_message()
    test_get_messages()
    
    print("\n✨ 测试完成!")

if __name__ == "__main__":
    run_all_tests() 