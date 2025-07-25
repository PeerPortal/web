"""
测试新的 API 架构
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from time import sleep
import asyncio

BASE_URL = "http://localhost:8001"  # 使用不同端口避免冲突


def test_health_check():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查连接失败: {e}")
        return False


def test_root_endpoint():
    """测试根路径"""
    print("🌐 测试根路径...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 根路径访问成功: {data}")
            return True
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 根路径连接失败: {e}")
        return False


def test_register_new_user():
    """测试新的用户注册接口"""
    print("📝 测试新的用户注册接口...")
    
    try:
        # 生成唯一用户名
        import time
        import random
        timestamp = int(time.time() * 1000)
        random_num = random.randint(1000, 9999)
        
        test_user = {
            "username": f"test_new_user_{timestamp}_{random_num}",
            "email": f"test_{timestamp}@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            user_data = response.json()
            print(f"✅ 用户注册成功: {user_data['username']}")
            return test_user, user_data
        else:
            print(f"❌ 用户注册失败: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ 注册接口测试失败: {e}")
        return None, None


def test_login_new_user(test_user):
    """测试新的用户登录接口"""
    if not test_user:
        print("⚠️  跳过登录测试（没有有效用户）")
        return None
        
    print("🔐 测试新的用户登录接口...")
    
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 用户登录成功: {token_data['token_type']}")
            return token_data["access_token"]
        else:
            print(f"❌ 用户登录失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 登录接口测试失败: {e}")
        return None


def test_user_profile_endpoints(token):
    """测试用户资料相关接口"""
    if not token:
        print("⚠️  跳过用户资料测试（没有有效令牌）")
        return
        
    print("👤 测试用户资料接口...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 测试获取当前用户资料
        response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            print(f"✅ 获取用户资料成功: {profile_data.get('username')}")
        else:
            print(f"❌ 获取用户资料失败: {response.status_code}")
            return
        
        # 测试更新用户资料
        update_data = {
            "full_name": "测试用户",
            "bio": "这是一个测试用户的简介"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/v1/users/me",
            json=update_data,
            headers={**headers, "Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            updated_profile = response.json()
            print(f"✅ 更新用户资料成功: {updated_profile.get('full_name')}")
        else:
            print(f"❌ 更新用户资料失败: {response.status_code} - {response.text}")
        
        # 测试获取基本用户信息
        response = requests.get(f"{BASE_URL}/api/v1/users/me/basic", headers=headers)
        if response.status_code == 200:
            basic_data = response.json()
            print(f"✅ 获取基本信息成功: {basic_data.get('username')}")
        else:
            print(f"❌ 获取基本信息失败: {response.status_code}")
        
    except Exception as e:
        print(f"❌ 用户资料接口测试失败: {e}")


def test_api_docs():
    """测试API文档"""
    print("📚 测试API文档...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API文档访问成功")
            return True
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False


def run_all_new_api_tests():
    """运行所有新API测试"""
    print("🚀 开始新API架构测试...")
    print("=" * 60)
    
    # 检查服务器是否运行
    if not test_health_check():
        print("\n❌ 服务器未运行，请先启动新的应用:")
        print("cd app && python main.py")
        return False
    
    # 测试基础端点
    test_root_endpoint()
    test_api_docs()
    
    # 测试认证流程
    test_user, user_data = test_register_new_user()
    token = test_login_new_user(test_user)
    
    # 测试用户资料功能
    test_user_profile_endpoints(token)
    
    print("\n" + "=" * 60)
    print("✨ 新API架构测试完成!")
    return True


if __name__ == "__main__":
    run_all_new_api_tests() 