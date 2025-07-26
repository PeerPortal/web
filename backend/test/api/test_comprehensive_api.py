#!/usr/bin/env python3
"""
启航引路人平台 - 完整API测试套件
测试所有API端点的功能性和安全性
"""
import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8001"

class ComprehensiveAPITester:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.tokens = {}  # 存储不同用户的token
        self.test_data = {}  # 存储测试过程中创建的数据
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
    
    async def setup(self):
        """初始化测试环境"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        logger.info("🚀 启动API测试套件")
        logger.info(f"📍 测试目标: {BASE_URL}")
    
    async def cleanup(self):
        """清理测试环境"""
        if self.session:
            await self.session.close()
        logger.info("🧹 测试环境已清理")
    
    def log_test(self, name: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.results['total'] += 1
        status = "✅ PASS" if success else "❌ FAIL"
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
        
        result = f"{status} | {name}"
        if details:
            result += f" | {details}"
        
        self.results['details'].append(result)
        logger.info(result)
    
    async def test_server_health(self) -> bool:
        """测试服务器健康状态"""
        logger.info("🏥 测试服务器健康状态")
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                success = response.status == 200
                if success:
                    data = await response.json()
                    self.log_test("服务器健康检查", True, f"状态: {data.get('status', 'unknown')}")
                else:
                    self.log_test("服务器健康检查", False, f"状态码: {response.status}")
                return success
        except Exception as e:
            self.log_test("服务器健康检查", False, f"连接错误: {str(e)}")
            return False
    
    async def test_basic_endpoints(self):
        """测试基础端点"""
        logger.info("📋 测试基础端点")
        
        # 测试根路径
        try:
            async with self.session.get(f"{BASE_URL}/") as response:
                success = response.status == 200
                self.log_test("根路径访问", success, f"状态码: {response.status}")
        except Exception as e:
            self.log_test("根路径访问", False, f"错误: {str(e)}")
        
        # 测试API文档
        try:
            async with self.session.get(f"{BASE_URL}/docs") as response:
                success = response.status == 200
                self.log_test("API文档访问", success, f"状态码: {response.status}")
        except Exception as e:
            self.log_test("API文档访问", False, f"错误: {str(e)}")
    
    async def test_user_registration_and_login(self):
        """测试用户注册和登录"""
        logger.info("👤 测试用户认证系统")
        
        # 生成测试用户数据
        timestamp = int(time.time())
        test_users = [
            {
                "username": f"student_{timestamp}",
                "email": f"student_{timestamp}@test.edu",
                "password": "test123456",
                "role": "student"
            },
            {
                "username": f"mentor_{timestamp}",
                "email": f"mentor_{timestamp}@stanford.edu",
                "password": "test123456",
                "role": "mentor"
            }
        ]
        
        for user_data in test_users:
            # 测试用户注册
            try:
                async with self.session.post(
                    f"{BASE_URL}/api/v1/auth/register",
                    json=user_data
                ) as response:
                    success = response.status == 201
                    if success:
                        result = await response.json()
                        self.test_data[f"{user_data['role']}_user"] = result
                        self.log_test(f"{user_data['role']}用户注册", True, f"用户ID: {result.get('id')}")
                    else:
                        error_text = await response.text()
                        self.log_test(f"{user_data['role']}用户注册", False, f"状态码: {response.status}, 错误: {error_text[:100]}")
                        continue
            except Exception as e:
                self.log_test(f"{user_data['role']}用户注册", False, f"错误: {str(e)}")
                continue
            
            # 测试用户登录
            try:
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
                async with self.session.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    success = response.status == 200
                    if success:
                        result = await response.json()
                        self.tokens[user_data['role']] = result['access_token']
                        self.log_test(f"{user_data['role']}用户登录", True, "获取token成功")
                    else:
                        error_text = await response.text()
                        self.log_test(f"{user_data['role']}用户登录", False, f"状态码: {response.status}, 错误: {error_text[:100]}")
            except Exception as e:
                self.log_test(f"{user_data['role']}用户登录", False, f"错误: {str(e)}")
    
    async def test_user_profile_operations(self):
        """测试用户资料操作"""
        logger.info("📝 测试用户资料操作")
        
        # 测试获取用户信息
        for role in ['student', 'mentor']:
            if role not in self.tokens:
                continue
                
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            
            try:
                async with self.session.get(
                    f"{BASE_URL}/api/v1/users/me",
                    headers=headers
                ) as response:
                    success = response.status == 200
                    if success:
                        user_data = await response.json()
                        self.log_test(f"获取{role}用户信息", True, f"用户名: {user_data.get('username')}")
                    else:
                        self.log_test(f"获取{role}用户信息", False, f"状态码: {response.status}")
            except Exception as e:
                self.log_test(f"获取{role}用户信息", False, f"错误: {str(e)}")
    
    async def test_mentor_operations(self):
        """测试导师相关操作"""
        if 'mentor' not in self.tokens:
            self.log_test("导师操作测试", False, "未获取到导师token，跳过测试")
            return
        
        logger.info("🎓 测试导师相关操作")
        headers = {"Authorization": f"Bearer {self.tokens['mentor']}"}
        
        # 测试创建导师资料
        mentor_profile = {
            "university": "Stanford University",
            "major": "Computer Science",
            "degree_level": "master",
            "graduation_year": 2023,
            "current_status": "graduated",
            "specialties": ["文书指导", "面试辅导"],
            "bio": "斯坦福CS硕士，专业提供留学申请指导"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/api/v1/mentors/profile",
                json=mentor_profile,
                headers=headers
            ) as response:
                success = response.status in [200, 201]
                if success:
                    result = await response.json()
                    self.test_data['mentor_profile'] = result
                    self.log_test("创建导师资料", True, f"专业: {mentor_profile['major']}")
                else:
                    error_text = await response.text()
                    self.log_test("创建导师资料", False, f"状态码: {response.status}, 错误: {error_text[:100]}")
        except Exception as e:
            self.log_test("创建导师资料", False, f"错误: {str(e)}")
    
    async def test_student_operations(self):
        """测试学生相关操作"""
        if 'student' not in self.tokens:
            self.log_test("学生操作测试", False, "未获取到学生token，跳过测试")
            return
        
        logger.info("📚 测试学生相关操作")
        headers = {"Authorization": f"Bearer {self.tokens['student']}"}
        
        # 测试创建学生资料
        student_profile = {
            "current_education": "本科大四",
            "target_degree": "master",
            "target_universities": ["Stanford University", "MIT"],
            "target_majors": ["Computer Science", "AI"],
            "application_timeline": "2024秋季申请"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/api/v1/students/profile",
                json=student_profile,
                headers=headers
            ) as response:
                success = response.status in [200, 201]
                if success:
                    result = await response.json()
                    self.test_data['student_profile'] = result
                    self.log_test("创建学生资料", True, f"目标学位: {student_profile['target_degree']}")
                else:
                    error_text = await response.text()
                    self.log_test("创建学生资料", False, f"状态码: {response.status}, 错误: {error_text[:100]}")
        except Exception as e:
            self.log_test("创建学生资料", False, f"错误: {str(e)}")
    
    async def test_service_operations(self):
        """测试服务相关操作"""
        if 'mentor' not in self.tokens:
            self.log_test("服务操作测试", False, "未获取到导师token，跳过测试")
            return
        
        logger.info("🛒 测试服务相关操作")
        headers = {"Authorization": f"Bearer {self.tokens['mentor']}"}
        
        # 测试发布服务
        service_data = {
            "title": "Stanford CS申请文书指导",
            "description": "一对一文书修改，包括Personal Statement和CV优化",
            "category": "essay",
            "price": 200.00,
            "duration": 120,
            "delivery_days": 3
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/api/v1/services",
                json=service_data,
                headers=headers
            ) as response:
                success = response.status in [200, 201]
                if success:
                    result = await response.json()
                    self.test_data['service'] = result
                    self.log_test("发布服务", True, f"服务标题: {service_data['title']}")
                else:
                    error_text = await response.text()
                    self.log_test("发布服务", False, f"状态码: {response.status}, 错误: {error_text[:100]}")
        except Exception as e:
            self.log_test("发布服务", False, f"错误: {str(e)}")
        
        # 测试获取服务列表
        try:
            async with self.session.get(f"{BASE_URL}/api/v1/services") as response:
                success = response.status == 200
                if success:
                    services = await response.json()
                    self.log_test("获取服务列表", True, f"服务数量: {len(services) if isinstance(services, list) else 'N/A'}")
                else:
                    self.log_test("获取服务列表", False, f"状态码: {response.status}")
        except Exception as e:
            self.log_test("获取服务列表", False, f"错误: {str(e)}")
    
    async def test_matching_system(self):
        """测试匹配系统"""
        if 'student' not in self.tokens:
            self.log_test("匹配系统测试", False, "未获取到学生token，跳过测试")
            return
        
        logger.info("🎯 测试智能匹配系统")
        headers = {"Authorization": f"Bearer {self.tokens['student']}"}
        
        # 测试获取推荐
        recommend_data = {
            "target_universities": ["Stanford University"],
            "target_majors": ["Computer Science"],
            "degree_level": "master"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/api/v1/matching/recommend",
                json=recommend_data,
                headers=headers
            ) as response:
                success = response.status == 200
                if success:
                    recommendations = await response.json()
                    self.log_test("获取推荐导师", True, f"推荐数量: {len(recommendations) if isinstance(recommendations, list) else 'N/A'}")
                else:
                    error_text = await response.text()
                    self.log_test("获取推荐导师", False, f"状态码: {response.status}, 错误: {error_text[:100]}")
        except Exception as e:
            self.log_test("获取推荐导师", False, f"错误: {str(e)}")
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info("⚠️ 测试错误处理")
        
        # 测试无效的认证
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        
        try:
            async with self.session.get(
                f"{BASE_URL}/api/v1/users/me",
                headers=invalid_headers
            ) as response:
                success = response.status == 401
                self.log_test("无效token处理", success, f"状态码: {response.status}")
        except Exception as e:
            self.log_test("无效token处理", False, f"错误: {str(e)}")
        
        # 测试不存在的端点
        try:
            async with self.session.get(f"{BASE_URL}/api/v1/nonexistent") as response:
                success = response.status == 404
                self.log_test("404错误处理", success, f"状态码: {response.status}")
        except Exception as e:
            self.log_test("404错误处理", False, f"错误: {str(e)}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        try:
            await self.setup()
            
            # 按顺序执行测试
            if not await self.test_server_health():
                logger.error("❌ 服务器不可用，终止测试")
                return False
            
            await self.test_basic_endpoints()
            await self.test_user_registration_and_login()
            await self.test_user_profile_operations()
            await self.test_mentor_operations()
            await self.test_student_operations()
            await self.test_service_operations()
            await self.test_matching_system()
            await self.test_error_handling()
            
            # 输出测试结果
            self.print_summary()
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            return False
        finally:
            await self.cleanup()
        
        return self.results['failed'] == 0
    
    def print_summary(self):
        """打印测试总结"""
        logger.info("=" * 60)
        logger.info("📊 测试结果总结")
        logger.info("=" * 60)
        logger.info(f"总测试数: {self.results['total']}")
        logger.info(f"通过: {self.results['passed']} ✅")
        logger.info(f"失败: {self.results['failed']} ❌")
        logger.info(f"成功率: {(self.results['passed'] / self.results['total'] * 100):.1f}%")
        logger.info("=" * 60)
        
        if self.results['failed'] > 0:
            logger.info("❌ 失败的测试:")
            for detail in self.results['details']:
                if "❌ FAIL" in detail:
                    logger.info(f"  {detail}")

async def main():
    """主函数"""
    print("🚀 启航引路人平台 - API测试套件")
    print("=" * 60)
    
    tester = ComprehensiveAPITester()
    success = await tester.run_all_tests()
    
    if success:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败，请查看日志")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
