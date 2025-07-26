#!/usr/bin/env python3
"""
优化后的Agent测试 - 验证查询分类器效果
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.standard_agent import get_standard_agent
from app.agents.langgraph.query_classifier import query_classifier

async def test_optimized_agent():
    """测试优化后的Agent"""
    print("🚀 优化后的Agent测试")
    print("=" * 60)
    
    agent = get_standard_agent()
    
    # 测试用例 - 重点测试之前失败的隐含性查询
    test_cases = [
        {
            "category": "隐含性查询测试",
            "queries": [
                "推荐信怎么准备？",
                "文书写作有什么技巧？", 
                "面试需要注意什么？",
                "申请时间怎么安排？",
                "申请费用大概多少？"
            ],
            "expected_kb_usage": True
        },
        {
            "category": "具体分数查询",
            "queries": [
                "GPA 3.8能申请什么学校？",
                "托福105分够吗？",
                "GRE 325分申请CMU有希望吗？"
            ],
            "expected_kb_usage": True
        },
        {
            "category": "网络搜索查询",
            "queries": [
                "2024年最新排名",
                "最新申请政策变化",
                "今年录取率怎么样？"
            ],
            "expected_kb_usage": False
        }
    ]
    
    total_tests = 0
    kb_usage_count = 0
    correct_tool_usage = 0
    
    for category_info in test_cases:
        category = category_info["category"]
        queries = category_info["queries"]
        expected_kb = category_info["expected_kb_usage"]
        
        print(f"\n📋 {category}")
        print("-" * 40)
        
        for i, query in enumerate(queries, 1):
            total_tests += 1
            
            print(f"\n🔍 测试 {total_tests}: {query}")
            
            # 1. 首先显示分类器分析
            classification = query_classifier.classify_query(query)
            print(f"   🤖 分类器分析:")
            print(f"      推荐工具: {classification['recommended_tool']}")
            print(f"      置信度: {classification['confidence']:.2f}")
            print(f"      原因: {', '.join(classification['reasons'][:2])}")  # 只显示前两个原因
            
            try:
                # 2. 执行Agent查询
                result = await agent.ainvoke({
                    "input": query,
                    "user_id": f"optimized_test_{total_tests}"
                })
                
                output = result.get('output', '')
                metadata = result.get('metadata', {})
                
                # 3. 判断实际工具使用
                used_kb = ('知识库' in output or 
                          '来源' in output or 
                          '📖' in output or
                          'CMU MSCS' in output or
                          'UC Berkeley EECS' in output or
                          'GPA：3.8' in output or
                          '托福：105' in output)
                
                if used_kb:
                    kb_usage_count += 1
                    actual_status = "✅ 使用知识库"
                else:
                    actual_status = "⚠️ 未使用知识库"
                
                # 4. 检查是否符合预期
                if (used_kb and expected_kb) or (not used_kb and not expected_kb):
                    correct_tool_usage += 1
                    expectation_status = "✅ 符合预期"
                else:
                    expectation_status = "❌ 不符合预期"
                
                print(f"   📊 实际结果: {actual_status}")
                print(f"   🎯 预期评估: {expectation_status}")
                print(f"   📝 回答长度: {len(output)}字符")
                print(f"   ⏱️  执行时间: {metadata.get('execution_time', 0):.2f}秒")
                
            except Exception as e:
                print(f"   ❌ 测试失败: {e}")
            
            await asyncio.sleep(0.5)
    
    # 生成优化效果报告
    print(f"\n📊 优化效果总结")
    print("=" * 40)
    print(f"总测试数: {total_tests}")
    print(f"知识库使用次数: {kb_usage_count}")
    print(f"知识库使用率: {kb_usage_count/total_tests*100:.1f}%")
    print(f"正确工具选择: {correct_tool_usage}")
    print(f"工具选择准确率: {correct_tool_usage/total_tests*100:.1f}%")
    
    # 优化效果评估
    kb_usage_rate = kb_usage_count / total_tests
    tool_accuracy = correct_tool_usage / total_tests
    
    if kb_usage_rate >= 0.7 and tool_accuracy >= 0.8:
        grade = "优秀"
        emoji = "🏆"
        comment = "查询分类器显著提升了知识库使用率和工具选择准确性"
    elif kb_usage_rate >= 0.5 and tool_accuracy >= 0.6:
        grade = "良好"
        emoji = "👍"
        comment = "优化效果明显，知识库使用率有较大提升"
    elif kb_usage_rate >= 0.3:
        grade = "一般"
        emoji = "🤔"
        comment = "有一定改进，但仍需进一步优化"
    else:
        grade = "需要改进"
        emoji = "⚠️"
        comment = "优化效果不明显，需要调整策略"
    
    print(f"\n{emoji} 优化效果评价: {grade}")
    print(f"   {comment}")
    
    # 具体改进建议
    if kb_usage_rate < 0.7:
        print(f"\n💡 改进建议:")
        print(f"   - 扩展关键词库，增加更多触发词")
        print(f"   - 提高系统提示的强制性")
        print(f"   - 考虑添加更精确的语义分析")

if __name__ == "__main__":
    asyncio.run(test_optimized_agent())
