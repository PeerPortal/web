#!/usr/bin/env python3
"""
用户登录测试脚本
测试登录功能和JWT token验证
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_login_valid_user():
    """测试有效用户登录"""
    print("🧪 测试 1: 有效用户登录")
    print("-" * 30)
    
    login_data = {
        "username": "frederick",
        "password": "123456"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功!")
            print(f"Token类型: {data['token_type']}")
            print(f"访问令牌: {data['access_token'][:30]}...")
            
            # 返回token用于后续测试
            return data['access_token']
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_login_invalid_user():
    """测试无效用户登录"""
    print("\n🧪 测试 2: 无效用户登录")
    print("-" * 30)
    
    login_data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ 正确拒绝了无效登录")
        else:
            print(f"⚠️  意外的响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_login_wrong_password():
    """测试错误密码"""
    print("\n🧪 测试 3: 正确用户名，错误密码")
    print("-" * 30)
    
    login_data = {
        "username": "frederick",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ 正确拒绝了错误密码")
        else:
            print(f"⚠️  意外的响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_protected_endpoint(token):
    """测试受保护的API端点"""
    if not token:
        print("\n❌ 跳过受保护端点测试（没有有效token）")
        return
        
    print("\n🔐 测试 4: 受保护API端点访问")
    print("-" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 测试获取用户资料
        response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功访问受保护端点")
            print(f"用户名: {data.get('username')}")
            print(f"邮箱: {data.get('email')}")
            print(f"注册时间: {data.get('created_at', '')[:10]}")
        else:
            print(f"❌ 访问失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_invalid_token():
    """测试无效token"""
    print("\n🚫 测试 5: 无效Token访问")
    print("-" * 30)
    
    headers = {
        "Authorization": "Bearer invalid_token_here",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ 正确拒绝了无效token")
        else:
            print(f"⚠️  意外的响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_update_profile(token):
    """测试更新用户资料"""
    if not token:
        print("\n❌ 跳过资料更新测试（没有有效token）")
        return
        
    print("\n📝 测试 6: 更新用户资料")
    print("-" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    profile_data = {
        "full_name": "Frederick Zhang",
        "bio": "后端开发工程师",
        "location": "北京",
        "website": "https://github.com/frederick"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/v1/users/me", 
            headers=headers,
            json=profile_data
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 资料更新成功")
            print(f"姓名: {data.get('full_name')}")
            print(f"简介: {data.get('bio')}")
            print(f"位置: {data.get('location')}")
        else:
            print(f"❌ 更新失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def check_server_status():
    """检查服务器状态"""
    print("🏥 检查服务器状态")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器运行正常")
            print(f"状态: {data.get('status')}")
            print(f"版本: {data.get('version')}")
            print(f"调试模式: {data.get('debug')}")
            return True
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("💡 请确保运行: python start_new_app.py")
        return False

def main():
    """主测试函数"""
    print("🚀 用户登录功能测试套件")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"服务器地址: {BASE_URL}")
    print()
    
    # 检查服务器状态
    if not check_server_status():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # 执行登录测试
    token = test_login_valid_user()
    test_login_invalid_user()
    test_login_wrong_password()
    test_protected_endpoint(token)
    test_invalid_token()
    test_update_profile(token)
    
    print("\n" + "=" * 50)
    print("🎉 登录测试完成!")
    
    if token:
        print(f"\n💡 当前有效的JWT Token:")
        print(f"Bearer {token}")
        print(f"\n🔧 可以用这个token测试其他API:")
        print(f"curl -H 'Authorization: Bearer {token}' {BASE_URL}/api/v1/users/me")

if __name__ == "__main__":
    main() 