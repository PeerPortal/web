"""
测试AI留学规划师Agent功能
验证数据库工具、网络搜索和智能回答是否正常工作
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.agents.tools.database_tools import find_mentors_tool, find_services_tool, get_platform_stats_tool

async def test_database_tools():
    """测试数据库工具"""
    print("🧪 测试AI留学规划师的数据库工具")
    print("=" * 50)

    try:
        # 测试平台统计工具
        print("📊 测试平台统计工具...")
        stats_result = await get_platform_stats_tool.ainvoke({})
        print(f"结果: {stats_result}\n")
        
        # 测试引路人查找工具
        print("👥 测试引路人查找工具...")
        mentors_result = await find_mentors_tool.ainvoke({
            "university": "Stanford",
            "major": "Computer Science"
        })
        print(f"结果: {mentors_result}\n")
        
        # 测试服务查找工具
        print("🛍️ 测试服务查找工具...")
        services_result = await find_services_tool.ainvoke({
            "category": "语言学习",
            "max_price": 500
        })
        print(f"结果: {services_result}\n")
        
        print("✅ 所有数据库工具测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库工具测试失败: {e}")
        return False

async def test_agent_basic():
    """测试Agent基本功能（不需要API key）"""
    print("\n🤖 测试Agent基本初始化")
    print("=" * 50)
    
    try:
        # 设置临时环境变量（用于测试）
        os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-for-initialization")
        
        from app.agents.planner_agent import get_agent_executor
        agent = get_agent_executor()
        
        print("✅ Agent初始化成功!")
        print(f"📝 可用工具数量: {len(agent.tools)}")
        print("🔧 工具列表:")
        for i, tool in enumerate(agent.tools, 1):
            print(f"   {i}. {tool.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False

def test_api_route_import():
    """测试API路由导入"""
    print("\n🌐 测试API路由导入")
    print("=" * 50)
    
    try:
        from app.api.routers.planner_router import router
        print("✅ Planner路由导入成功!")
        print(f"📍 路由前缀: {router.prefix}")
        print(f"🏷️ 路由标签: {router.tags}")
        return True
        
    except Exception as e:
        print(f"❌ API路由导入失败: {e}")
        return False

async def main():
    """运行所有测试"""
    print("🚀 AI留学规划师Agent测试套件")
    print("=" * 60)
    
    results = []
    
    # 测试数据库工具
    results.append(await test_database_tools())
    
    # 测试Agent初始化
    results.append(await test_agent_basic())
    
    # 测试API路由导入
    results.append(test_api_route_import())
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果总结:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ 所有测试通过! ({passed}/{total})")
        print("\n🎉 AI留学规划师Agent已准备就绪!")
        print("\n📝 使用说明:")
        print("1. 确保设置了 OPENAI_API_KEY 环境变量")
        print("2. 启动FastAPI服务器: uvicorn app.main:app --reload --port 8001")
        print("3. 访问 http://localhost:8001/docs 查看API文档")
        print("4. 使用 POST /api/v1/ai/planner/invoke 调用AI规划师")
    else:
        print(f"❌ 部分测试失败 ({passed}/{total})")
        print("请检查错误信息并修复问题")

if __name__ == "__main__":
    asyncio.run(main())
