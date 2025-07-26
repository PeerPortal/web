#!/usr/bin/env python3
"""
修复测试脚本 - 验证Supabase插入和角色权限问题
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_user_registration_with_roles():
    """测试用户注册时可以指定角色"""
    print("🧪 测试用户注册与角色设置")
    print("-" * 50)
    
    timestamp = int(time.time())
    
    # 测试注册student用户
    student_data = {
        "username": f"test_student_{timestamp}",
        "email": f"student_{timestamp}@test.com",
        "password": "testpass123",
        "role": "student"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=student_data)
    print(f"Student注册: {response.status_code}")
    if response.status_code == 201:
        user_data = response.json()
        print(f"  ✅ 用户ID: {user_data['id']}, 角色: {user_data.get('role', 'unknown')}")
        student_username = user_data['username']
    else:
        print(f"  ❌ 注册失败: {response.text}")
        return False
    
    # 测试注册mentor用户
    mentor_data = {
        "username": f"test_mentor_{timestamp}",
        "email": f"mentor_{timestamp}@test.com", 
        "password": "testpass123",
        "role": "mentor"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=mentor_data)
    print(f"Mentor注册: {response.status_code}")
    if response.status_code == 201:
        user_data = response.json()
        print(f"  ✅ 用户ID: {user_data['id']}, 角色: {user_data.get('role', 'unknown')}")
        mentor_username = user_data['username']
    else:
        print(f"  ❌ 注册失败: {response.text}")
        return False
    
    return student_username, mentor_username

def get_auth_token(username: str, password: str = "testpass123"):
    """获取认证token"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def test_mentor_profile_creation(mentor_username: str):
    """测试导师资料创建"""
    print("\n🧪 测试导师资料创建")
    print("-" * 50)
    
    token = get_auth_token(mentor_username)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    mentor_profile_data = {
        "university": "北京大学",
        "major": "计算机科学",
        "degree_level": "bachelor",
        "graduation_year": 2023,
        "current_status": "working",
        "bio": "我是一名软件开发工程师，希望帮助学弟学妹",
        "specialties": ["编程", "算法", "系统设计"],
        "languages": ["中文", "英文"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/mentors/profile", 
        json=mentor_profile_data,
        headers=headers
    )
    
    print(f"导师资料创建: {response.status_code}")
    if response.status_code == 200:
        profile_data = response.json()
        print(f"  ✅ 导师ID: {profile_data.get('id', 'unknown')}")
        print(f"  ✅ 大学: {profile_data.get('university', 'unknown')}")
        return True
    else:
        print(f"  ❌ 创建失败: {response.text}")
        return False

def test_student_profile_creation(student_username: str):
    """测试学生资料创建"""
    print("\n🧪 测试学生资料创建")
    print("-" * 50)
    
    token = get_auth_token(student_username)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    student_profile_data = {
        "current_education": "本科在读",
        "target_degree": "master",
        "target_universities": ["MIT", "Stanford", "CMU"],
        "target_majors": ["计算机科学", "人工智能"],
        "application_timeline": "2024年秋季入学",
        "gpa": 3.8,
        "language_scores": {
            "TOEFL": 105,
            "GRE": 320
        },
        "research_experience": "有机器学习项目经验",
        "work_experience": "实习经验",
        "preferred_countries": ["美国"],
        "budget_range": "50-100万"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/students/profile",
        json=student_profile_data,
        headers=headers
    )
    
    print(f"学生资料创建: {response.status_code}")
    if response.status_code == 200:
        profile_data = response.json()
        print(f"  ✅ 学生ID: {profile_data.get('id', 'unknown')}")
        print(f"  ✅ 目标国家: {profile_data.get('target_country', 'unknown')}")
        return True
    else:
        print(f"  ❌ 创建失败: {response.text}")
        return False

def test_service_creation(mentor_username: str):
    """测试服务发布"""
    print("\n🧪 测试服务发布")
    print("-" * 50)
    
    token = get_auth_token(mentor_username)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    service_data = {
        "title": "计算机科学申请指导",
        "description": "提供美国计算机科学研究生申请的全面指导",
        "category": "consultation", 
        "price": 299,
        "duration": 120,  # 修改为duration而不是duration_hours
        "delivery_days": 7,  # 添加必需字段
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/services",
        json=service_data,
        headers=headers
    )
    
    print(f"服务发布: {response.status_code}")
    if response.status_code == 200:
        service_data = response.json()
        print(f"  ✅ 服务ID: {service_data.get('id', 'unknown')}")
        print(f"  ✅ 服务标题: {service_data.get('title', 'unknown')}")
        return True
    else:
        print(f"  ❌ 发布失败: {response.text}")
        return False

def main():
    """主测试函数"""
    print("🔧 修复测试 - Supabase插入和角色权限")
    print("=" * 60)
    
    # 检查服务器状态
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器未运行，请先启动服务器")
            return
        print("✅ 服务器运行正常")
    except:
        print("❌ 无法连接到服务器")
        return
    
    # 测试用户注册
    result = test_user_registration_with_roles()
    if not result:
        print("❌ 用户注册测试失败")
        return
    
    student_username, mentor_username = result
    
    # 测试导师资料创建
    mentor_success = test_mentor_profile_creation(mentor_username)
    
    # 测试学生资料创建  
    student_success = test_student_profile_creation(student_username)
    
    # 测试服务发布
    service_success = test_service_creation(mentor_username)
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"✅ 用户注册: 通过")
    print(f"{'✅' if mentor_success else '❌'} 导师资料创建: {'通过' if mentor_success else '失败'}")
    print(f"{'✅' if student_success else '❌'} 学生资料创建: {'通过' if student_success else '失败'}")
    print(f"{'✅' if service_success else '❌'} 服务发布: {'通过' if service_success else '失败'}")
    
    if mentor_success and student_success and service_success:
        print("\n🎉 所有测试通过！修复成功！")
    else:
        print("\n⚠️ 部分测试仍然失败，需要进一步调试")

if __name__ == "__main__":
    main()
