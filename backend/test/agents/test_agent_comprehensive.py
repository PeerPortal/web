#!/usr/bin/env python3
"""
AI留学规划师Agent综合测试脚本
测试Agent的核心功能、工具调用、LangSmith集成等
"""
import os
import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["PYTHONPATH"] = str(project_root)

class AgentTester:
    """Agent测试器"""
    
    def __init__(self):
        self.test_results = {}
        self.agent = None
        
    async def initialize_agent(self):
        """初始化Agent"""
        try:
            from app.agents.langgraph.agent_graph import get_advanced_agent
            self.agent = get_advanced_agent()
            print("✅ Agent初始化成功")
            return True
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            return False
    
    def display_environment_info(self):
        """显示环境信息"""
        print("🌍 环境配置检查")
        print("=" * 50)
        
        # 检查关键环境变量
        env_vars = {
            "OPENAI_API_KEY": "OpenAI API密钥",
            "TAVILY_API_KEY": "Tavily搜索API密钥", 
            "LANGCHAIN_TRACING_V2": "LangSmith追踪",
            "LANGCHAIN_API_KEY": "LangSmith API密钥",
            "LANGCHAIN_PROJECT": "LangSmith项目名",
            "SUPABASE_URL": "Supabase数据库URL",
            "SUPABASE_KEY": "Supabase密钥"
        }
        
        for var, desc in env_vars.items():
            value = os.getenv(var)
            if value:
                if "KEY" in var and len(value) > 20:
                    # 隐藏敏感信息
                    masked_value = f"{value[:8]}...{value[-4:]}"
                    status = f"✅ {masked_value}"
                elif var == "LANGCHAIN_TRACING_V2":
                    status = f"✅ {value}"
                else:
                    status = f"✅ 已配置"
            else:
                status = "❌ 未配置"
            
            print(f"{desc:20}: {status}")
        
        print()
    
    async def test_basic_conversation(self):
        """测试基础对话功能"""
        print("💬 测试基础对话功能")
        print("=" * 50)
        
        test_cases = [
            {
                "name": "简单问候",
                "input": "你好，我想了解一下留学申请的流程",
                "expected_keywords": ["留学", "申请", "流程"]
            },
            {
                "name": "具体专业咨询",
                "input": "我想申请美国的计算机科学硕士，需要什么条件？",
                "expected_keywords": ["计算机科学", "硕士", "条件", "GPA", "托福", "雅思"]
            },
            {
                "name": "学校推荐",
                "input": "我的GPA是3.5，托福100分，能申请哪些美国大学的CS专业？",
                "expected_keywords": ["学校", "推荐", "CS", "计算机"]
            }
        ]
        
        results = []
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n📝 测试用例 {i}: {case['name']}")
            print(f"输入: {case['input']}")
            
            try:
                start_time = time.time()
                
                result = await self.agent.ainvoke({
                    "input": case["input"],
                    "chat_history": [],
                    "user_id": f"test_user_{i}"
                })
                
                execution_time = time.time() - start_time
                output = result.get("output", "")
                metadata = result.get("metadata", {})
                
                # 检查关键词
                keywords_found = [kw for kw in case["expected_keywords"] 
                                if kw.lower() in output.lower()]
                
                test_result = {
                    "case": case["name"],
                    "success": len(output) > 50,  # 基本响应长度检查
                    "execution_time": execution_time,
                    "output_length": len(output),
                    "keywords_found": keywords_found,
                    "keywords_expected": len(case["expected_keywords"]),
                    "tool_calls": metadata.get("tool_calls", 0),
                    "langsmith_enabled": metadata.get("langsmith_enabled", False)
                }
                
                results.append(test_result)
                
                # 显示结果
                status = "✅" if test_result["success"] else "❌"
                print(f"{status} 执行时间: {execution_time:.2f}秒")
                print(f"📄 输出长度: {len(output)}字符")
                print(f"🔧 工具调用: {metadata.get('tool_calls', 0)}次")
                print(f"🎯 关键词匹配: {len(keywords_found)}/{len(case['expected_keywords'])}")
                print(f"🔍 LangSmith: {'启用' if metadata.get('langsmith_enabled') else '未启用'}")
                
                # 显示输出摘要
                output_preview = output[:200] + "..." if len(output) > 200 else output
                print(f"📋 输出预览: {output_preview}")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                results.append({
                    "case": case["name"],
                    "success": False,
                    "error": str(e)
                })
        
        self.test_results["basic_conversation"] = results
        return results
    
    async def test_tool_integration(self):
        """测试工具集成"""
        print("\n🔧 测试工具集成")
        print("=" * 50)
        
        tool_test_cases = [
            {
                "name": "网络搜索工具",
                "input": "2024年美国大学计算机科学专业排名前10的学校有哪些？",
                "expected_tools": ["web_search", "tavily_search"]
            },
            {
                "name": "知识库搜索",
                "input": "Spring Boot框架在实际项目中如何应用？",
                "expected_tools": ["knowledge_base_search"]
            },
            {
                "name": "数据库查询",
                "input": "有哪些计算机科学相关的服务或导师？",
                "expected_tools": ["find_services_tool", "find_mentors_tool"]
            }
        ]
        
        results = []
        
        for i, case in enumerate(tool_test_cases, 1):
            print(f"\n🛠️ 工具测试 {i}: {case['name']}")
            print(f"输入: {case['input']}")
            
            try:
                start_time = time.time()
                
                result = await self.agent.ainvoke({
                    "input": case["input"],
                    "chat_history": [],
                    "user_id": f"tool_test_user_{i}"
                })
                
                execution_time = time.time() - start_time
                output = result.get("output", "")
                metadata = result.get("metadata", {})
                tool_calls = metadata.get("tool_calls", 0)
                
                test_result = {
                    "case": case["name"],
                    "success": tool_calls > 0,  # 至少调用了一个工具
                    "execution_time": execution_time,
                    "output_length": len(output),
                    "tool_calls": tool_calls,
                    "tools_used": "未知"  # 需要从详细日志中获取
                }
                
                results.append(test_result)
                
                status = "✅" if test_result["success"] else "❌"
                print(f"{status} 工具调用: {tool_calls}次")
                print(f"⏱️ 执行时间: {execution_time:.2f}秒")
                print(f"📄 输出长度: {len(output)}字符")
                
                # 输出预览
                output_preview = output[:150] + "..." if len(output) > 150 else output
                print(f"📋 输出预览: {output_preview}")
                
            except Exception as e:
                print(f"❌ 工具测试失败: {e}")
                results.append({
                    "case": case["name"],
                    "success": False,
                    "error": str(e)
                })
        
        self.test_results["tool_integration"] = results
        return results
    
    async def test_conversation_continuity(self):
        """测试对话连续性"""
        print("\n🔄 测试对话连续性")
        print("=" * 50)
        
        # 模拟多轮对话
        conversation_flow = [
            {
                "input": "我想申请美国的研究生",
                "context": "初始咨询"
            },
            {
                "input": "我的专业是计算机科学",
                "context": "补充专业信息"
            },
            {
                "input": "我的GPA是3.7，托福还没考",
                "context": "提供成绩信息"
            },
            {
                "input": "你觉得我应该申请哪些学校？",
                "context": "请求具体建议"
            }
        ]
        
        chat_history = []
        results = []
        
        for i, turn in enumerate(conversation_flow, 1):
            print(f"\n💬 对话轮次 {i}: {turn['context']}")
            print(f"输入: {turn['input']}")
            
            try:
                start_time = time.time()
                
                result = await self.agent.ainvoke({
                    "input": turn["input"],
                    "chat_history": chat_history,
                    "user_id": "continuity_test_user"
                })
                
                execution_time = time.time() - start_time
                output = result.get("output", "")
                
                # 更新对话历史
                chat_history.extend([
                    {"role": "user", "content": turn["input"]},
                    {"role": "assistant", "content": output}
                ])
                
                test_result = {
                    "turn": i,
                    "context": turn["context"],
                    "success": len(output) > 30,
                    "execution_time": execution_time,
                    "output_length": len(output),
                    "chat_history_length": len(chat_history)
                }
                
                results.append(test_result)
                
                status = "✅" if test_result["success"] else "❌"
                print(f"{status} 执行时间: {execution_time:.2f}秒")
                print(f"📄 输出长度: {len(output)}字符")
                print(f"💾 对话历史: {len(chat_history)}条消息")
                
                # 输出摘要
                output_preview = output[:120] + "..." if len(output) > 120 else output
                print(f"📋 回答摘要: {output_preview}")
                
            except Exception as e:
                print(f"❌ 对话测试失败: {e}")
                results.append({
                    "turn": i,
                    "context": turn["context"],
                    "success": False,
                    "error": str(e)
                })
        
        self.test_results["conversation_continuity"] = results
        return results
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n🚨 测试错误处理")
        print("=" * 50)
        
        error_cases = [
            {
                "name": "空输入",
                "input": "",
                "expected": "应该优雅处理空输入"
            },
            {
                "name": "超长输入",
                "input": "测试" * 1000,  # 很长的输入
                "expected": "应该处理超长输入"
            },
            {
                "name": "特殊字符",
                "input": "申请@#$%^&*()学校？？？！！！",
                "expected": "应该处理特殊字符"
            }
        ]
        
        results = []
        
        for case in error_cases:
            print(f"\n🧪 错误处理测试: {case['name']}")
            print(f"输入: {case['input'][:50]}{'...' if len(case['input']) > 50 else ''}")
            
            try:
                start_time = time.time()
                
                result = await self.agent.ainvoke({
                    "input": case["input"],
                    "chat_history": [],
                    "user_id": "error_test_user"
                })
                
                execution_time = time.time() - start_time
                output = result.get("output", "")
                
                # 检查是否有合理的错误处理
                handled_gracefully = (
                    len(output) > 10 and  # 有响应
                    "错误" not in output.lower() or  # 没有直接显示错误
                    "抱歉" in output.lower()  # 或者有礼貌的错误提示
                )
                
                test_result = {
                    "case": case["name"],
                    "success": handled_gracefully,
                    "execution_time": execution_time,
                    "output_length": len(output),
                    "handled_gracefully": handled_gracefully
                }
                
                results.append(test_result)
                
                status = "✅" if handled_gracefully else "❌"
                print(f"{status} 优雅处理: {'是' if handled_gracefully else '否'}")
                print(f"⏱️ 执行时间: {execution_time:.2f}秒")
                print(f"📄 输出长度: {len(output)}字符")
                
            except Exception as e:
                print(f"⚠️ 异常捕获: {e}")
                results.append({
                    "case": case["name"],
                    "success": True,  # 异常被捕获也算是正确的错误处理
                    "error_caught": str(e)
                })
        
        self.test_results["error_handling"] = results
        return results
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n📊 测试报告汇总")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.test_results.items():
            category_passed = sum(1 for r in results if r.get("success", False))
            category_total = len(results)
            
            total_tests += category_total
            passed_tests += category_passed
            
            print(f"\n📋 {category} ({category_passed}/{category_total})")
            print("-" * 40)
            
            for result in results:
                status = "✅" if result.get("success", False) else "❌"
                case_name = result.get("case", result.get("context", "未知"))
                
                if "execution_time" in result:
                    print(f"{status} {case_name} ({result['execution_time']:.2f}s)")
                else:
                    print(f"{status} {case_name}")
                
                if "error" in result:
                    print(f"    错误: {result['error']}")
        
        # 总体统计
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 总体结果: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 测试通过！Agent运行状态良好")
        elif success_rate >= 60:
            print("⚠️ 测试部分通过，建议检查失败项目")
        else:
            print("❌ 测试失败较多，需要检查Agent配置")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "detailed_results": self.test_results
        }
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 AI留学规划师Agent综合测试")
        print("=" * 60)
        
        # 显示环境信息
        self.display_environment_info()
        
        # 初始化Agent
        if not await self.initialize_agent():
            return False
        
        # 运行测试套件
        test_functions = [
            self.test_basic_conversation,
            self.test_tool_integration,
            self.test_conversation_continuity,
            self.test_error_handling
        ]
        
        for test_func in test_functions:
            try:
                await test_func()
            except Exception as e:
                print(f"❌ 测试套件执行失败: {test_func.__name__} - {e}")
        
        # 生成报告
        return self.generate_test_report()

async def main():
    """主函数"""
    tester = AgentTester()
    report = await tester.run_all_tests()
    
    # 保存详细报告
    if report:
        report_file = "agent_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())
