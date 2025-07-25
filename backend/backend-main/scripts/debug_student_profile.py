#!/usr/bin/env python3
"""
调试学生资料创建错误的详细脚本
"""
import asyncio
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def test_create_student_profile():
    """测试创建学生资料"""
    
    # 1. 注册学生
    print("🔧 步骤1: 注册学生账户...")
    register_data = {
        "username": f"student_debug_{datetime.now().strftime('%H%M%S')}",
        "email": f"debug_{datetime.now().strftime('%H%M%S')}@example.com",
        "password": "testpassword123",
        "user_type": "student"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    if response.status_code not in [200, 201]:
        print(f"❌ 注册失败: {response.status_code} - {response.text}")
        return
    
    user_data = response.json()
    user_id = user_data["id"]  # 修正字段路径
    print(f"✅ 注册成功，用户ID: {user_id}")
    
    # 2. 登录获取token
    print("🔧 步骤2: 登录获取token...")
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return
    
    login_result = response.json()
    token = login_result["access_token"]
    print(f"✅ 登录成功，获取到token")
    
    # 3. 创建学生资料
    print("🔧 步骤3: 创建学生资料...")
    headers = {"Authorization": f"Bearer {token}"}
    profile_data = {
        "urgency_level": 2,
        "budget_min": 100,
        "budget_max": 500,
        "description": "需要雅思口语指导",
        "learning_goals": "提升雅思口语到7分",
        "preferred_format": "online"
    }
    
    print(f"📤 发送数据: {json.dumps(profile_data, ensure_ascii=False, indent=2)}")
    print(f"📤 请求头: {headers}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/students/profile", 
        json=profile_data, 
        headers=headers
    )
    
    print(f"📥 响应状态码: {response.status_code}")
    print(f"📥 响应头: {dict(response.headers)}")
    print(f"📥 响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 学生资料创建成功!")
        print(f"📋 资料详情: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ 学生资料创建失败: {response.status_code}")
        print(f"💥 错误详情: {response.text}")

if __name__ == "__main__":
    test_create_student_profile()
