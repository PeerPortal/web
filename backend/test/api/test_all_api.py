#!/usr/bin/env python3
"""
完整API接口测试套件
一次性测试所有API端点，包括正常和异常情况
"""
import requests
import json
import sys
import time
import random
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8001"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_user_id = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        
        self.test_results.append(result)
        print(result)

    def check_server_health(self) -> bool:
        """检查服务器健康状态"""
        print("🏥 检查服务器状态")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("服务器健康检查", True, f"状态: {data.get('status')}")
                return True
            else:
                self.log_test("服务器健康检查", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("服务器健康检查", False, f"连接失败: {e}")
            return False

    def test_root_endpoint(self):
        """测试根路径"""
        print("\n🏠 测试根路径")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            success = response.status_code == 200
            self.log_test("根路径访问", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("根路径访问", False, f"异常: {e}")

    def test_auth_endpoints(self):
        """测试认证相关端点"""
        print("\n🔐 测试认证API")
        print("-" * 50)
        
        # 生成唯一的测试用户名
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        test_username = f"apitest_{timestamp}_{random_num}"
        test_email = f"apitest_{timestamp}@example.com"
        test_password = "test123456"
        
        # 1. 测试用户注册
        self._test_user_registration(test_username, test_email, test_password)
        
        # 2. 测试重复注册（应该失败）
        self._test_duplicate_registration(test_username, test_email, test_password)
        
        # 3. 测试无效注册数据
        self._test_invalid_registration()
        
        # 4. 测试用户登录
        self._test_user_login(test_username, test_password)
        
        # 5. 测试错误登录
        self._test_invalid_login(test_username, "wrongpassword")
        
        # 6. 测试不存在用户登录
        self._test_nonexistent_user_login()
        
        # 7. 测试token刷新
        if self.token:
            self._test_token_refresh()

    def _test_user_registration(self, username: str, email: str, password: str):
        """测试用户注册"""
        register_data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=register_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_user_id = data.get('id')
                self.log_test("用户注册", True, f"用户ID: {self.test_user_id}")
            else:
                self.log_test("用户注册", False, f"状态码: {response.status_code}, 响应: {response.text}")
        except Exception as e:
            self.log_test("用户注册", False, f"异常: {e}")

    def _test_duplicate_registration(self, username: str, email: str, password: str):
        """测试重复注册"""
        register_data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=register_data
            )
            
            # 重复注册应该失败
            success = response.status_code == 400
            self.log_test("重复注册拒绝", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("重复注册拒绝", False, f"异常: {e}")

    def _test_invalid_registration(self):
        """测试无效注册数据"""
        # 测试缺少必需字段
        invalid_data = {"username": "test"}  # 缺少密码
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=invalid_data
            )
            
            success = response.status_code == 422  # 验证错误
            self.log_test("无效注册数据拒绝", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("无效注册数据拒绝", False, f"异常: {e}")

    def _test_user_login(self, username: str, password: str):
        """测试用户登录"""
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.log_test("用户登录", True, "Token获取成功")
            else:
                self.log_test("用户登录", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("用户登录", False, f"异常: {e}")

    def _test_invalid_login(self, username: str, wrong_password: str):
        """测试错误密码登录"""
        login_data = {
            "username": username,
            "password": wrong_password
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            success = response.status_code == 401
            self.log_test("错误密码登录拒绝", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("错误密码登录拒绝", False, f"异常: {e}")

    def _test_nonexistent_user_login(self):
        """测试不存在用户登录"""
        login_data = {
            "username": "nonexistent_user_12345",
            "password": "anypassword"
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            success = response.status_code == 401
            self.log_test("不存在用户登录拒绝", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("不存在用户登录拒绝", False, f"异常: {e}")

    def _test_token_refresh(self):
        """测试token刷新"""
        if not self.token:
            self.log_test("Token刷新", False, "没有有效token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                headers=headers
            )
            
            success = response.status_code == 200
            if success:
                data = response.json()
                new_token = data.get('access_token')
                if new_token:
                    self.token = new_token  # 更新token
            
            self.log_test("Token刷新", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("Token刷新", False, f"异常: {e}")

    def test_user_endpoints(self):
        """测试用户相关端点"""
        print("\n👤 测试用户API")
        print("-" * 50)
        
        if not self.token:
            self.log_test("用户API测试", False, "没有有效token，跳过用户API测试")
            return
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # 1. 测试获取当前用户资料
        self._test_get_current_user_profile(headers)
        
        # 2. 测试获取基本用户信息
        self._test_get_current_user_basic(headers)
        
        # 3. 测试更新用户资料
        self._test_update_user_profile(headers)
        
        # 4. 测试获取其他用户公开资料
        if self.test_user_id:
            self._test_get_public_user_profile(self.test_user_id)
        
        # 5. 测试无效token访问
        self._test_invalid_token_access()
        
        # 6. 测试无authorization header访问
        self._test_no_auth_access()

    def _test_get_current_user_profile(self, headers):
        """测试获取当前用户完整资料"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
            success = response.status_code == 200
            self.log_test("获取用户完整资料", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("获取用户完整资料", False, f"异常: {e}")

    def _test_get_current_user_basic(self, headers):
        """测试获取基本用户信息"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/users/me/basic", headers=headers)
            success = response.status_code == 200
            self.log_test("获取基本用户信息", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("获取基本用户信息", False, f"异常: {e}")

    def _test_update_user_profile(self, headers):
        """测试更新用户资料"""
        profile_data = {
            "full_name": "API Test User",
            "bio": "这是API测试用户的简介",
            "location": "测试城市",
            "website": "https://api-test.example.com"
        }
        
        try:
            response = self.session.put(
                f"{BASE_URL}/api/v1/users/me",
                headers=headers,
                json=profile_data
            )
            success = response.status_code == 200
            self.log_test("更新用户资料", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("更新用户资料", False, f"异常: {e}")

    def _test_get_public_user_profile(self, user_id):
        """测试获取其他用户公开资料"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/users/{user_id}/profile")
            success = response.status_code == 200
            self.log_test("获取公开用户资料", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("获取公开用户资料", False, f"异常: {e}")

    def _test_invalid_token_access(self):
        """测试无效token访问"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
            success = response.status_code == 401
            self.log_test("无效Token访问拒绝", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("无效Token访问拒绝", False, f"异常: {e}")

    def _test_no_auth_access(self):
        """测试无认证头访问"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/users/me")
            success = response.status_code == 401
            self.log_test("无认证头访问拒绝", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("无认证头访问拒绝", False, f"异常: {e}")

    def test_api_documentation(self):
        """测试API文档端点"""
        print("\n📚 测试API文档")
        print("-" * 50)
        
        # 测试Swagger UI
        try:
            response = self.session.get(f"{BASE_URL}/docs")
            success = response.status_code == 200
            self.log_test("Swagger UI访问", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("Swagger UI访问", False, f"异常: {e}")
        
        # 测试ReDoc
        try:
            response = self.session.get(f"{BASE_URL}/redoc")
            success = response.status_code == 200
            self.log_test("ReDoc访问", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("ReDoc访问", False, f"异常: {e}")
        
        # 测试OpenAPI Schema
        try:
            response = self.session.get(f"{BASE_URL}/openapi.json")
            success = response.status_code == 200
            self.log_test("OpenAPI Schema", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("OpenAPI Schema", False, f"异常: {e}")

    def test_error_handling(self):
        """测试错误处理"""
        print("\n🚨 测试错误处理")
        print("-" * 50)
        
        # 测试不存在的端点
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/nonexistent")
            success = response.status_code == 404
            self.log_test("404错误处理", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("404错误处理", False, f"异常: {e}")
        
        # 测试方法不允许
        try:
            response = self.session.patch(f"{BASE_URL}/health")
            success = response.status_code == 405
            self.log_test("405方法不允许", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("405方法不允许", False, f"异常: {e}")

    def test_cors_headers(self):
        """测试CORS头"""
        print("\n🌐 测试CORS配置")
        print("-" * 50)
        
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
        
        try:
            response = self.session.options(f"{BASE_URL}/api/v1/auth/login", headers=headers)
            success = response.status_code in [200, 204]
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            self.log_test("CORS预检请求", success, f"状态码: {response.status_code}, CORS: {cors_header}")
        except Exception as e:
            self.log_test("CORS预检请求", False, f"异常: {e}")

    def run_performance_test(self):
        """运行简单的性能测试"""
        print("\n⚡ 性能测试")
        print("-" * 50)
        
        # 测试健康检查端点的响应时间
        total_time = 0
        iterations = 10
        successful_requests = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                response = self.session.get(f"{BASE_URL}/health")
                end_time = time.time()
                
                if response.status_code == 200:
                    successful_requests += 1
                    total_time += (end_time - start_time)
            except:
                pass
        
        if successful_requests > 0:
            avg_time = (total_time / successful_requests) * 1000  # 转换为毫秒
            success = avg_time < 1000  # 小于1秒认为是好的性能
            self.log_test("健康检查性能", success, f"平均响应时间: {avg_time:.2f}ms")
        else:
            self.log_test("健康检查性能", False, "所有请求都失败了")

    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("📊 API测试总结报告")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总测试数: {self.total_tests}")
        print(f"✅ 通过: {self.passed_tests}")
        print(f"❌ 失败: {self.failed_tests}")
        print(f"📈 成功率: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        if self.failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        print("\n📋 所有测试结果:")
        for result in self.test_results:
            print(f"  {result}")
        
        print("\n" + "=" * 80)
        if self.failed_tests == 0:
            print("🎉 所有测试通过！API工作完美！")
        else:
            print(f"⚠️  有 {self.failed_tests} 个测试失败，需要检查")
        print("=" * 80)

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始完整API测试套件")
        print("=" * 80)
        print(f"测试目标: {BASE_URL}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 检查服务器状态
        if not self.check_server_health():
            print("❌ 服务器不可用，退出测试")
            return False
        
        # 依次运行所有测试
        self.test_root_endpoint()
        self.test_auth_endpoints()
        self.test_user_endpoints()
        self.test_api_documentation()
        self.test_error_handling()
        self.test_cors_headers()
        self.run_performance_test()
        
        # 打印总结
        self.print_summary()
        
        return self.failed_tests == 0

def main():
    """主函数"""
    tester = APITester()
    success = tester.run_all_tests()
    
    # 设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 