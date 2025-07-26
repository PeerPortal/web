#!/usr/bin/env python3
"""
简化的Tavily搜索工具测试
直接测试工具功能，不依赖复杂的环境加载
"""
import os
import sys
import time
from pathlib import Path

# 设置环境变量
os.environ['TAVILY_API_KEY'] = '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'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tavily_direct():
    """直接测试Tavily工具"""
    print("🔍 直接测试Tavily搜索工具")
    print("=" * 40)
    
    try:
        # 方法1: 直接使用Tavily
        from langchain_community.tools.tavily_search import TavilySearchResults
        
        tavily_tool = TavilySearchResults(
            max_results=3,
            name="web_search",
            description="网络搜索工具",
            api_key="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"
        )
        
        print("✅ Tavily工具初始化成功")
        
        # 测试搜索
        test_query = "MIT computer science admission requirements 2024"
        print(f"🔍 测试查询: {test_query}")
        
        start_time = time.time()
        result = tavily_tool.run(test_query)
        execution_time = time.time() - start_time
        
        print(f"✅ 搜索完成，耗时: {execution_time:.2f}秒")
        print(f"📄 结果长度: {len(result)}字符")
        
        # 显示结果预览
        preview = result[:300] + "..." if len(result) > 300 else result
        print(f"📋 结果预览:")
        print(preview)
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_agent_tools():
    """测试Agent工具集中的搜索工具"""
    print("\n🤖 测试Agent工具集中的搜索工具")
    print("=" * 40)
    
    try:
        # 直接设置环境变量
        os.environ['OPENAI_API_KEY'] = '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'
        
        from app.agents.langgraph.agent_tools import get_search_tool
        
        search_tool = get_search_tool()
        print(f"✅ 获取搜索工具成功")
        print(f"   工具名称: {search_tool.name}")
        print(f"   工具类型: {type(search_tool)}")
        
        # 测试搜索
        test_query = "Stanford University computer science masters program"
        print(f"🔍 测试查询: {test_query}")
        
        start_time = time.time()
        result = search_tool.run(test_query)
        execution_time = time.time() - start_time
        
        print(f"✅ 搜索完成，耗时: {execution_time:.2f}秒")
        print(f"📄 结果长度: {len(result) if result else 0}字符")
        
        if result:
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"📋 结果预览:")
            print(preview)
        else:
            print("❌ 无搜索结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_queries():
    """测试多个查询"""
    print("\n📋 多查询测试")
    print("=" * 40)
    
    queries = [
        "Harvard University admission requirements",
        "best computer science programs USA",
        "Stanford vs MIT computer science"
    ]
    
    try:
        from app.agents.langgraph.agent_tools import get_search_tool
        search_tool = get_search_tool()
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 查询 {i}: {query}")
            
            try:
                start_time = time.time()
                result = search_tool.run(query)
                execution_time = time.time() - start_time
                
                if result and len(result) > 20:
                    print(f"✅ 成功 ({execution_time:.2f}秒, {len(result)}字符)")
                    # 简短预览
                    preview = result[:100] + "..." if len(result) > 100 else result
                    print(f"   预览: {preview}")
                else:
                    print(f"❌ 失败或结果过短")
                    
            except Exception as e:
                print(f"❌ 查询失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 多查询测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Tavily搜索工具简化测试")
    print("=" * 50)
    
    # 测试序列
    tests = [
        ("直接Tavily测试", test_tavily_direct),
        ("Agent工具测试", test_agent_tools),
        ("多查询测试", test_multiple_queries)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name}异常: {e}")
            results[test_name] = False
    
    # 汇总结果
    print(f"\n{'='*50}")
    print("📊 测试结果汇总")
    print("=" * 30)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {test_name}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n🎯 总体结果: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 66:
        print("🎉 Tavily搜索工具基本可用！")
    else:
        print("⚠️ Tavily搜索工具存在问题，请检查配置")

if __name__ == "__main__":
    main()
