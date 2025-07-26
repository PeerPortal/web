#!/usr/bin/env python3
"""
LangSmith集成测试脚本
测试AI留学规划师Agent的LangSmith追踪功能
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["PYTHONPATH"] = str(project_root)

async def test_langsmith_config():
    """测试LangSmith配置模块"""
    print("=" * 60)
    print("🔧 测试LangSmith配置模块")
    print("=" * 60)
    
    try:
        from app.core.langsmith_config import (
            is_langsmith_enabled,
            study_abroad_tracer,
            study_abroad_evaluator,
            get_langsmith_callbacks
        )
        
        print(f"✅ LangSmith配置模块导入成功")
        print(f"🔍 LangSmith状态: {'启用' if is_langsmith_enabled() else '未启用'}")
        
        # 测试回调函数
        callbacks = get_langsmith_callbacks("test_user", "test_session")
        print(f"📞 获取回调函数: {len(callbacks) if callbacks else 0} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ LangSmith配置测试失败: {e}")
        return False

async def test_agent_integration():
    """测试Agent的LangSmith集成"""
    print("\n" + "=" * 60)
    print("🤖 测试Agent LangSmith集成")
    print("=" * 60)
    
    try:
        from app.agents.langgraph.agent_graph import get_advanced_agent
        from app.core.langsmith_config import is_langsmith_enabled, study_abroad_tracer
        
        agent = get_advanced_agent()
        print("✅ Agent实例创建成功")
        
        # 测试输入
        test_input = {
            "input": "我想申请美国的计算机科学硕士，请给我一些建议",
            "chat_history": [],
            "user_id": "test_user"
        }
        
        print(f"🔍 测试输入: {test_input['input']}")
        
        if is_langsmith_enabled():
            print("🔄 使用LangSmith追踪执行...")
        else:
            print("🔄 标准执行（无追踪）...")
        
        result = await agent.ainvoke(test_input)
        
        print(f"✅ Agent执行成功")
        print(f"📊 会话ID: {result.get('session_id', 'N/A')}")
        print(f"📝 输出长度: {len(result.get('output', ''))}")
        print(f"⏱️ 执行时间: {result.get('metadata', {}).get('execution_time', 0):.2f}秒")
        print(f"� 工具调用: {result.get('metadata', {}).get('tool_calls', 0)}次")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_evaluation_manager():
    """测试评估管理器"""
    print("\n" + "=" * 60)
    print("📊 测试评估管理器")
    print("=" * 60)
    
    try:
        from app.core.evaluation_manager import StudyAbroadDatasetManager
        
        eval_manager = StudyAbroadDatasetManager()
        print("✅ 评估管理器创建成功")
        
        # 测试数据集生成
        datasets = eval_manager.get_standard_datasets()
        print(f"📚 标准数据集: {len(datasets)} 个")
        
        for name, dataset in datasets.items():
            print(f"  - {name}: {len(dataset['examples'])} 个示例")
        
        return True
        
    except Exception as e:
        print(f"❌ 评估管理器测试失败: {e}")
        return False

async def test_api_integration():
    """测试API集成"""
    print("\n" + "=" * 60)
    print("🌐 测试API集成")
    print("=" * 60)
    
    try:
        # 测试导入
        from app.api.routers.advanced_planner_router import (
            AdvancedPlannerRequest,
            AdvancedPlannerResponse,
            invoke_advanced_planner
        )
        
        print("✅ API路由导入成功")
        
        # 创建测试请求
        test_request = AdvancedPlannerRequest(
            input="测试LangSmith集成是否正常工作",
            user_id="test_user",
            session_id="test_session",
            chat_history=[],
            stream=False
        )
        
        print(f"📝 测试请求: {test_request.input}")
        print(f"👤 用户ID: {test_request.user_id}")
        print(f"🔑 会话ID: {test_request.session_id}")
        
        # 注意：这里只测试导入和模型创建，不实际执行API调用
        print("✅ API模型验证成功")
        
        return True
        
    except Exception as e:
        print(f"❌ API集成测试失败: {e}")
        return False

def display_environment_info():
    """显示环境信息"""
    print("=" * 60)
    print("🌍 环境信息")
    print("=" * 60)
    
    env_vars = [
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_API_KEY", 
        "LANGCHAIN_PROJECT",
        "LANGCHAIN_ENDPOINT"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if var == "LANGCHAIN_API_KEY" and value:
            # 隐藏API密钥的大部分内容
            masked_value = f"{value[:8]}...{value[-4:] if len(value) > 12 else ''}"
            print(f"🔑 {var}: {masked_value}")
        else:
            print(f"📋 {var}: {value or '未设置'}")

async def main():
    """主测试函数"""
    print("🚀 LangSmith集成全面测试")
    print("=" * 60)
    
    # 显示环境信息
    display_environment_info()
    
    # 执行测试
    tests = [
        ("配置模块", test_langsmith_config),
        ("评估管理器", test_evaluation_manager),
        ("API集成", test_api_integration),
        ("Agent集成", test_agent_integration),  # 放在最后，因为可能耗时较长
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 总结报告
    print("\n" + "=" * 60)
    print("📋 测试总结报告")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！LangSmith集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    asyncio.run(main())
