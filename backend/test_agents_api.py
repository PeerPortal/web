#!/usr/bin/env python3
"""
PeerPortal AI智能体系统 v2.0 API测试脚本
测试留学规划师和咨询师的功能
"""
import asyncio
import json
import time
from typing import Dict, Any
import httpx


class AgentAPITester:
    """AI智能体API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_server_health(self) -> bool:
        """测试服务器健康状态"""
        try:
            print("🔍 检查服务器状态...")
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 服务器运行正常")
                print(f"   状态: {data.get('status', 'unknown')}")
                print(f"   服务: {data.get('service', 'unknown')}")
                return True
            else:
                print(f"⚠️ 服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
            return False
    
    async def test_agent_system_status(self) -> bool:
        """测试智能体系统状态"""
        try:
            print("\n🤖 检查AI智能体系统状态...")
            response = await self.client.get(f"{self.base_url}/api/v2/agents/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 智能体系统运行正常")
                print(f"   版本: {data.get('version', 'unknown')}")
                print(f"   初始化状态: {data.get('is_initialized', False)}")
                print(f"   可用智能体: {', '.join(data.get('available_agents', []))}")
                
                external_services = data.get('external_services', {})
                print(f"   外部服务状态:")
                for service, status in external_services.items():
                    status_icon = "✅" if status else "⚪"
                    print(f"     {status_icon} {service}: {'已配置' if status else '未配置'}")
                return True
            else:
                print(f"⚠️ 智能体系统响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 智能体系统连接失败: {e}")
            return False
    
    async def test_agent_info(self) -> bool:
        """测试获取架构信息"""
        try:
            print("\n🏗️ 获取架构信息...")
            response = await self.client.get(f"{self.base_url}/api/v2/agents/info")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 架构信息获取成功")
                print(f"   系统名称: {data.get('name', 'unknown')}")
                print(f"   系统版本: {data.get('version', 'unknown')}")
                print(f"   作者: {data.get('author', 'unknown')}")
                print(f"   智能体类型: {', '.join(data.get('agent_types', []))}")
                print(f"   功能模块: {len(data.get('modules', []))}个")
                print(f"   特色功能: {len(data.get('features', []))}个")
                print(f"   集成工具: {len(data.get('tools', []))}个")
                return True
            else:
                print(f"⚠️ 架构信息获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 架构信息获取异常: {e}")
            return False
    
    async def test_study_planner(self) -> bool:
        """测试留学规划师"""
        try:
            print("\n🎓 测试留学规划师...")
            
            test_messages = [
                "你好，我想申请美国大学的计算机科学专业，请给我一些建议",
                "我的GPA是3.5，托福100分，能申请哪些学校？"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n  📝 测试对话 {i}: {message[:50]}...")
                
                request_data = {
                    "message": message,
                    "user_id": "test_user_123",
                    "session_id": f"test_session_{int(time.time())}"
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/v2/agents/planner/chat",
                    json=request_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ 规划师回复成功")
                    print(f"    智能体类型: {data.get('agent_type', 'unknown')}")
                    print(f"    回复长度: {len(data.get('response', ''))}字符")
                    
                    # 显示回复的前100个字符
                    response_text = data.get('response', '')
                    if response_text:
                        preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
                        print(f"    回复预览: {preview}")
                    else:
                        print(f"    ⚠️ 回复为空")
                        return False
                else:
                    print(f"    ❌ 规划师回复失败: {response.status_code}")
                    if response.status_code < 500:
                        try:
                            error_data = response.json()
                            print(f"    错误详情: {error_data.get('detail', 'unknown')}")
                        except:
                            pass
                    return False
                
                # 间隔一下，避免请求过快
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ 留学规划师测试异常: {e}")
            return False
    
    async def test_study_consultant(self) -> bool:
        """测试留学咨询师"""
        try:
            print("\n💬 测试留学咨询师...")
            
            test_messages = [
                "留学美国的总费用大概是多少？",
                "申请美国研究生需要什么材料？"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n  📝 测试咨询 {i}: {message[:50]}...")
                
                request_data = {
                    "message": message,
                    "user_id": "test_user_456",
                    "session_id": f"consultant_session_{int(time.time())}"
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/v2/agents/consultant/chat",
                    json=request_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ 咨询师回复成功")
                    print(f"    智能体类型: {data.get('agent_type', 'unknown')}")
                    print(f"    回复长度: {len(data.get('response', ''))}字符")
                    
                    # 显示回复的前100个字符
                    response_text = data.get('response', '')
                    if response_text:
                        preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
                        print(f"    回复预览: {preview}")
                    else:
                        print(f"    ⚠️ 回复为空")
                        return False
                else:
                    print(f"    ❌ 咨询师回复失败: {response.status_code}")
                    if response.status_code < 500:
                        try:
                            error_data = response.json()
                            print(f"    错误详情: {error_data.get('detail', 'unknown')}")
                        except:
                            pass
                    return False
                
                # 间隔一下，避免请求过快
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ 留学咨询师测试异常: {e}")
            return False
    
    async def test_agent_health(self) -> bool:
        """测试智能体系统健康检查"""
        try:
            print("\n🩺 测试智能体系统健康检查...")
            response = await self.client.get(f"{self.base_url}/api/v2/agents/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 智能体系统健康检查通过")
                print(f"   状态: {data.get('status', 'unknown')}")
                print(f"   系统: {data.get('system', 'unknown')}")
                print(f"   专注: {data.get('focus', 'unknown')}")
                print(f"   智能体: {', '.join(data.get('agents', []))}")
                return True
            else:
                print(f"⚠️ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🧪 PeerPortal AI智能体系统 v2.0 API测试")
        print("=" * 60)
        
        tests = [
            ("服务器健康检查", self.test_server_health),
            ("智能体系统状态", self.test_agent_system_status),
            ("架构信息获取", self.test_agent_info),
            ("智能体健康检查", self.test_agent_health),
            ("留学规划师功能", self.test_study_planner),
            ("留学咨询师功能", self.test_study_consultant),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                    print(f"\n✅ {test_name}: 通过")
                else:
                    print(f"\n❌ {test_name}: 失败")
            except Exception as e:
                print(f"\n💥 {test_name}: 异常 - {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！AI智能体系统运行正常")
            return True
        elif passed >= total * 0.7:
            print("⚠️ 大部分测试通过，系统基本可用")
            return True
        else:
            print("❌ 多项测试失败，请检查系统配置")
            return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    tester = AgentAPITester()
    
    try:
        success = await tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("💡 使用建议:")
        print("   🌐 浏览器访问: http://localhost:8000/docs")
        print("   🤖 智能体状态: http://localhost:8000/api/v2/agents/status") 
        print("   📝 测试对话: 使用API文档的交互界面")
        print("   🔧 如有问题: 检查日志和环境配置")
        
        if success:
            print("\n🚀 系统已准备就绪，可以开始使用！")
        else:
            print("\n🔄 系统需要进一步配置，请参考错误信息")
    
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main()) 