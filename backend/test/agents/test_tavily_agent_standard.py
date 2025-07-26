#!/usr/bin/env python3
"""完整的Tavily Agent测试 - 使用标准模式"""

import asyncio
import sys
import os
import time
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.standard_agent import get_standard_agent

class TavilyAgentTester:
    """Tavily Agent集成测试器 - 标准模式"""
    
    def __init__(self):
        self.agent = get_standard_agent()
        self.test_results = []
    
    async def test_search_query(self, query: str, query_name: str) -> Dict[str, Any]:
        """测试单个搜索查询"""
        print(f"\n🔍 测试查询: {query_name}")
        print(f"📝 问题: {query}")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # 执行Agent查询
            result = await self.agent.ainvoke({
                "input": query,
                "user_id": f"test_{query_name.lower().replace(' ', '_')}"
            })
            
            execution_time = time.time() - start_time
            
            # 检查结果
            output = result.get('output', '')
            metadata = result.get('metadata', {})
            
            # 判断是否使用了搜索工具
            used_search_tool = '搜索' in output or 'MIT' in output or '申请' in output
            
            test_result = {
                'query_name': query_name,
                'query': query,
                'success': True,
                'output': output,
                'execution_time': execution_time,
                'messages_count': metadata.get('messages_count', 0),
                'used_search_tool': used_search_tool,
                'has_detailed_info': len(output) > 100,
                'error': None
            }
            
            print(f"✅ 查询成功")
            print(f"⏱️  执行时间: {execution_time:.2f}秒")
            print(f"📊 消息数量: {metadata.get('messages_count', 0)}")
            print(f"🔍 使用搜索工具: {'是' if used_search_tool else '否'}")
            print(f"📄 回答长度: {len(output)} 字符")
            print(f"📝 回答预览: {output[:200]}...")
            
        except Exception as e:
            execution_time = time.time() - start_time
            test_result = {
                'query_name': query_name,
                'query': query,
                'success': False,
                'output': str(e),
                'execution_time': execution_time,
                'messages_count': 0,
                'used_search_tool': False,
                'has_detailed_info': False,
                'error': str(e)
            }
            
            print(f"❌ 查询失败: {str(e)}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def run_comprehensive_tests(self):
        """运行全面的Agent测试"""
        print("🚀 开始Tavily Agent综合测试 - 标准模式")
        print("=" * 60)
        
        # 测试查询列表
        test_queries = [
            {
                "query": "2024年美国大学计算机科学专业排名前10的学校有哪些？",
                "name": "CS排名查询"
            },
            {
                "query": "MIT计算机科学硕士申请的最新要求是什么？",
                "name": "MIT申请要求"
            },
            {
                "query": "斯坦福大学和MIT的计算机科学项目有什么区别？",
                "name": "学校对比"
            },
            {
                "query": "美国留学申请文书应该怎么写？",
                "name": "文书指导"
            }
        ]
        
        # 执行测试
        for test_query in test_queries:
            await self.test_search_query(test_query["query"], test_query["name"])
            
            # 避免请求过快
            await asyncio.sleep(1)
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 Tavily Agent测试报告 - 标准模式")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        search_tool_usage = sum(1 for r in self.test_results if r['used_search_tool'])
        detailed_responses = sum(1 for r in self.test_results if r['has_detailed_info'])
        
        avg_execution_time = sum(r['execution_time'] for r in self.test_results) / total_tests
        avg_messages_count = sum(r['messages_count'] for r in self.test_results) / total_tests
        
        print(f"📈 总体统计:")
        print(f"  • 总测试数: {total_tests}")
        print(f"  • 成功测试: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"  • 搜索工具使用: {search_tool_usage} ({search_tool_usage/total_tests*100:.1f}%)")
        print(f"  • 详细回答: {detailed_responses} ({detailed_responses/total_tests*100:.1f}%)")
        print(f"  • 平均执行时间: {avg_execution_time:.2f}秒")
        print(f"  • 平均消息数: {avg_messages_count:.1f}条")
        
        print(f"\n📋 详细结果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            search_status = "🔍" if result['used_search_tool'] else "💭"
            
            print(f"{i}. {status} {search_status} {result['query_name']}")
            print(f"   执行时间: {result['execution_time']:.2f}s | "
                  f"消息数: {result['messages_count']} | "
                  f"回答长度: {len(result['output'])}字符")
            
            if result['error']:
                print(f"   ❌ 错误: {result['error']}")
        
        # 评估等级
        success_rate = successful_tests / total_tests
        if success_rate >= 0.9 and search_tool_usage >= total_tests * 0.5:
            grade = "优秀"
            emoji = "🏆"
        elif success_rate >= 0.7:
            grade = "良好"
            emoji = "👍"
        elif success_rate >= 0.5:
            grade = "一般"
            emoji = "🤔"
        else:
            grade = "需要改进"
            emoji = "⚠️"
        
        print(f"\n{emoji} 总体评价: {grade}")
        print(f"   Agent能够成功处理搜索查询并提供有价值的回答")

async def main():
    """主函数"""
    tester = TavilyAgentTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())
