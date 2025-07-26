#!/usr/bin/env python3
"""调试Agent Graph执行流程"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.agent_graph import get_advanced_agent
from app.core.config import settings

async def debug_agent_flow():
    """调试Agent Graph的执行流程"""
    print("🔍 调试Agent Graph执行流程")
    print("=" * 50)
    
    # 获取Agent实例
    agent = get_advanced_agent()
    
    # 测试查询
    test_query = "请搜索MIT计算机科学硕士申请的最新要求是什么？"
    
    print(f"📝 测试查询: {test_query}")
    print("-" * 30)
    
    try:
        # 准备输入
        input_data = {
            "input": test_query,
            "user_id": "debug_user",
            "chat_history": []
        }
        
        # 执行Agent
        print("🚀 开始执行Agent...")
        result = await agent.ainvoke(input_data)
        
        print("\n📊 执行结果:")
        print(f"输出: {result.get('output', 'No output')}")
        print(f"会话ID: {result.get('session_id', 'No session')}")
        
        # 检查元数据
        metadata = result.get('metadata', {})
        print(f"\n📈 元数据:")
        print(f"执行时间: {metadata.get('execution_time', 0):.2f}秒")
        print(f"工具调用次数: {metadata.get('tool_calls', 0)}")
        print(f"LangSmith启用: {metadata.get('langsmith_enabled', False)}")
        
        # 检查是否有错误
        if 'error' in metadata:
            print(f"❌ 错误: {metadata['error']}")
        
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent_flow())
