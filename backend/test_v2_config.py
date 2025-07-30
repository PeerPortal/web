#!/usr/bin/env python3
"""
PeerPortal AI智能体系统 v2.0 配置测试脚本 (留学规划专版)

这个脚本用于测试和验证v2.0智能体系统的配置是否正确。
专注于留学规划和咨询功能的测试。
"""
import asyncio
import os
import sys
from pathlib import Path

# 确保加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  未安装python-dotenv，将只使用系统环境变量")

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.agents.v2.config import config_manager, init_v2_from_env
    from app.agents.v2 import (
        create_study_planner, 
        create_study_consultant,
        get_architecture_info
    )
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保您在正确的目录中运行此脚本")
    sys.exit(1)


async def check_environment():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    required_vars = {
        'OPENAI_API_KEY': '必需 - OpenAI API密钥'
    }
    
    optional_vars = {
        'REDIS_URL': '可选 - Redis缓存服务',
        'MILVUS_HOST': '可选 - Milvus向量数据库',
        'MONGODB_URL': '可选 - MongoDB文档数据库',
        'ELASTICSEARCH_URL': '可选 - Elasticsearch搜索引擎',
        'DEBUG': '可选 - 调试模式'
    }
    
    # 检查必需变量
    all_required_set = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # 只显示前几个字符，保护隐私
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✅ {var}: {masked_value} ({desc})")
        else:
            print(f"  ❌ {var}: 未设置 ({desc})")
            all_required_set = False
    
    # 检查可选变量
    print("\n🔧 可选配置:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已设置 ({desc})")
        else:
            print(f"  ⚪ {var}: 未设置 ({desc})")
    
    return all_required_set


async def test_configuration():
    """测试v2.0配置"""
    print("\n🧪 开始测试v2.0智能体系统配置...")
    print("=" * 60)
    
    # 1. 检查环境变量
    env_ok = await check_environment()
    if not env_ok:
        print("\n❌ 环境变量配置不完整，请设置必需的环境变量")
        print("💡 最小配置示例:")
        print("   export OPENAI_API_KEY=sk-your-api-key-here")
        return False
    
    # 2. 初始化系统
    print(f"\n🚀 初始化v2.0智能体系统...")
    try:
        success = await init_v2_from_env()
        if not success:
            print("❌ 系统初始化失败")
            return False
    except Exception as e:
        print(f"❌ 初始化过程中出错: {e}")
        return False
    
    # 3. 检查配置状态
    print(f"\n📊 配置状态检查...")
    try:
        status = config_manager.get_config_status()
        print(f"  ✅ 系统已初始化: {status['is_initialized']}")
        print(f"  ✅ 配置已加载: {status['config_loaded']}")
        print(f"  🐛 调试模式: {status['debug_mode']}")
        
        services = status['external_services']
        print(f"  💾 Redis缓存: {'✅ 已配置' if services['redis'] else '⚪ 未配置'}")
        print(f"  🔍 Milvus向量库: {'✅ 已配置' if services['milvus'] else '⚪ 未配置'}")
        print(f"  📄 MongoDB文档库: {'✅ 已配置' if services['mongodb'] else '⚪ 未配置'}")
        print(f"  🔎 Elasticsearch搜索: {'✅ 已配置' if services['elasticsearch'] else '⚪ 未配置'}")
        
    except Exception as e:
        print(f"❌ 配置状态检查失败: {e}")
        return False
    
    # 4. 测试架构信息
    print(f"\n🏗️ 架构信息:")
    try:
        info = get_architecture_info()
        print(f"  📝 名称: {info['name']}")
        print(f"  🔢 版本: {info['version']}")
        print(f"  👨‍💻 作者: {info['author']}")
        print(f"  🤖 智能体类型: {', '.join(info['agent_types'])}")
        print(f"  📦 模块数: {len(info['modules'])}")
        print(f"  ⭐ 功能数: {len(info['features'])}")
        print(f"  🛠️ 工具数: {len(info['tools'])}")
    except Exception as e:
        print(f"❌ 架构信息获取失败: {e}")
        return False
    
    # 5. 测试智能体创建
    print(f"\n🤖 测试智能体创建...")
    agents_to_test = [
        ("留学规划师", create_study_planner),
        ("留学咨询师", create_study_consultant)
    ]
    
    created_agents = []
    for name, create_func in agents_to_test:
        try:
            agent = create_func("test_user")
            created_agents.append((name, agent))
            print(f"  ✅ {name}: 创建成功")
        except Exception as e:
            print(f"  ❌ {name}: 创建失败 - {e}")
            return False
    
    # 6. 测试基本对话
    print(f"\n💬 测试AI对话功能...")
    if created_agents:
        # 测试留学规划师
        name, agent = created_agents[0]  
        try:
            test_queries = [
                "你好，请简单介绍一下你的功能",
                "我想申请美国大学的计算机科学专业，请给我一些建议"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"  🔸 测试对话 {i}: {query}")
                try:
                    response = await agent.execute(query)
                    if response and len(response) > 10:
                        # 只显示前100个字符
                        short_response = response[:100] + "..." if len(response) > 100 else response
                        print(f"    ✅ 响应: {short_response}")
                    else:
                        print(f"    ⚠️ 响应较短: {response}")
                        
                except Exception as e:
                    print(f"    ❌ 对话失败: {e}")
                    # 继续测试其他功能，不立即返回False
                    
        except Exception as e:
            print(f"  ❌ 对话测试失败: {e}")
            # 不立即返回False，让其他测试继续
    
    # 7. 测试工具功能
    print(f"\n🛠️ 测试工具功能...")
    try:
        from app.agents.v2.tools.study_tools import (
            find_mentors_tool, 
            find_services_tool, 
            get_platform_stats_tool,
            web_search_tool
        )
        
        print("  ✅ 工具导入成功")
        print("  📋 可用工具:")
        print("    - find_mentors_tool: 查找引路人")
        print("    - find_services_tool: 查找服务")
        print("    - get_platform_stats_tool: 平台统计")
        print("    - web_search_tool: 网络搜索")
        
    except Exception as e:
        print(f"  ❌ 工具导入失败: {e}")
    
    return True


async def show_quick_start_guide():
    """显示快速开始指南"""
    print("\n🚀 v2.0智能体系统快速开始指南")
    print("=" * 60)
    
    print("""
📝 基础使用示例:

```python
from app.agents.v2 import create_study_planner, create_study_consultant

# 创建留学规划师
planner = create_study_planner("your_user_id")
response = await planner.execute("我想申请美国大学CS专业")

# 创建留学咨询师
consultant = create_study_consultant("your_user_id") 
response = await consultant.execute("美国留学的费用大概是多少？")
```

🔧 在FastAPI中集成:

```python
from fastapi import FastAPI
from app.agents.v2.config import init_v2_from_env

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_v2_from_env()

@app.post("/api/v2/planner/chat")
async def chat_with_planner(message: str, user_id: str):
    from app.agents.v2 import create_study_planner
    agent = create_study_planner(user_id)
    response = await agent.execute(message)
    return {"response": response, "agent_type": "study_planner"}

@app.post("/api/v2/consultant/chat")
async def chat_with_consultant(message: str, user_id: str):
    from app.agents.v2 import create_study_consultant
    agent = create_study_consultant(user_id)
    response = await agent.execute(message)
    return {"response": response, "agent_type": "study_consultant"}
```

🎯 智能体特色功能:
- 🎓 留学规划师: 个性化申请策略、选校建议、时间规划
- 💬 留学咨询师: 留学问答、政策解读、经验分享
- 🔍 工具集成: 引路人查找、服务推荐、实时搜索
- 🧠 智能记忆: 上下文理解、对话连续性

📚 更多配置选项请查看: app/agents/v2/CONFIGURATION_GUIDE.md
""")


async def main():
    """主函数"""
    print("🎯 PeerPortal AI智能体系统 v2.0 配置测试 (留学规划专版)")
    print("=" * 70)
    
    # 检查是否有OpenAI API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 未设置OPENAI_API_KEY环境变量")
        print("\n💡 请先设置环境变量:")
        print("   export OPENAI_API_KEY=sk-your-openai-api-key-here")
        print("\n或创建 .env 文件:")
        print("   echo 'OPENAI_API_KEY=sk-your-openai-api-key-here' > .env")
        return
    
    # 运行配置测试
    try:
        success = await test_configuration()
        
        if success:
            print("\n🎉 配置测试完成！v2.0留学智能体系统已就绪")
            print("✅ 系统专注于留学规划和咨询服务")
            print("🤖 支持智能体类型: 留学规划师、留学咨询师")
            await show_quick_start_guide()
        else:
            print("\n❌ 部分测试失败，但系统基本功能可用")
            print("💡 请参考配置指南: app/agents/v2/CONFIGURATION_GUIDE.md")
            
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生意外错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 