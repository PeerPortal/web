#!/usr/bin/env python3
"""
完整的API功能验证测试
验证学生资料、导师资料和服务创建的完整流程
"""

import json
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_complete_workflow():
    """测试完整的工作流程"""
    
    # 生成时间戳以确保用户名唯一
    timestamp = str(int(time.time()))[-6:]
    
    print("🚀 开始完整的API功能验证测试...")
    print("=" * 60)
    
    # 步骤1: 测试学生流程
    print("\n📚 测试学生流程:")
    print("-" * 30)
    
    # 1.1 注册学生用户
    student_data = {
        "username": f"test_student_{timestamp}",
        "email": f"student_{timestamp}@test.edu",
        "password": "test123456",
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=student_data)
    if response.status_code == 201:
        student_user = response.json()
        print(f"✅ 学生注册成功: {student_user['username']}")
    else:
        print(f"❌ 学生注册失败: {response.status_code}")
        return False
    
    # 1.2 学生登录
    login_data = {"username": student_data["username"], "password": student_data["password"]}
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        student_tokens = response.json()
        student_headers = {"Authorization": f"Bearer {student_tokens['access_token']}"}
        print("✅ 学生登录成功")
    else:
        print(f"❌ 学生登录失败: {response.status_code}")
        return False
    
    # 1.3 创建学生资料
    student_profile_data = {
        "urgency_level": 2,
        "budget_min": 50.0,
        "budget_max": 200.0,
        "description": "申请master学位",
        "learning_goals": "目标学校: MIT, Stanford, CMU",
        "preferred_format": "online",
        "currency": "CNY",
        "current_level": 1,
        "target_level": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/students/profile", 
        json=student_profile_data, 
        headers=student_headers
    )
    if response.status_code == 200:
        student_profile = response.json()
        print("✅ 学生资料创建成功")
    else:
        print(f"❌ 学生资料创建失败: {response.status_code} - {response.text}")
        return False
    
    # 步骤2: 测试导师流程
    print("\n👨‍🏫 测试导师流程:")
    print("-" * 30)
    
    # 2.1 注册导师用户
    mentor_data = {
        "username": f"test_mentor_{timestamp}",
        "email": f"mentor_{timestamp}@stanford.edu",
        "password": "test123456",
        "role": "mentor"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=mentor_data)
    if response.status_code == 201:
        mentor_user = response.json()
        print(f"✅ 导师注册成功: {mentor_user['username']}")
    else:
        print(f"❌ 导师注册失败: {response.status_code}")
        return False
    
    # 2.2 导师登录
    login_data = {"username": mentor_data["username"], "password": mentor_data["password"]}
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code == 200:
        mentor_tokens = response.json()
        mentor_headers = {"Authorization": f"Bearer {mentor_tokens['access_token']}"}
        print("✅ 导师登录成功")
    else:
        print(f"❌ 导师登录失败: {response.status_code}")
        return False
    
    # 2.3 创建导师资料
    mentor_profile_data = {
        "bio": "斯坦福大学计算机科学博士，专业指导研究生申请",
        "location": "美国加州",
        "hourly_rate": 200.0,
        "availability": "工作日晚上，周末全天",
        "expertise_areas": ["研究生申请", "计算机科学", "学术写作"],
        "education_background": "Stanford University PhD in Computer Science",
        "years_of_experience": 5,
        "languages_spoken": ["中文", "英文"],
        "timezone": "PST"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/mentors/profile", 
        json=mentor_profile_data, 
        headers=mentor_headers
    )
    if response.status_code == 200:
        mentor_profile = response.json()
        print("✅ 导师资料创建成功")
    else:
        print(f"❌ 导师资料创建失败: {response.status_code} - {response.text}")
        return False
    
    # 2.4 创建服务
    service_data = {
        "title": "CS研究生申请指导",
        "description": "提供全面的计算机科学研究生申请指导，包括选校、文书、面试等",
        "category": "研究生申请",
        "price": 300,
        "duration_hours": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/services", 
        json=service_data, 
        headers=mentor_headers
    )
    if response.status_code == 200:
        service = response.json()
        print("✅ 服务创建成功")
        print(f"📋 服务ID: {service['id']}")
    else:
        print(f"❌ 服务创建失败: {response.status_code} - {response.text}")
        return False
    
    # 步骤3: 测试服务浏览
    print("\n🔍 测试服务浏览:")
    print("-" * 30)
    
    response = requests.get(f"{BASE_URL}/api/v1/services")
    if response.status_code == 200:
        services = response.json()
        print(f"✅ 服务浏览成功，共找到 {len(services)} 个服务")
        if services:
            print(f"📋 最新服务: {services[-1]['title']}")
    else:
        print(f"❌ 服务浏览失败: {response.status_code}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有API测试通过！平台功能正常运行")
    print("✅ 学生注册、登录、资料创建 - 正常")
    print("✅ 导师注册、登录、资料创建 - 正常") 
    print("✅ 服务创建和浏览 - 正常")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_workflow()
        if not success:
            print("\n❌ 测试失败")
            exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中出现异常: {e}")
        exit(1)
