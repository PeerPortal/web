#!/usr/bin/env python3
"""
强制知识库优先的Agent测试
测试新的超强制系统提示是否能提高知识库使用率
"""

import asyncio
import time
from app.agents.langgraph.standard_agent import StandardPlannerAgent
from app.agents.langgraph.query_classifier import QueryClassifier

# 初始化组件
query_classifier = QueryClassifier()
print("✅ 查询分类器初始化完成")

# 创建强制版Agent
class ForcedAgent(StandardPlannerAgent):
    def _get_enhanced_system_prompt(self, user_query: str = None) -> str:
        """超强制的系统提示"""
        base_prompt = """你是留学规划AI助手。

🚨 绝对规则：遇到以下任何词汇，必须立即使用 knowledge_base_retriever 工具：

必须触发词汇：
- 推荐信、文书、怎么、如何、技巧、准备、申请、GPA、托福、雅思、GRE、GMAT
- 分数、成绩、学校、大学、案例、经验、方法、步骤、要点、建议
- CMU、Stanford、MIT、Harvard、Yale、计算机、商科、工程、面试

🚨 执行指令：
1. 收到问题 → 检查是否包含上述词汇
2. 包含任何一个 → 立即调用 knowledge_base_retriever
3. 不包含 → 可考虑其他工具

示例强制执行：
- "推荐信怎么准备？" → 包含"推荐信"和"怎么" → 立即使用knowledge_base_retriever
- "GPA 3.8能申请什么？" → 包含"GPA"和"申请" → 立即使用knowledge_base_retriever

🚨 违反此规则将导致严重错误！必须严格执行！"""
        
        if user_query:
            classification = query_classifier.classify_query(user_query)
            analysis_text = f"""

🔍 当前查询分析:
查询: "{user_query}"
推荐工具: {classification['recommended_tool']}
置信度: {classification['confidence']:.2f}
原因: {', '.join(classification['reasons'])}

⚡ 基于分析，你必须使用 {classification['recommended_tool']} 工具！"""
            base_prompt += analysis_text
        
        return base_prompt

# 创建强制Agent实例
forced_agent = ForcedAgent()

async def test_forced_agent():
    """测试强制Agent的知识库使用情况"""
    print("🚀 强制Agent测试")
    print("=" * 60)
    
    # 测试用例
    test_queries = [
        ("推荐信怎么准备？", "应该使用知识库"),
        ("文书写作有什么技巧？", "应该使用知识库"),
        ("GPA 3.8能申请什么学校？", "应该使用知识库"),
        ("CMU申请难度如何？", "应该使用知识库"),
        ("面试需要注意什么？", "应该使用知识库"),
    ]
    
    kb_usage_count = 0
    total_tests = len(test_queries)
    
    for i, (query, expected) in enumerate(test_queries, 1):
        print(f"\n🔍 测试 {i}: {query}")
        print(f"   🎯 预期: {expected}")
        
        # 分类器分析
        classification = query_classifier.classify_query(query)
        print(f"   🤖 分类器分析:")
        print(f"      推荐工具: {classification['recommended_tool']}")
        print(f"      置信度: {classification['confidence']:.2f}")
        print(f"      原因: {', '.join(classification['reasons'])}")
        
        # Agent执行
        start_time = time.time()
        try:
            result = await forced_agent.ainvoke({
                "input": query,
                "user_id": "test_user"
            })
            
            # 分析结果
            messages = result.get("messages", [])
            used_kb = any("knowledge_base_retriever" in str(msg) for msg in messages)
            
            if used_kb:
                kb_usage_count += 1
                print(f"   📊 实际结果: ✅ 使用了知识库")
            else:
                print(f"   📊 实际结果: ❌ 未使用知识库")
            
            # 获取最终回答
            final_answer = ""
            if messages:
                final_answer = str(messages[-1])[:200]
            
            execution_time = time.time() - start_time
            print(f"   📝 回答预览: {final_answer}...")
            print(f"   ⏱️  执行时间: {execution_time:.2f}秒")
            
        except Exception as e:
            print(f"   ❌ 执行错误: {str(e)}")
    
    # 统计结果
    usage_rate = (kb_usage_count / total_tests) * 100
    print(f"\n📊 强制Agent测试结果")
    print("=" * 40)
    print(f"总测试数: {total_tests}")
    print(f"知识库使用次数: {kb_usage_count}")
    print(f"知识库使用率: {usage_rate:.1f}%")
    
    if usage_rate >= 80:
        print("🎉 优秀！强制策略效果显著")
    elif usage_rate >= 50:
        print("👍 良好！有明显改善")
    else:
        print("⚠️ 仍需改进！强制策略效果有限")
    
    return usage_rate

if __name__ == "__main__":
    asyncio.run(test_forced_agent())
