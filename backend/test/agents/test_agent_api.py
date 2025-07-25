#!/usr/bin/env python3
"""
AI留学规划师Agent API完整测试脚本
测试通过HTTP接口调用Agent功能
"""

import requests
import json
import time
from typing import Dict, Any

class AgentAPITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self) -> bool:
        """测试健康检查接口"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ai/planner/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data['service']}")
                print(f"📊 服务状态: {data['status']}")
                print(f"🔧 工具数量: {data['tools_count']}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_agent_invoke(self, query: str) -> bool:
        """测试Agent调用接口"""
        try:
            payload = {
                "input": query,
                "session_id": "test_session_123",
                "stream": False
            }
            
            print(f"\n🤖 发送查询: {query}")
            print("=" * 60)
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/planner/invoke",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Agent响应成功!")
                print(f"📝 回答:\n{result.get('output', '无响应内容')}")
                
                # 显示会话信息
                if 'session_id' in result:
                    print(f"\n� 会话ID: {result['session_id']}")
                
                return True
            else:
                print(f"❌ Agent调用失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Agent调用异常: {e}")
            return False
    
    def test_streaming_response(self, query: str) -> bool:
        """测试流式响应接口"""
        try:
            payload = {
                "input": query,
                "session_id": "test_session_123",
                "stream": True
            }
            
            print(f"\n🌊 测试流式响应: {query}")
            print("=" * 60)
            
            response = self.session.post(
                f"{self.base_url}/api/v1/ai/planner/invoke",  # 使用同一个invoke路由
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True
            )
            
            if response.status_code == 200:
                print("✅ 流式响应开始:")
                full_response = ""
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # 去掉 'data: ' 前缀
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                chunk = data.get('chunk', '')
                                if chunk:
                                    print(chunk, end='', flush=True)
                                    full_response += chunk
                            except json.JSONDecodeError:
                                continue
                
                print(f"\n\n✅ 流式响应完成! 总长度: {len(full_response)} 字符")
                return True
            else:
                print(f"❌ 流式响应失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 流式响应异常: {e}")
            return False

def main():
    """主测试函数"""
    print("🚀 AI留学规划师Agent API测试套件")
    print("=" * 60)
    
    tester = AgentAPITester()
    
    # 测试用例
    test_cases = [
        "你好，我想了解一下平台上有多少引路人？",
        "我想申请美国计算机科学硕士，能帮我找找相关的引路人吗？",
        "有什么语言学习相关的服务吗？价格在500元以内的",
        "请给我一些关于留学申请的建议"
    ]
    
    # 1. 健康检查
    print("🏥 步骤1: 健康检查")
    if not tester.test_health_check():
        print("❌ 健康检查失败，停止测试")
        return
    
    # 2. 测试普通调用
    print("\n📞 步骤2: 测试Agent普通调用")
    success_count = 0
    for i, query in enumerate(test_cases[:2], 1):  # 只测试前两个查询
        print(f"\n--- 测试用例 {i} ---")
        if tester.test_agent_invoke(query):
            success_count += 1
        time.sleep(2)  # 避免API限制
    
    # 3. 测试流式响应
    print("\n🌊 步骤3: 测试流式响应")
    if tester.test_streaming_response(test_cases[2]):
        success_count += 1
    
    # 结果总结
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    print(f"✅ 成功测试: {success_count + 1}/4")  # +1 是健康检查
    
    if success_count >= 2:
        print("🎉 AI留学规划师Agent API测试通过！")
        print("\n📝 使用说明:")
        print("- API文档: http://127.0.0.1:8001/docs")
        print("- 健康检查: GET /api/v1/ai/planner/health")
        print("- 普通调用: POST /api/v1/ai/planner/invoke")
        print("- 流式响应: POST /api/v1/ai/planner/stream")
    else:
        print("⚠️ 部分测试失败，请检查服务器状态和配置")

if __name__ == "__main__":
    main()
