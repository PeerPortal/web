#!/usr/bin/env python3
"""
诊断Agent工具调用问题
深入分析为什么Agent不使用知识库
"""

import asyncio
import json
from app.agents.langgraph.standard_agent import StandardPlannerAgent
from app.agents.langgraph.query_classifier import QueryClassifier

class DiagnosticAgent(StandardPlannerAgent):
    def _call_model(self, state):
        """重写模型调用方法，添加诊断信息"""
        print(f"\n🔍 诊断信息:")
        
        # 获取用户消息
        user_message = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'content') and isinstance(msg.content, str):
                user_message = msg.content
                break
        
        print(f"   用户查询: {user_message}")
        
        # 查询分类和智能提示
        enhanced_prompt = self._get_enhanced_system_prompt(user_message)
        print(f"   系统提示长度: {len(enhanced_prompt)} 字符")
        print(f"   系统提示开头: {enhanced_prompt[:200]}...")
        
        messages = [{"role": "system", "content": enhanced_prompt}] + state["messages"]
        print(f"   发送给模型的消息数: {len(messages)}")
        
        # 调用模型
        response = self.llm_with_tools.invoke(messages)
        print(f"   模型响应类型: {type(response)}")
        print(f"   工具调用数量: {len(response.tool_calls) if response.tool_calls else 0}")
        
        if response.tool_calls:
            for i, tool_call in enumerate(response.tool_calls):
                print(f"   工具调用 {i+1}: {tool_call.get('name', 'Unknown')}")
                print(f"   工具参数: {tool_call.get('args', {})}")
        else:
            print(f"   无工具调用，直接回答")
            print(f"   回答内容: {str(response.content)[:100]}...")
        
        return {"messages": [response]}

async def diagnose_single_query():
    """诊断单个查询的完整执行过程"""
    print("🚀 诊断Agent工具调用问题")
    print("=" * 60)
    
    # 创建诊断Agent
    agent = DiagnosticAgent()
    
    # 测试查询
    query = "推荐信怎么准备？"
    print(f"🔍 测试查询: {query}")
    
    try:
        result = await agent.ainvoke({
            "input": query,
            "user_id": "diagnostic_test"
        })
        
        print(f"\n📊 最终结果:")
        print(f"   消息数量: {len(result.get('messages', []))}")
        
        # 分析每条消息
        for i, msg in enumerate(result.get('messages', [])):
            print(f"   消息 {i+1}: {type(msg)}")
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"      包含工具调用: {[tc.get('name') for tc in msg.tool_calls]}")
            if hasattr(msg, 'content'):
                content_preview = str(msg.content)[:100] if msg.content else "无内容"
                print(f"      内容预览: {content_preview}...")
        
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_tool_availability():
    """测试工具是否可用"""
    print("\n🔧 测试工具可用性")
    print("-" * 40)
    
    agent = StandardPlannerAgent()
    
    # 检查工具绑定
    if hasattr(agent, 'llm_with_tools'):
        print("✅ llm_with_tools 存在")
        
        # 检查绑定的工具
        if hasattr(agent.llm_with_tools, 'bound'):
            bound_tools = getattr(agent.llm_with_tools, 'bound', {})
            print(f"   绑定的工具信息: {type(bound_tools)}")
        
        # 尝试获取工具列表
        try:
            # 检查是否有tools属性
            if hasattr(agent.llm_with_tools, 'tools'):
                tools = agent.llm_with_tools.tools
                print(f"   工具数量: {len(tools) if tools else 0}")
                if tools:
                    for tool in tools:
                        tool_name = getattr(tool, 'name', 'Unknown')
                        print(f"   - {tool_name}")
        except Exception as e:
            print(f"   获取工具列表失败: {e}")
    
    else:
        print("❌ llm_with_tools 不存在")

if __name__ == "__main__":
    asyncio.run(test_tool_availability())
    asyncio.run(diagnose_single_query())
