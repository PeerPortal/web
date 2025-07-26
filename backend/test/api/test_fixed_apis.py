#!/usr/bin/env python3
"""
验证修复后的API测试
"""
import asyncio
import httpx
import time
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8001"
TEST_TIMEOUT = 30

async def test_fixed_apis():
    """测试修复后的API"""
    print("🧪 开始测试修复后的API...")
    
    # 生成唯一测试数据
    timestamp = int(time.time())
    
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        results = {}
        
        # 1. 健康检查
        try:
            response = await client.get(f"{BASE_URL}/health")
            results["health_check"] = {
                "status": "✅ PASS" if response.status_code == 200 else "❌ FAIL",
                "status_code": response.status_code
            }
        except Exception as e:
            results["health_check"] = {"status": "❌ FAIL", "error": str(e)}
        
        # 2. 注册学生用户  
        student_data = {
            "username": f"test_student_{timestamp}",
            "email": f"student_{timestamp}@test.edu",
            "password": "testpass123",
            "role": "student"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=student_data)
            if response.status_code == 201:
                results["student_register"] = {"status": "✅ PASS", "user_id": response.json().get("id")}
            else:
                results["student_register"] = {"status": "❌ FAIL", "status_code": response.status_code, "detail": response.text}
        except Exception as e:
            results["student_register"] = {"status": "❌ FAIL", "error": str(e)}
        
        # 3. 学生登录
        login_data = {"username": student_data["username"], "password": student_data["password"]}
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                student_token = response.json().get("access_token")
                results["student_login"] = {"status": "✅ PASS", "has_token": bool(student_token)}
            else:
                results["student_login"] = {"status": "❌ FAIL", "status_code": response.status_code}
                student_token = None
        except Exception as e:
            results["student_login"] = {"status": "❌ FAIL", "error": str(e)}
            student_token = None
        
        # 4. 注册导师用户
        mentor_data = {
            "username": f"test_mentor_{timestamp}",
            "email": f"mentor_{timestamp}@stanford.edu",
            "password": "testpass123",
            "role": "mentor"
        }
        
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/register", json=mentor_data)
            if response.status_code == 201:
                results["mentor_register"] = {"status": "✅ PASS", "user_id": response.json().get("id")}
            else:
                results["mentor_register"] = {"status": "❌ FAIL", "status_code": response.status_code}
        except Exception as e:
            results["mentor_register"] = {"status": "❌ FAIL", "error": str(e)}
        
        # 5. 导师登录
        mentor_login_data = {"username": mentor_data["username"], "password": mentor_data["password"]}
        try:
            response = await client.post(f"{BASE_URL}/api/v1/auth/login", json=mentor_login_data)
            if response.status_code == 200:
                mentor_token = response.json().get("access_token")
                results["mentor_login"] = {"status": "✅ PASS", "has_token": bool(mentor_token)}
            else:
                results["mentor_login"] = {"status": "❌ FAIL", "status_code": response.status_code}
                mentor_token = None
        except Exception as e:
            results["mentor_login"] = {"status": "❌ FAIL", "error": str(e)}
            mentor_token = None
        
        # 6. 创建导师资料 (使用新的Schema)
        if mentor_token:
            mentor_profile_data = {
                "title": "斯坦福 计算机科学 导师",
                "description": "我是一名软件开发工程师，希望帮助学弟学妹",
                "learning_goals": "专业: 计算机科学, 特长: 编程, 算法, 系统设计",
                "hourly_rate": 100.0,
                "session_duration_minutes": 60
            }
            
            headers = {"Authorization": f"Bearer {mentor_token}"}
            try:
                response = await client.post(f"{BASE_URL}/api/v1/mentors/profile", json=mentor_profile_data, headers=headers)
                if response.status_code in [200, 201]:
                    results["mentor_profile_create"] = {"status": "✅ PASS"}
                else:
                    results["mentor_profile_create"] = {"status": "❌ FAIL", "status_code": response.status_code, "detail": response.text}
            except Exception as e:
                results["mentor_profile_create"] = {"status": "❌ FAIL", "error": str(e)}
        else:
            results["mentor_profile_create"] = {"status": "⏭️ SKIP", "reason": "No mentor token"}
        
        # 7. 创建学生资料 (使用新的Schema)
        if student_token:
            student_profile_data = {
                "urgency_level": 2,
                "budget_min": 50.0,
                "budget_max": 200.0,
                "description": "申请master学位",
                "learning_goals": "目标学校: MIT, Stanford, CMU",
                "preferred_format": "online"
            }
            
            headers = {"Authorization": f"Bearer {student_token}"}
            try:
                response = await client.post(f"{BASE_URL}/api/v1/students/profile", json=student_profile_data, headers=headers)
                if response.status_code in [200, 201]:
                    results["student_profile_create"] = {"status": "✅ PASS"}
                else:
                    results["student_profile_create"] = {"status": "❌ FAIL", "status_code": response.status_code, "detail": response.text}
            except Exception as e:
                results["student_profile_create"] = {"status": "❌ FAIL", "error": str(e)}
        else:
            results["student_profile_create"] = {"status": "⏭️ SKIP", "reason": "No student token"}
        
        # 8. 创建服务 (使用新的Schema)
        if mentor_token:
            service_data = {
                "title": "留学申请全程指导",
                "description": "提供从选校到申请的全程指导服务",
                "category": "consultation",
                "price": 150,  # 整数类型
                "duration_hours": 2
            }
            
            headers = {"Authorization": f"Bearer {mentor_token}"}
            try:
                response = await client.post(f"{BASE_URL}/api/v1/services", json=service_data, headers=headers)
                if response.status_code in [200, 201]:
                    results["service_create"] = {"status": "✅ PASS"}
                else:
                    results["service_create"] = {"status": "❌ FAIL", "status_code": response.status_code, "detail": response.text}
            except Exception as e:
                results["service_create"] = {"status": "❌ FAIL", "error": str(e)}
        else:
            results["service_create"] = {"status": "⏭️ SKIP", "reason": "No mentor token"}
        
        # 9. 搜索服务
        try:
            response = await client.get(f"{BASE_URL}/api/v1/services")
            if response.status_code == 200:
                services = response.json()
                results["service_search"] = {"status": "✅ PASS", "count": len(services)}
            else:
                results["service_search"] = {"status": "❌ FAIL", "status_code": response.status_code}
        except Exception as e:
            results["service_search"] = {"status": "❌ FAIL", "error": str(e)}
    
    # 输出测试结果
    print("\n📊 测试结果汇总:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = result.get("status", "❓ UNKNOWN")
        print(f"{test_name:<25} | {status}")
        
        if result.get("status_code"):
            print(f"{'':<25} | 状态码: {result['status_code']}")
        if result.get("error"):
            print(f"{'':<25} | 错误: {result['error']}")
        if result.get("detail") and "FAIL" in status:
            print(f"{'':<25} | 详情: {result['detail'][:100]}...")
    
    print("=" * 60)
    
    # 统计
    passed = sum(1 for r in results.values() if r.get("status", "").startswith("✅"))
    failed = sum(1 for r in results.values() if r.get("status", "").startswith("❌"))
    skipped = sum(1 for r in results.values() if r.get("status", "").startswith("⏭️"))
    
    print(f"总测试数: {len(results)}")
    print(f"通过: {passed} | 失败: {failed} | 跳过: {skipped}")
    
    if failed == 0:
        print("🎉 所有测试都通过了！修复成功！") 
    else:
        print(f"⚠️ 还有 {failed} 个测试失败，需要进一步修复")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_fixed_apis())
