#!/usr/bin/env python3
"""
调试服务创建错误的详细脚本
"""
import asyncio
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"

def test_create_service():
    """测试创建服务"""
    
    # 1. 注册导师
    print("🔧 步骤1: 注册导师账户...")
    register_data = {
        "username": f"mentor_debug_{datetime.now().strftime('%H%M%S')}",
        "email": f"mentor_debug_{datetime.now().strftime('%H%M%S')}@example.com",
        "password": "testpassword123",
        "role": "mentor"  # 使用role而不是user_type
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    if response.status_code not in [200, 201]:
        print(f"❌ 注册失败: {response.status_code} - {response.text}")
        return
    
    user_data = response.json()
    user_id = user_data["id"]
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
    
    # 3. 创建导师资料（如果需要）
    print("🔧 步骤3: 创建导师资料...")
    headers = {"Authorization": f"Bearer {token}"}
    mentor_data = {
        "title": "雅思口语专家",
        "description": "拥有10年雅思教学经验，帮助学生提升口语成绩",
        "learning_goals": "雅思口语提升到7分以上",
        "hourly_rate": 200,
        "session_duration_minutes": 60
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/mentors/profile", 
        json=mentor_data, 
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ 导师资料创建成功")
    else:
        print(f"⚠️ 导师资料创建可能失败: {response.status_code} - {response.text}")
    
    # 4. 创建服务
    print("🔧 步骤4: 创建服务...")
    service_data = {
        "title": "雅思口语1对1指导",
        "description": "专业雅思口语指导，针对性提升口语表达能力",
        "category": "语言学习",
        "price": 300,
        "duration_hours": 2
    }
    
    print(f"📤 发送数据: {json.dumps(service_data, ensure_ascii=False, indent=2)}")
    print(f"📤 请求头: {headers}")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/services", 
        json=service_data, 
        headers=headers
    )
    
    print(f"📥 响应状态码: {response.status_code}")
    print(f"📥 响应头: {dict(response.headers)}")
    print(f"📥 响应内容: {response.text}")
    
    if response.status_code == 200:
        print("✅ 服务创建成功!")
        print(f"📋 服务详情: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ 服务创建失败: {response.status_code}")
        print(f"💥 错误详情: {response.text}")

if __name__ == "__main__":
    test_create_service()
