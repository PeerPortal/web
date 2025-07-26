#!/usr/bin/env python3
"""
知识库检索工具 (RAG) 测试
验证Agent能否从私有文档中准确检索信息
"""

import asyncio
import sys
import os
import time
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.standard_agent import get_standard_agent
from app.agents.langgraph.knowledge_base import knowledge_manager

class RAGTester:
    """知识库检索(RAG)测试器"""
    
    def __init__(self):
        self.agent = get_standard_agent()
        self.test_results = []
    
    def check_knowledge_base_status(self) -> Dict[str, Any]:
        """检查知识库状态"""
        print("🔍 检查知识库状态")
        print("-" * 40)
        
        try:
            stats = knowledge_manager.get_knowledge_base_stats()
            
            print(f"📁 文档数量: {stats['files_count']}")
            print(f"🧠 向量库状态: {'已建立' if stats['vector_store_exists'] else '未建立'}")
            
            if stats['files']:
                print("📚 已上传的文档:")
                for file in stats['files']:
                    print(f"  • {file}")
            
            return stats
            
        except Exception as e:
            print(f"❌ 检查知识库状态失败: {e}")
            return {"files_count": 0, "vector_store_exists": False, "files": []}
    
    async def test_direct_retrieval(self, query: str, test_name: str) -> Dict[str, Any]:
        """直接测试知识库检索工具"""
        print(f"\n🔧 直接测试知识库检索: {test_name}")
        print(f"📝 查询: {query}")
        print("-" * 50)
        
        try:
            from app.agents.langgraph.knowledge_base import knowledge_base_retriever
            
            start_time = time.time()
            results = knowledge_base_retriever.invoke({"query": query})
            execution_time = time.time() - start_time
            
            print(f"⏱️  检索时间: {execution_time:.2f}秒")
            print(f"📊 结果数量: {len(results)}")
            
            if results:
                print("📖 检索结果:")
                for i, result in enumerate(results, 1):
                    print(f"\n结果 {i}:")
                    print(result[:300] + "..." if len(result) > 300 else result)
            else:
                print("📝 未找到相关结果")
            
            return {
                "test_name": test_name,
                "query": query,
                "success": True,
                "results_count": len(results),
                "execution_time": execution_time,
                "has_content": bool(results and any(len(r) > 50 for r in results)),
                "results": results
            }
            
        except Exception as e:
            print(f"❌ 直接检索失败: {e}")
            return {
                "test_name": test_name,
                "query": query,
                "success": False,
                "error": str(e)
            }
    
    async def test_agent_with_retrieval(self, query: str, test_name: str) -> Dict[str, Any]:
        """测试Agent使用知识库检索"""
        print(f"\n🤖 测试Agent知识库使用: {test_name}")
        print(f"📝 查询: {query}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = await self.agent.ainvoke({
                "input": query,
                "user_id": f"rag_test_{test_name.lower().replace(' ', '_')}"
            })
            execution_time = time.time() - start_time
            
            output = result.get('output', '')
            metadata = result.get('metadata', {})
            
            # 判断是否使用了知识库
            used_knowledge_base = ('知识库' in output or 
                                 '文档' in output or 
                                 '来源' in output or
                                 '根据' in output)
            
            print(f"⏱️  执行时间: {execution_time:.2f}秒")
            print(f"📊 消息数量: {metadata.get('messages_count', 0)}")
            print(f"🔍 使用知识库: {'是' if used_knowledge_base else '否'}")
            print(f"📄 回答长度: {len(output)}字符")
            print(f"📝 回答预览: {output[:300]}...")
            
            test_result = {
                "test_name": test_name,
                "query": query,
                "success": True,
                "output": output,
                "execution_time": execution_time,
                "messages_count": metadata.get('messages_count', 0),
                "used_knowledge_base": used_knowledge_base,
                "has_detailed_info": len(output) > 150,
                "error": None
            }
            
            self.test_results.append(test_result)
            return test_result
            
        except Exception as e:
            print(f"❌ Agent测试失败: {e}")
            test_result = {
                "test_name": test_name,
                "query": query,
                "success": False,
                "error": str(e)
            }
            self.test_results.append(test_result)
            return test_result
    
    async def run_comprehensive_rag_tests(self):
        """运行全面的RAG测试"""
        print("🚀 开始知识库检索(RAG)综合测试")
        print("=" * 60)
        
        # 1. 检查知识库状态
        kb_stats = self.check_knowledge_base_status()
        
        if kb_stats['files_count'] == 0:
            print("⚠️ 知识库为空，无法进行测试")
            return
        
        if not kb_stats['vector_store_exists']:
            print("⚠️ 向量库不存在，尝试重建...")
            try:
                knowledge_manager.load_and_embed_knowledge_base()
                print("✅ 向量库重建成功")
            except Exception as e:
                print(f"❌ 向量库重建失败: {e}")
                return
        
        # 2. 测试查询列表
        test_queries = [
            {
                "query": "总结一下知识库中关于留学申请的成功案例。",
                "name": "成功案例总结",
                "expected_kb_usage": True
            },
            {
                "query": "根据知识库的内容，留学申请文书写作有什么要点？",
                "name": "文书写作指导",
                "expected_kb_usage": True
            },
            {
                "query": "知识库里有哪些关于计算机科学专业申请的建议？",
                "name": "专业申请建议",
                "expected_kb_usage": True
            },
            {
                "query": "根据上传的文档，有什么关于面试准备的建议吗？",
                "name": "面试准备指导",
                "expected_kb_usage": True
            },
            {
                "query": "知识库状态如何？包含了哪些文档？",
                "name": "知识库状态查询",
                "expected_kb_usage": True
            }
        ]
        
        # 3. 先测试直接检索
        print(f"\n🔧 第一阶段：直接检索测试")
        print("=" * 40)
        
        direct_results = []
        for test_query in test_queries[:3]:  # 测试前3个查询
            result = await self.test_direct_retrieval(
                test_query["query"], 
                f"直接-{test_query['name']}"
            )
            direct_results.append(result)
            await asyncio.sleep(1)
        
        # 4. 再测试Agent集成
        print(f"\n🤖 第二阶段：Agent集成测试")
        print("=" * 40)
        
        for test_query in test_queries:
            await self.test_agent_with_retrieval(
                test_query["query"], 
                test_query["name"]
            )
            await asyncio.sleep(1)
        
        # 5. 生成测试报告
        self.generate_rag_report(direct_results)
    
    def generate_rag_report(self, direct_results: List[Dict]):
        """生成RAG测试报告"""
        print("\n" + "=" * 60)
        print("📊 知识库检索(RAG)测试报告")
        print("=" * 60)
        
        # Agent测试统计
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        kb_usage = sum(1 for r in self.test_results if r.get('used_knowledge_base', False))
        detailed_responses = sum(1 for r in self.test_results if r.get('has_detailed_info', False))
        
        if total_tests > 0:
            avg_execution_time = sum(r['execution_time'] for r in self.test_results if r['success']) / max(successful_tests, 1)
            avg_messages_count = sum(r.get('messages_count', 0) for r in self.test_results if r['success']) / max(successful_tests, 1)
        else:
            avg_execution_time = 0
            avg_messages_count = 0
        
        # 直接检索统计
        direct_successful = sum(1 for r in direct_results if r.get('success', False))
        direct_with_content = sum(1 for r in direct_results if r.get('has_content', False))
        
        print(f"📈 Agent集成测试统计:")
        print(f"  • 总测试数: {total_tests}")
        print(f"  • 成功测试: {successful_tests} ({successful_tests/max(total_tests,1)*100:.1f}%)")
        print(f"  • 知识库使用: {kb_usage} ({kb_usage/max(total_tests,1)*100:.1f}%)")
        print(f"  • 详细回答: {detailed_responses} ({detailed_responses/max(total_tests,1)*100:.1f}%)")
        print(f"  • 平均执行时间: {avg_execution_time:.2f}秒")
        print(f"  • 平均消息数: {avg_messages_count:.1f}条")
        
        print(f"\n📋 直接检索测试统计:")
        print(f"  • 成功检索: {direct_successful}/{len(direct_results)}")
        print(f"  • 有效内容: {direct_with_content}/{len(direct_results)}")
        
        print(f"\n📋 详细结果:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            kb_status = "📚" if result.get('used_knowledge_base') else "🌐"
            
            print(f"{i}. {status} {kb_status} {result['test_name']}")
            if result['success']:
                print(f"   执行时间: {result['execution_time']:.2f}s | "
                      f"消息数: {result.get('messages_count', 0)} | "
                      f"回答长度: {len(result.get('output', ''))}字符")
            else:
                print(f"   ❌ 错误: {result['error']}")
        
        # 评估等级
        if total_tests == 0:
            grade = "无法评估"
            emoji = "❓"
        else:
            success_rate = successful_tests / total_tests
            kb_usage_rate = kb_usage / total_tests
            
            if success_rate >= 0.8 and kb_usage_rate >= 0.6:
                grade = "优秀"
                emoji = "🏆"
            elif success_rate >= 0.6 and kb_usage_rate >= 0.4:
                grade = "良好"
                emoji = "👍"
            elif success_rate >= 0.4:
                grade = "一般"
                emoji = "🤔"
            else:
                grade = "需要改进"
                emoji = "⚠️"
        
        print(f"\n{emoji} RAG功能评价: {grade}")
        if grade != "无法评估":
            print(f"   Agent能够有效使用知识库进行信息检索和回答生成")

async def main():
    """主函数"""
    tester = RAGTester()
    await tester.run_comprehensive_rag_tests()

if __name__ == "__main__":
    asyncio.run(main())
