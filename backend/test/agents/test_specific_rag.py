#!/usr/bin/env python3
"""
更具体的RAG测试 - 明确指向知识库内容
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.standard_agent import get_standard_agent

async def test_specific_rag_queries():
    """测试具体的RAG查询"""
    print("🎯 更具体的RAG测试")
    print("=" * 50)
    
    agent = get_standard_agent()
    
    # 更具体的测试查询
    specific_queries = [
        {
            "query": "从你的知识库中找到关于CMU和Stanford申请的具体案例信息。",
            "name": "具体学校案例查询"
        },
        {
            "query": "请使用知识库检索工具，查找关于GPA 3.8申请成功的案例。",
            "name": "明确要求使用工具"
        },
        {
            "query": "知识库里有什么关于托福105分申请结果的信息？",
            "name": "具体分数查询"
        },
        {
            "query": "根据知识库中的成功案例，计算机科学申请者的背景是什么？",
            "name": "背景信息提取"
        },
        {
            "query": "请调用knowledge_base_retriever工具，查找推荐信准备的详细步骤。",
            "name": "明确工具调用"
        }
    ]
    
    for i, test_query in enumerate(specific_queries, 1):
        print(f"\n🔍 测试 {i}: {test_query['name']}")
        print(f"📝 查询: {test_query['query']}")
        print("-" * 40)
        
        try:
            result = await agent.ainvoke({
                "input": test_query["query"],
                "user_id": f"specific_test_{i}"
            })
            
            output = result.get('output', '')
            metadata = result.get('metadata', {})
            
            # 判断是否使用了知识库
            used_kb = ('知识库' in output or 
                      '来源' in output or 
                      '📖' in output or
                      'CMU MSCS' in output or
                      'UC Berkeley EECS' in output)
            
            print(f"📊 消息数量: {metadata.get('messages_count', 0)}")
            print(f"🔍 使用知识库: {'是' if used_kb else '否'}")
            print(f"📄 回答长度: {len(output)}字符")
            print(f"📝 回答预览: {output[:200]}...")
            
            if used_kb:
                print("✅ 成功使用知识库")
            else:
                print("⚠️ 未使用知识库")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_specific_rag_queries())
