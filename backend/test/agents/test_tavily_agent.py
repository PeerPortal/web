#!/usr/bin/env python3
"""
Tavily搜索工具在Agent中的实际测试
测试搜索工具与Agent的集成效果
"""
import os
import sys
import asyncio
import time
from pathlib import Path

# 设置环境变量
os.environ['TAVILY_API_KEY'] = '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'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = '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'
os.environ['LANGCHAIN_PROJECT'] = 'AI留学规划师'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class AgentSearchTester:
    """Agent搜索工具测试器"""
    
    def __init__(self):
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
            import traceback
            traceback.print_exc()
            return False
    
    def test_search_tool_directly(self):
        """直接测试搜索工具"""
        print("🔧 直接测试搜索工具")
        print("=" * 40)
        
        try:
            from app.agents.langgraph.agent_tools import get_search_tool
            
            search_tool = get_search_tool()
            print(f"✅ 搜索工具初始化成功")
            print(f"   工具名称: {search_tool.name}")
            print(f"   工具类型: {type(search_tool).__name__}")
            
            # 测试查询
            query = "2024 top 10 computer science universities USA ranking"
            print(f"🔍 测试查询: {query}")
            
            start_time = time.time()
            result = search_tool.run(query)
            execution_time = time.time() - start_time
            
            print(f"✅ 搜索完成，耗时: {execution_time:.2f}秒")
            print(f"📄 结果类型: {type(result)}")
            print(f"📄 结果长度: {len(str(result))}字符")
            
            # 处理不同类型的返回结果
            if isinstance(result, dict):
                print("📊 结构化结果:")
                if 'results' in result:
                    print(f"   搜索结果数: {len(result['results'])}")
                    for i, res in enumerate(result['results'][:2], 1):
                        print(f"   结果{i}: {res.get('title', 'N/A')}")
                        print(f"         URL: {res.get('url', 'N/A')}")
                        content_preview = res.get('content', '')[:100] + "..." if len(res.get('content', '')) > 100 else res.get('content', '')
                        print(f"         内容: {content_preview}")
            elif isinstance(result, list):
                print("📊 列表结果:")
                for i, item in enumerate(result[:2], 1):
                    if isinstance(item, dict):
                        print(f"   项目{i}: {item.get('title', str(item)[:50])}")
            else:
                print("📊 文本结果:")
                preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                print(f"   预览: {preview}")
            
            return True
            
        except Exception as e:
            print(f"❌ 搜索工具测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_agent_with_search_queries(self):
        """测试Agent处理需要搜索的查询"""
        print("\n🤖 测试Agent处理搜索查询")
        print("=" * 40)
        
        search_queries = [
            {
                "query": "2024年美国大学计算机科学专业排名前10的学校有哪些？",
                "description": "大学排名查询",
                "expected_search": True
            },
            {
                "query": "MIT计算机科学硕士申请的最新要求是什么？",
                "description": "具体大学申请要求",
                "expected_search": True
            },
            {
                "query": "斯坦福大学和MIT的计算机科学项目有什么区别？",
                "description": "大学对比查询",
                "expected_search": True
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(search_queries, 1):
            print(f"\n📝 测试 {i}: {test_case['description']}")
            print(f"查询: {test_case['query']}")
            
            try:
                start_time = time.time()
                
                result = await self.agent.ainvoke({
                    "input": test_case["query"],
                    "chat_history": [],
                    "user_id": f"search_test_user_{i}"
                })
                
                execution_time = time.time() - start_time
                
                if isinstance(result, dict):
                    output = result.get("output", "")
                    metadata = result.get("metadata", {})
                    tool_calls = metadata.get("tool_calls", 0)
                    
                    test_result = {
                        "query": test_case["query"],
                        "success": len(output) > 100,  # 至少100字符的回答
                        "execution_time": execution_time,
                        "output_length": len(output),
                        "tool_calls": tool_calls,
                        "used_search": tool_calls > 0,  # 假设工具调用包含搜索
                        "langsmith_enabled": metadata.get("langsmith_enabled", False)
                    }
                    
                    results.append(test_result)
                    
                    status = "✅" if test_result["success"] else "❌"
                    print(f"{status} 执行时间: {execution_time:.2f}秒")
                    print(f"📄 输出长度: {len(output)}字符") 
                    print(f"🔧 工具调用: {tool_calls}次")
                    print(f"🔍 使用搜索: {'是' if test_result['used_search'] else '否'}")
                    print(f"🔍 LangSmith: {'启用' if test_result['langsmith_enabled'] else '未启用'}")
                    
                    # 显示输出预览
                    preview = output[:300] + "..." if len(output) > 300 else output
                    print(f"📋 回答预览: {preview}")
                    
                else:
                    print(f"❌ 意外的结果类型: {type(result)}")
                    results.append({
                        "query": test_case["query"],
                        "success": False,
                        "error": f"意外结果类型: {type(result)}"
                    })
                    
            except Exception as e:
                print(f"❌ Agent测试失败: {e}")
                results.append({
                    "query": test_case["query"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def analyze_search_effectiveness(self, results):
        """分析搜索工具的有效性"""
        print("\n📊 搜索工具有效性分析")
        print("=" * 40)
        
        if not results:
            print("❌ 无测试结果可分析")
            return
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.get('success', False))
        tests_with_search = sum(1 for r in results if r.get('used_search', False))
        
        avg_execution_time = sum(r.get('execution_time', 0) for r in results) / total_tests
        avg_output_length = sum(r.get('output_length', 0) for r in results) / total_tests
        avg_tool_calls = sum(r.get('tool_calls', 0) for r in results) / total_tests
        
        print(f"📋 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功测试: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"   使用搜索: {tests_with_search} ({tests_with_search/total_tests*100:.1f}%)")
        print(f"   平均执行时间: {avg_execution_time:.2f}秒")
        print(f"   平均输出长度: {avg_output_length:.0f}字符")
        print(f"   平均工具调用: {avg_tool_calls:.1f}次")
        
        print(f"\n🎯 搜索工具评估:")
        if tests_with_search >= total_tests * 0.8:
            print("✅ 搜索工具调用频率: 优秀")
        elif tests_with_search >= total_tests * 0.5:
            print("⚠️ 搜索工具调用频率: 一般")
        else:
            print("❌ 搜索工具调用频率: 较低")
        
        if avg_execution_time < 10:
            print("✅ 搜索响应速度: 优秀")
        elif avg_execution_time < 20:
            print("⚠️ 搜索响应速度: 一般")
        else:
            print("❌ 搜索响应速度: 较慢")
        
        if successful_tests >= total_tests * 0.8:
            print("✅ 整体成功率: 优秀")
        elif successful_tests >= total_tests * 0.6:
            print("⚠️ 整体成功率: 一般")
        else:
            print("❌ 整体成功率: 需改进")
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 Tavily搜索工具综合测试")
        print("=" * 50)
        
        # 1. 直接测试搜索工具
        direct_test_success = self.test_search_tool_directly()
        
        if not direct_test_success:
            print("❌ 搜索工具直接测试失败，跳过Agent测试")
            return False
        
        # 2. 初始化Agent
        if not await self.initialize_agent():
            print("❌ Agent初始化失败，无法进行Agent搜索测试")
            return False
        
        # 3. 测试Agent使用搜索
        agent_results = await self.test_agent_with_search_queries()
        
        # 4. 分析结果
        self.analyze_search_effectiveness(agent_results)
        
        print(f"\n🎉 Tavily搜索工具综合测试完成！")
        return True

async def main():
    """主函数"""
    tester = AgentSearchTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
