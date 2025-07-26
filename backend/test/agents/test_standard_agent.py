#!/usr/bin/env python3
"""测试标准模式的Agent Graph"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.standard_agent import get_standard_agent

async def test_standard_agent():
    """测试标准模式的Agent"""
    print("🔍 测试标准模式Agent")
    print("=" * 50)
    
    # 获取Agent实例
    agent = get_standard_agent()
    
    # 测试查询
    test_query = "请搜索MIT计算机科学硕士申请的最新要求是什么？"
    
    print(f"📝 测试查询: {test_query}")
    print("-" * 30)
    
    try:
        # 准备输入
        input_data = {
            "input": test_query,
            "user_id": "test_user"
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
        print(f"消息数量: {metadata.get('messages_count', 0)}")
        
        # 检查是否有错误
        if 'error' in metadata:
            print(f"❌ 错误: {metadata['error']}")
        else:
            print("✅ 执行成功!")
        
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_standard_agent())
