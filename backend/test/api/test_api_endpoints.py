#!/usr/bin/env python3
"""
AI留学规划师API快速测试脚本
测试API端点的功能和响应
"""
import requests
import json
import time
from typing import Dict, Any

class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/v1/advanced-planner"
        
    def test_health_check(self) -> bool:
        """测试健康检查端点"""
        print("🏥 测试健康检查端点")
        try:
            response = requests.get(f"{self.api_endpoint}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过")
                print(f"   状态: {data.get('status', 'unknown')}")
                print(f"   服务: {data.get('service', 'unknown')}")
                print(f"   版本: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败: API服务未启动")
            print("💡 请先启动API服务: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
            return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_basic_invoke(self) -> bool:
        """测试基础调用"""
        print("\n💬 测试基础API调用")
        
        test_request = {
            "input": "我想申请美国的计算机科学硕士，需要什么条件？",
            "user_id": "api_test_user",
            "session_id": "api_test_session",
            "chat_history": [],
            "stream": False
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_endpoint}/invoke",
                json=test_request,
                timeout=30
            )
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API调用成功")
                print(f"   执行时间: {execution_time:.2f}秒")
                print(f"   响应长度: {len(data.get('output', ''))}字符")
                print(f"   会话ID: {data.get('session_id', 'N/A')}")
                
                metadata = data.get('metadata', {})
                if metadata:
                    print(f"   LangSmith: {'启用' if metadata.get('langsmith_enabled') else '未启用'}")
                    print(f"   工具调用: {metadata.get('tool_calls', 0)}次")
                
                # 显示响应预览
                output = data.get('output', '')
                preview = output[:200] + "..." if len(output) > 200 else output
                print(f"   响应预览: {preview}")
                
                return True
            else:
                print(f"❌ API调用失败: HTTP {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时（>30秒）")
            return False
        except Exception as e:
            print(f"❌ API调用异常: {e}")
            return False
    
    def test_conversation_continuity(self) -> bool:
        """测试对话连续性"""
        print("\n🔄 测试对话连续性")
        
        conversation_steps = [
            {
                "input": "我想申请美国的研究生",
                "description": "初始咨询"
            },
            {
                "input": "我的专业是计算机科学，GPA是3.7",
                "description": "提供背景信息"
            },
            {
                "input": "你觉得我应该申请哪些学校？",
                "description": "请求具体建议"
            }
        ]
        
        chat_history = []
        session_id = "continuity_test_session"
        
        for i, step in enumerate(conversation_steps, 1):
            print(f"\n💬 对话步骤 {i}: {step['description']}")
            print(f"   输入: {step['input']}")
            
            request_data = {
                "input": step["input"],
                "user_id": "continuity_test_user",
                "session_id": session_id,
                "chat_history": chat_history,
                "stream": False
            }
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_endpoint}/invoke",
                    json=request_data,
                    timeout=30
                )
                execution_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    output = data.get('output', '')
                    
                    # 更新对话历史
                    chat_history.extend([
                        {"role": "user", "content": step["input"]},
                        {"role": "assistant", "content": output}
                    ])
                    
                    print(f"   ✅ 成功 ({execution_time:.2f}秒)")
                    print(f"   响应长度: {len(output)}字符")
                    
                    # 简短预览
                    preview = output[:100] + "..." if len(output) > 100 else output
                    print(f"   响应预览: {preview}")
                    
                else:
                    print(f"   ❌ 失败: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                return False
        
        print(f"\n✅ 对话连续性测试完成，共 {len(chat_history)} 条消息")
        return True
    
    def test_stream_response(self) -> bool:
        """测试流式响应"""
        print("\n🌊 测试流式响应")
        
        request_data = {
            "input": "请详细介绍一下申请美国研究生的完整流程",
            "user_id": "stream_test_user",
            "session_id": "stream_test_session",
            "chat_history": [],
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.api_endpoint}/invoke",
                json=request_data,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✅ 开始接收流式数据...")
                
                chunk_count = 0
                total_content = ""
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # 移除 'data: ' 前缀
                            
                            if data_str == '[DONE]':
                                print("\n✅ 流式响应完成")
                                break
                            
                            try:
                                data = json.loads(data_str)
                                chunk_type = data.get('type', 'unknown')
                                
                                if chunk_type == 'chunk':
                                    chunk_content = data.get('chunk', '')
                                    total_content += chunk_content
                                    chunk_count += 1
                                    print(f"📦 数据块 {chunk_count}: {len(chunk_content)}字符")
                                elif chunk_type == 'start':
                                    print(f"🚀 {data.get('message', '开始处理')}")
                                elif chunk_type == 'end':
                                    print(f"🏁 处理完成")
                                elif chunk_type == 'tool':
                                    print(f"🔧 {data.get('message', '工具调用中')}")
                                    
                            except json.JSONDecodeError:
                                continue
                
                print(f"📊 流式响应统计:")
                print(f"   数据块数量: {chunk_count}")
                print(f"   总内容长度: {len(total_content)}字符")
                
                return True
            else:
                print(f"❌ 流式响应失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 流式响应异常: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        print("\n🚨 测试错误处理")
        
        error_cases = [
            {
                "name": "空输入",
                "request": {
                    "input": "",
                    "user_id": "error_test",
                    "session_id": "error_session",
                    "stream": False
                },
                "expected_status": [400, 422]  # 可能的错误状态码
            },
            {
                "name": "缺少必填字段",
                "request": {
                    "user_id": "error_test",
                    "session_id": "error_session",
                    "stream": False
                    # 缺少 input 字段
                },
                "expected_status": [400, 422]
            }
        ]
        
        for case in error_cases:
            print(f"\n🧪 测试: {case['name']}")
            
            try:
                response = requests.post(
                    f"{self.api_endpoint}/invoke",
                    json=case["request"],
                    timeout=10
                )
                
                if response.status_code in case["expected_status"]:
                    print(f"   ✅ 正确返回错误状态: HTTP {response.status_code}")
                elif response.status_code == 200:
                    print(f"   ⚠️ 意外成功响应，可能错误处理不够严格")
                else:
                    print(f"   ❌ 意外状态码: HTTP {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ 测试异常: {e}")
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 AI留学规划师API测试")
        print("=" * 50)
        
        # 测试序列
        tests = [
            ("健康检查", self.test_health_check),
            ("基础调用", self.test_basic_invoke),
            ("对话连续性", self.test_conversation_continuity),
            ("流式响应", self.test_stream_response),
            ("错误处理", self.test_error_handling)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name}测试异常: {e}")
                results[test_name] = False
        
        # 汇总结果
        print("\n📊 测试结果汇总")
        print("=" * 30)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n🎯 总体结果: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 API测试通过！服务运行正常")
        else:
            print("⚠️ 部分测试失败，请检查API服务")

def main():
    """主函数"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
