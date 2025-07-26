#!/usr/bin/env python3
"""
优化后的RAG系统提示测试
验证强化后的知识库优先策略
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.standard_agent import get_standard_agent

async def test_enhanced_rag_prompts():
    """测试优化后的RAG系统提示"""
    print("🚀 优化后的RAG系统提示测试")
    print("=" * 60)
    
    agent = get_standard_agent()
    
    # 测试各种触发知识库的场景
    test_cases = [
        {
            "category": "具体案例查询",
            "queries": [
                "有什么成功申请CMU的案例吗？",
                "知识库里有GPA 3.8的申请案例吗？",
                "告诉我一个托福105分的申请故事"
            ]
        },
        {
            "category": "文档相关查询", 
            "queries": [
                "根据上传的文档，推荐信怎么准备？",
                "文档里有关于面试的建议吗？",
                "知识库里关于文书写作有什么技巧？"
            ]
        },
        {
            "category": "具体数据查询",
            "queries": [
                "申请MIT需要什么GPA？",
                "Stanford申请案例中的托福分数是多少？",
                "计算机科学申请的平均GRE分数是？"
            ]
        },
        {
            "category": "对比测试",
            "queries": [
                "美国研究生申请需要什么条件？",  # 通用问题，可能不用知识库
                "给我一些申请建议",  # 通用问题
                "最新的美国大学排名是什么？"  # 应该用网络搜索
            ]
        }
    ]
    
    total_tests = 0
    kb_usage_count = 0
    
    for category_info in test_cases:
        category = category_info["category"]
        queries = category_info["queries"]
        
        print(f"\n📋 {category}")
        print("-" * 40)
        
        for i, query in enumerate(queries, 1):
            total_tests += 1
            
            print(f"\n🔍 测试 {i}: {query}")
            
            try:
                result = await agent.ainvoke({
                    "input": query,
                    "user_id": f"enhanced_test_{total_tests}"
                })
                
                output = result.get('output', '')
                metadata = result.get('metadata', {})
                
                # 判断是否使用了知识库
                used_kb = ('知识库' in output or 
                          '来源' in output or 
                          '📖' in output or
                          'CMU MSCS' in output or
                          'UC Berkeley EECS' in output or
                          'GPA：3.8' in output or
                          '托福：105' in output)
                
                if used_kb:
                    kb_usage_count += 1
                    status = "✅ 使用知识库"
                else:
                    status = "⚠️ 未使用知识库"
                
                print(f"   {status}")
                print(f"   回答长度: {len(output)}字符")
                print(f"   预览: {output[:100]}...")
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
            
            await asyncio.sleep(0.5)
    
    # 总结报告
    print(f"\n📊 优化后RAG测试总结")
    print("=" * 40)
    print(f"总测试数: {total_tests}")
    print(f"知识库使用次数: {kb_usage_count}")
    print(f"知识库使用率: {kb_usage_count/total_tests*100:.1f}%")
    
    # 评估效果
    usage_rate = kb_usage_count / total_tests
    if usage_rate >= 0.7:
        grade = "优秀"
        emoji = "🏆"
        comment = "系统提示优化效果显著，Agent能够正确识别并优先使用知识库"
    elif usage_rate >= 0.5:
        grade = "良好"
        emoji = "👍"
        comment = "系统提示优化有效，知识库使用率明显提升"
    elif usage_rate >= 0.3:
        grade = "一般"
        emoji = "🤔"
        comment = "系统提示有一定效果，但仍需进一步优化"
    else:
        grade = "需要改进"
        emoji = "⚠️"
        comment = "系统提示优化效果不明显，需要重新设计策略"
    
    print(f"\n{emoji} 优化效果评价: {grade}")
    print(f"   {comment}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_rag_prompts())
