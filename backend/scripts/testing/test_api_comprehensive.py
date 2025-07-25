#!/usr/bin/env python3
"""
启航引路人平台 - API功能测试套件
使用标准库进行全面的API测试
"""
import requests
import json
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8001"

class APITestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.tokens = {}  # 存储不同用户的token
        self.test_data = {}  # 存储测试过程中创建的数据
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
    
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
        print(result)
    
    def test_server_connectivity(self) -> bool:
        """测试服务器连通性"""
        print("🌐 测试服务器连通性")
        print("-" * 50)
        
        try:
            # 测试健康检查端点
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            if success:
                data = response.json()
                self.log_test("健康检查", True, f"状态: {data.get('status', 'unknown')}")
            else:
                self.log_test("健康检查", False, f"状态码: {response.status_code}")
            
            # 测试根路径
            response = self.session.get(f"{BASE_URL}/")
            root_success = response.status_code == 200
            if root_success:
                data = response.json()
                self.log_test("根路径访问", True, f"平台版本: {data.get('version', 'unknown')}")
            else:
                self.log_test("根路径访问", False, f"状态码: {response.status_code}")
            
            # 测试API文档
            response = self.session.get(f"{BASE_URL}/docs")
            docs_success = response.status_code == 200
            self.log_test("API文档访问", docs_success, 
                         "可访问" if docs_success else f"状态码: {response.status_code}")
            
            return success and root_success
            
        except requests.exceptions.RequestException as e:
            self.log_test("服务器连通性", False, f"连接错误: {str(e)}")
            return False
    
    def test_authentication_system(self):
        """测试认证系统"""
        print("\n🔐 测试用户认证系统")
        print("-" * 50)
        
        # 生成唯一的测试用户数据
        timestamp = int(time.time())
        test_users = [
            {
                "username": f"test_student_{timestamp}",
                "email": f"student_{timestamp}@test.edu",
                "password": "TestPass123!",
                "role": "student"
            },
            {
                "username": f"test_mentor_{timestamp}",
                "email": f"mentor_{timestamp}@stanford.edu",
                "password": "TestPass123!",
                "role": "mentor"
            }
        ]
        
        for user_data in test_users:
            role = user_data['role']
            
            # 测试用户注册
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/v1/auth/register",
                    json=user_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.test_data[f"{role}_user"] = result
                    self.log_test(f"{role}用户注册", True, f"用户ID: {result.get('id', 'N/A')}")
                else:
                    error_detail = self._get_error_detail(response)
                    self.log_test(f"{role}用户注册", False, f"状态码: {response.status_code}, {error_detail}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"{role}用户注册", False, f"请求错误: {str(e)}")
                continue
            
            # 测试用户登录
            try:
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
                
                response = self.session.post(
                    f"{BASE_URL}/api/v1/auth/login",
                    data=login_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.tokens[role] = result.get('access_token')
                    self.log_test(f"{role}用户登录", True, "Token获取成功")
                else:
                    error_detail = self._get_error_detail(response)
                    self.log_test(f"{role}用户登录", False, f"状态码: {response.status_code}, {error_detail}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"{role}用户登录", False, f"请求错误: {str(e)}")
    
    def test_user_profile_management(self):
        """测试用户资料管理"""
        print("\n👤 测试用户资料管理")
        print("-" * 50)
        
        for role in ['student', 'mentor']:
            if role not in self.tokens:
                self.log_test(f"{role}资料测试", False, "未获取到认证token")
                continue
            
            headers = {"Authorization": f"Bearer {self.tokens[role]}"}
            
            # 测试获取当前用户信息
            try:
                response = self.session.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
                if response.status_code == 200:
                    user_info = response.json()
                    self.log_test(f"获取{role}用户信息", True, 
                                 f"用户名: {user_info.get('username', 'N/A')}")
                else:
                    error_detail = self._get_error_detail(response)
                    self.log_test(f"获取{role}用户信息", False, 
                                 f"状态码: {response.status_code}, {error_detail}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"获取{role}用户信息", False, f"请求错误: {str(e)}")
    
    def test_mentor_specific_features(self):
        """测试导师专用功能"""
        if 'mentor' not in self.tokens:
            self.log_test("导师功能测试", False, "未获取到导师token")
            return
        
        print("\n🎓 测试导师专用功能")
        print("-" * 50)
        
        headers = {"Authorization": f"Bearer {self.tokens['mentor']}"}
        
        # 测试创建导师资料
        mentor_profile = {
            "university": "Stanford University",
            "major": "Computer Science",
            "degree_level": "master",
            "graduation_year": 2023,
            "current_status": "graduated",
            "specialties": ["文书指导", "面试辅导", "选校咨询"],
            "bio": "斯坦福大学计算机科学硕士，专业提供留学申请全流程指导，已成功帮助50+学生获得心仪offer。"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/mentors/profile",
                json=mentor_profile,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.test_data['mentor_profile'] = result
                self.log_test("创建导师资料", True, f"专业: {mentor_profile['major']}")
            else:
                error_detail = self._get_error_detail(response)
                self.log_test("创建导师资料", False, 
                             f"状态码: {response.status_code}, {error_detail}")
        except requests.exceptions.RequestException as e:
            self.log_test("创建导师资料", False, f"请求错误: {str(e)}")
        
        # 测试发布服务
        service_data = {
            "title": "Stanford CS申请全程指导",
            "description": "提供包括选校策略、文书修改、面试准备在内的一对一个性化指导服务",
            "category": "comprehensive",
            "price": 299.99,
            "duration": 180,
            "delivery_days": 7
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/services",
                json=service_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.test_data['service'] = result
                self.log_test("发布指导服务", True, f"服务: {service_data['title']}")
            else:
                error_detail = self._get_error_detail(response)
                self.log_test("发布指导服务", False, 
                             f"状态码: {response.status_code}, {error_detail}")
        except requests.exceptions.RequestException as e:
            self.log_test("发布指导服务", False, f"请求错误: {str(e)}")
    
    def test_student_specific_features(self):
        """测试学生专用功能"""
        if 'student' not in self.tokens:
            self.log_test("学生功能测试", False, "未获取到学生token")
            return
        
        print("\n📚 测试学生专用功能")
        print("-" * 50)
        
        headers = {"Authorization": f"Bearer {self.tokens['student']}"}
        
        # 测试创建学生资料
        student_profile = {
            "current_education": "本科大三",
            "target_degree": "master",
            "target_universities": ["Stanford University", "MIT", "CMU"],
            "target_majors": ["Computer Science", "Machine Learning"],
            "application_timeline": "2025年秋季入学",
            "gpa": 3.8,
            "english_test_score": "TOEFL 110"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/students/profile",
                json=student_profile,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.test_data['student_profile'] = result
                self.log_test("创建学生资料", True, f"目标学位: {student_profile['target_degree']}")
            else:
                error_detail = self._get_error_detail(response)
                self.log_test("创建学生资料", False, 
                             f"状态码: {response.status_code}, {error_detail}")
        except requests.exceptions.RequestException as e:
            self.log_test("创建学生资料", False, f"请求错误: {str(e)}")
    
    def test_service_browsing(self):
        """测试服务浏览功能"""
        print("\n🛒 测试服务浏览功能")
        print("-" * 50)
        
        # 测试获取服务列表（无需认证）
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/services")
            if response.status_code == 200:
                services = response.json()
                service_count = len(services) if isinstance(services, list) else "未知"
                self.log_test("获取服务列表", True, f"服务数量: {service_count}")
            else:
                error_detail = self._get_error_detail(response)
                self.log_test("获取服务列表", False, 
                             f"状态码: {response.status_code}, {error_detail}")
        except requests.exceptions.RequestException as e:
            self.log_test("获取服务列表", False, f"请求错误: {str(e)}")
    
    def test_matching_system(self):
        """测试智能匹配系统"""
        if 'student' not in self.tokens:
            self.log_test("匹配系统测试", False, "未获取到学生token")
            return
        
        print("\n🎯 测试智能匹配系统")
        print("-" * 50)
        
        headers = {"Authorization": f"Bearer {self.tokens['student']}"}
        
        # 测试获取导师推荐
        matching_criteria = {
            "target_universities": ["Stanford University"],
            "target_majors": ["Computer Science"],
            "degree_level": "master",
            "budget_range": [200, 500]
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/matching/recommend",
                json=matching_criteria,
                headers=headers
            )
            
            if response.status_code == 200:
                recommendations = response.json()
                rec_count = len(recommendations) if isinstance(recommendations, list) else "未知"
                self.log_test("获取导师推荐", True, f"推荐数量: {rec_count}")
            else:
                error_detail = self._get_error_detail(response)
                self.log_test("获取导师推荐", False, 
                             f"状态码: {response.status_code}, {error_detail}")
        except requests.exceptions.RequestException as e:
            self.log_test("获取导师推荐", False, f"请求错误: {str(e)}")
    
    def test_error_handling(self):
        """测试错误处理机制"""
        print("\n⚠️ 测试错误处理机制")
        print("-" * 50)
        
        # 测试无效的认证token
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/users/me", headers=invalid_headers)
            success = response.status_code == 401
            self.log_test("无效token处理", success, 
                         f"状态码: {response.status_code}" + (" (正确)" if success else " (错误)"))
        except requests.exceptions.RequestException as e:
            self.log_test("无效token处理", False, f"请求错误: {str(e)}")
        
        # 测试不存在的API端点
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/nonexistent-endpoint")
            success = response.status_code == 404
            self.log_test("404错误处理", success, 
                         f"状态码: {response.status_code}" + (" (正确)" if success else " (错误)"))
        except requests.exceptions.RequestException as e:
            self.log_test("404错误处理", False, f"请求错误: {str(e)}")
        
        # 测试无效的请求数据
        if 'student' in self.tokens:
            headers = {"Authorization": f"Bearer {self.tokens['student']}"}
            invalid_data = {"invalid_field": "invalid_value"}
            
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/v1/students/profile",
                    json=invalid_data,
                    headers=headers
                )
                success = response.status_code in [400, 422]  # 数据验证错误
                self.log_test("数据验证错误处理", success, 
                             f"状态码: {response.status_code}" + (" (正确)" if success else " (错误)"))
            except requests.exceptions.RequestException as e:
                self.log_test("数据验证错误处理", False, f"请求错误: {str(e)}")
    
    def test_performance_basic(self):
        """测试基本性能指标"""
        print("\n⚡ 测试基本性能指标")
        print("-" * 50)
        
        # 测试响应时间
        endpoints = [
            ("/", "根路径"),
            ("/health", "健康检查"),
            ("/api/v1/services", "服务列表")
        ]
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}{endpoint}")
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                success = response.status_code == 200 and response_time < 2000  # 2秒阈值
                
                self.log_test(f"{name}响应时间", success, 
                             f"{response_time:.0f}ms" + (" (良好)" if response_time < 500 else " (可接受)" if response_time < 2000 else " (较慢)"))
            except requests.exceptions.RequestException as e:
                self.log_test(f"{name}响应时间", False, f"请求错误: {str(e)}")
    
    def _get_error_detail(self, response) -> str:
        """提取响应中的错误详情"""
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                if isinstance(error_data, dict):
                    return error_data.get('detail', 'Unknown error')
                else:
                    return str(error_data)[:100]
            else:
                return response.text[:100]
        except:
            return "Unable to parse error"
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 启航引路人平台 - API功能测试套件")
        print("=" * 60)
        print(f"📍 测试目标: {BASE_URL}")
        print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # 检查服务器连通性
            if not self.test_server_connectivity():
                print("❌ 服务器不可用，终止测试")
                return False
            
            # 按顺序执行功能测试
            self.test_authentication_system()
            self.test_user_profile_management()
            self.test_mentor_specific_features()
            self.test_student_specific_features()
            self.test_service_browsing()
            self.test_matching_system()
            self.test_error_handling()
            self.test_performance_basic()
            
            # 输出测试结果
            self.print_summary()
            
        except Exception as e:
            print(f"❌ 测试执行失败: {str(e)}")
            return False
        finally:
            self.session.close()
        
        return self.results['failed'] == 0
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 API测试结果总结")
        print("=" * 60)
        print(f"🕐 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 总测试数: {self.results['total']}")
        print(f"✅ 通过数量: {self.results['passed']}")
        print(f"❌ 失败数量: {self.results['failed']}")
        print(f"📊 成功率: {(self.results['passed'] / self.results['total'] * 100):.1f}%")
        print("=" * 60)
        
        if self.results['failed'] > 0:
            print("❌ 失败的测试详情:")
            for detail in self.results['details']:
                if "❌ FAIL" in detail:
                    print(f"  {detail}")
            print("=" * 60)
        
        # 给出建议
        if self.results['failed'] == 0:
            print("🎉 所有测试通过！API功能运行正常。")
        elif self.results['failed'] <= 3:
            print("⚠️ 少量测试失败，请检查具体问题。")
        else:
            print("🚨 多个测试失败，建议检查服务器配置和数据库连接。")

def main():
    """主函数"""
    tester = APITestSuite()
    success = tester.run_all_tests()
    
    if success:
        print("🎊 API测试全部通过！")
        sys.exit(0)
    else:
        print("💥 部分API测试失败，请查看详细日志")
        sys.exit(1)

if __name__ == "__main__":
    main()
