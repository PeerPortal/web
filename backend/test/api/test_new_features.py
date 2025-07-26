"""
PeerPortal 新增功能综合测试脚本
测试论坛系统、消息系统、文件上传、AI路由等新功能
"""
import asyncio
import httpx
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_USER_CREDENTIALS = {
    "username": "test_student",
    "password": "test123456"
}

class FeatureTestRunner:
    """新功能测试运行器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_results = {}
        
    async def setup(self):
        """测试环境设置"""
        print("🔧 设置测试环境...")
        
        # 检查服务器是否运行
        try:
            response = await self.client.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ 服务器运行正常")
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到服务器: {e}")
            print("请确保后端服务器已启动: uvicorn app.main:app --reload")
            return False
        
        # 尝试登录获取认证令牌
        await self.authenticate()
        return True
    
    async def authenticate(self):
        """用户认证"""
        print("🔐 尝试用户认证...")
        
        try:
            # 尝试注册测试用户
            register_data = {
                "username": TEST_USER_CREDENTIALS["username"],
                "email": "test@example.com",
                "password": TEST_USER_CREDENTIALS["password"],
                "role": "student"
            }
            register_response = await self.client.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data
            )
            
            if register_response.status_code in [201, 400]:  # 201创建成功，400可能已存在
                print("📝 测试用户准备完成")
            
            # 登录获取token
            login_data = {
                "username": TEST_USER_CREDENTIALS["username"],
                "password": TEST_USER_CREDENTIALS["password"]
            }
            login_response = await self.client.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.auth_token = token_data.get("access_token")
                print("✅ 用户认证成功")
                return True
            else:
                print(f"❌ 登录失败: {login_response.status_code}")
                print(f"响应: {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 认证过程出错: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_forum_system(self):
        """测试论坛系统"""
        print("\n🏛️ 测试论坛系统...")
        results = {}
        
        headers = self.get_auth_headers()
        
        # 1. 测试获取论坛分类
        print("  📂 测试获取论坛分类...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/forum/categories")
            if response.status_code == 200:
                categories = response.json()
                print(f"  ✅ 获取到 {len(categories)} 个分类")
                results["get_categories"] = "✅ 成功"
            else:
                print(f"  ❌ 获取分类失败: {response.status_code}")
                results["get_categories"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取分类异常: {e}")
            results["get_categories"] = f"❌ 异常: {e}"
        
        # 2. 测试创建帖子
        print("  📝 测试创建帖子...")
        try:
            post_data = {
                "title": "测试帖子 - 美国CS申请经验分享",
                "content": "这是一个测试帖子，分享申请美国计算机科学硕士的经验...",
                "category": "application",
                "tags": ["美国留学", "CS申请", "经验分享"]
            }
            response = await self.client.post(
                f"{self.base_url}/api/v1/forum/posts",
                json=post_data,
                headers=headers
            )
            if response.status_code == 201:
                post = response.json()
                print(f"  ✅ 创建帖子成功，ID: {post.get('id', 'N/A')}")
                results["create_post"] = "✅ 成功"
                results["test_post_id"] = post.get("id")
            else:
                print(f"  ❌ 创建帖子失败: {response.status_code}")
                print(f"  响应: {response.text}")
                results["create_post"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 创建帖子异常: {e}")
            results["create_post"] = f"❌ 异常: {e}"
        
        # 3. 测试获取帖子列表
        print("  📋 测试获取帖子列表...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/forum/posts?limit=10&category=application"
            )
            if response.status_code == 200:
                posts_data = response.json()
                posts = posts_data.get("posts", [])
                total = posts_data.get("total", 0)
                print(f"  ✅ 获取到 {len(posts)} 个帖子，总计 {total} 个")
                results["get_posts"] = "✅ 成功"
            else:
                print(f"  ❌ 获取帖子失败: {response.status_code}")
                results["get_posts"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取帖子异常: {e}")
            results["get_posts"] = f"❌ 异常: {e}"
        
        # 4. 测试获取热门标签
        print("  🏷️ 测试获取热门标签...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/forum/tags/popular")
            if response.status_code == 200:
                tags = response.json()
                print(f"  ✅ 获取到 {len(tags)} 个热门标签")
                results["get_popular_tags"] = "✅ 成功"
            else:
                print(f"  ❌ 获取标签失败: {response.status_code}")
                results["get_popular_tags"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取标签异常: {e}")
            results["get_popular_tags"] = f"❌ 异常: {e}"
        
        self.test_results["forum_system"] = results
        return results
    
    async def test_message_system(self):
        """测试消息系统"""
        print("\n💬 测试消息系统...")
        results = {}
        
        headers = self.get_auth_headers()
        
        # 1. 测试获取对话列表
        print("  📋 测试获取对话列表...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/messages/conversations",
                headers=headers
            )
            if response.status_code == 200:
                conversations = response.json()
                print(f"  ✅ 获取到 {len(conversations)} 个对话")
                results["get_conversations"] = "✅ 成功"
            else:
                print(f"  ❌ 获取对话失败: {response.status_code}")
                results["get_conversations"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取对话异常: {e}")
            results["get_conversations"] = f"❌ 异常: {e}"
        
        # 2. 测试获取消息列表
        print("  📨 测试获取消息列表...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/messages?limit=10",
                headers=headers
            )
            if response.status_code == 200:
                messages = response.json()
                print(f"  ✅ 获取到 {len(messages)} 条消息")
                results["get_messages"] = "✅ 成功"
            else:
                print(f"  ❌ 获取消息失败: {response.status_code}")
                results["get_messages"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取消息异常: {e}")
            results["get_messages"] = f"❌ 异常: {e}"
        
        # 3. 测试发送消息
        print("  📤 测试发送消息...")
        try:
            message_data = {
                "recipient_id": 2,  # 假设存在ID为2的用户
                "content": "这是一条测试消息，用于验证消息系统功能",
                "message_type": "text"
            }
            response = await self.client.post(
                f"{self.base_url}/api/v1/messages",
                json=message_data,
                headers=headers
            )
            if response.status_code == 201:
                message = response.json()
                print(f"  ✅ 发送消息成功，ID: {message.get('id', 'N/A')}")
                results["send_message"] = "✅ 成功"
                results["test_message_id"] = message.get("id")
            else:
                print(f"  ❌ 发送消息失败: {response.status_code}")
                print(f"  响应: {response.text}")
                results["send_message"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 发送消息异常: {e}")
            results["send_message"] = f"❌ 异常: {e}"
        
        self.test_results["message_system"] = results
        return results
    
    async def test_file_upload(self):
        """测试文件上传系统"""
        print("\n📁 测试文件上传系统...")
        results = {}
        
        headers = self.get_auth_headers()
        
        # 1. 测试头像上传
        print("  🖼️ 测试头像上传...")
        try:
            # 创建一个临时测试图片文件
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                # 创建一个简单的PNG文件头（1x1像素的透明PNG）
                png_data = bytes([
                    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
                    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
                    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 pixels
                    0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # 32-bit RGBA
                    0x89, 0x00, 0x00, 0x00, 0x0B, 0x49, 0x44, 0x41,  # IDAT chunk
                    0x54, 0x08, 0x1D, 0x01, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x37, 0x6E, 0xF9, 0x24, 0x00, 0x00, 0x00,
                    0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82  # IEND
                ])
                temp_file.write(png_data)
                temp_file_path = temp_file.name
            
            # 上传文件
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test_avatar.png", f, "image/png")}
                response = await self.client.post(
                    f"{self.base_url}/api/v1/files/upload/avatar",
                    files=files,
                    headers=headers
                )
            
            # 清理临时文件
            os.unlink(temp_file_path)
            
            if response.status_code == 200:
                upload_result = response.json()
                print(f"  ✅ 头像上传成功: {upload_result.get('file_url', 'N/A')}")
                results["upload_avatar"] = "✅ 成功"
            else:
                print(f"  ❌ 头像上传失败: {response.status_code}")
                print(f"  响应: {response.text}")
                results["upload_avatar"] = f"❌ 失败: {response.status_code}"
                
        except Exception as e:
            print(f"  ❌ 头像上传异常: {e}")
            results["upload_avatar"] = f"❌ 异常: {e}"
        
        # 2. 测试文档上传
        print("  📄 测试文档上传...")
        try:
            # 创建一个临时测试文本文件
            with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as temp_file:
                temp_file.write("这是一个测试文档，用于验证文件上传功能。")
                temp_file_path = temp_file.name
            
            # 上传文件
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test_document.txt", f, "text/plain")}
                data = {"description": "测试文档上传"}
                response = await self.client.post(
                    f"{self.base_url}/api/v1/files/upload/document",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            # 清理临时文件
            os.unlink(temp_file_path)
            
            if response.status_code == 200:
                upload_result = response.json()
                print(f"  ✅ 文档上传成功: {upload_result.get('file_url', 'N/A')}")
                results["upload_document"] = "✅ 成功"
            else:
                print(f"  ❌ 文档上传失败: {response.status_code}")
                print(f"  响应: {response.text}")
                results["upload_document"] = f"❌ 失败: {response.status_code}"
                
        except Exception as e:
            print(f"  ❌ 文档上传异常: {e}")
            results["upload_document"] = f"❌ 异常: {e}"
        
        self.test_results["file_upload"] = results
        return results
    
    async def test_ai_routes(self):
        """测试AI路由修复"""
        print("\n🤖 测试AI路由修复...")
        results = {}
        
        headers = self.get_auth_headers()
        
        # 1. 测试AI能力查询
        print("  🔍 测试AI能力查询...")
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/planner/capabilities")
            if response.status_code == 200:
                capabilities = response.json()
                print(f"  ✅ AI能力查询成功")
                print(f"  📋 可用能力: {capabilities.get('capabilities', [])}")
                results["get_capabilities"] = "✅ 成功"
            else:
                print(f"  ❌ AI能力查询失败: {response.status_code}")
                results["get_capabilities"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ AI能力查询异常: {e}")
            results["get_capabilities"] = f"❌ 异常: {e}"
        
        # 2. 测试AI对话接口（非流式）
        print("  💭 测试AI对话接口...")
        try:
            ai_data = {
                "input": "请简单介绍一下美国CS硕士申请的基本要求",
                "session_id": "test_session",
                "stream": False
            }
            response = await self.client.post(
                f"{self.base_url}/api/v1/planner/invoke",
                json=ai_data,
                headers=headers
            )
            if response.status_code == 200:
                ai_response = response.json()
                print(f"  ✅ AI对话成功")
                results["ai_invoke"] = "✅ 成功"
            else:
                print(f"  ❌ AI对话失败: {response.status_code}")
                print(f"  响应: {response.text}")
                results["ai_invoke"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ AI对话异常: {e}")
            results["ai_invoke"] = f"❌ 异常: {e}"
        
        self.test_results["ai_routes"] = results
        return results
    
    async def test_user_endpoints(self):
        """测试用户管理端点"""
        print("\n👤 测试用户管理端点...")
        results = {}
        
        headers = self.get_auth_headers()
        
        # 1. 测试获取当前用户信息
        print("  📋 测试获取当前用户信息...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/users/me",
                headers=headers
            )
            if response.status_code == 200:
                user = response.json()
                print(f"  ✅ 获取用户信息成功: {user.get('username', 'N/A')}")
                results["get_user_me"] = "✅ 成功"
            else:
                print(f"  ❌ 获取用户信息失败: {response.status_code}")
                results["get_user_me"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取用户信息异常: {e}")
            results["get_user_me"] = f"❌ 异常: {e}"
        
        # 2. 测试获取基础用户信息端点
        print("  📝 测试获取基础用户信息...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/users/me/basic",
                headers=headers
            )
            if response.status_code == 200:
                user_basic = response.json()
                print(f"  ✅ 获取基础信息成功")
                results["get_user_basic"] = "✅ 成功"
            else:
                print(f"  ❌ 获取基础信息失败: {response.status_code}")
                results["get_user_basic"] = f"❌ 失败: {response.status_code}"
        except Exception as e:
            print(f"  ❌ 获取基础信息异常: {e}")
            results["get_user_basic"] = f"❌ 异常: {e}"
        
        self.test_results["user_endpoints"] = results
        return results
    
    async def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 生成测试报告...")
        
        report_data = {
            "test_time": datetime.now().isoformat(),
            "test_results": self.test_results,
            "summary": {}
        }
        
        # 统计测试结果
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            for test_name, result in tests.items():
                if test_name.endswith("_id"):  # 跳过存储ID的字段
                    continue
                total_tests += 1
                if result.startswith("✅"):
                    passed_tests += 1
        
        report_data["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }
        
        # 保存报告
        report_filename = f"new_features_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 测试报告已保存: {report_filename}")
        
        # 打印摘要
        print("\n📈 测试摘要:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过测试: {passed_tests}")
        print(f"  失败测试: {total_tests - passed_tests}")
        print(f"  成功率: {report_data['summary']['success_rate']}")
        
        # 打印详细结果
        print("\n📋 详细测试结果:")
        for category, tests in self.test_results.items():
            print(f"  📂 {category}:")
            for test_name, result in tests.items():
                if not test_name.endswith("_id"):
                    print(f"    {test_name}: {result}")
        
        return report_data
    
    async def cleanup(self):
        """清理测试环境"""
        await self.client.aclose()
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始新功能综合测试")
        print("=" * 50)
        
        # 环境设置
        if not await self.setup():
            print("❌ 测试环境设置失败，终止测试")
            return
        
        try:
            # 运行各项测试
            await self.test_forum_system()
            await self.test_message_system()
            await self.test_file_upload()
            await self.test_ai_routes()
            await self.test_user_endpoints()
            
            # 生成报告
            await self.generate_test_report()
            
        finally:
            await self.cleanup()
        
        print("\n🎉 测试完成！")

async def main():
    """主函数"""
    tester = FeatureTestRunner()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 