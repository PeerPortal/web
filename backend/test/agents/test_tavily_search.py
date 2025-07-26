#!/usr/bin/env python3
"""
Tavily网络搜索工具测试脚本
测试Tavily搜索工具的功能和性能
"""
import os
import sys
import asyncio
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TavilyTester:
    """Tavily搜索工具测试器"""
    
    def __init__(self):
        self.search_tool = None
        
    def check_environment(self):
        """检查环境配置"""
        print("🌍 Tavily环境检查")
        print("=" * 40)
        
        # 检查API Key
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            print("❌ TAVILY_API_KEY 未设置")
            return False
        elif tavily_key == "your-tavily-api-key-optional":
            print("❌ TAVILY_API_KEY 使用默认值，请设置真实的API密钥")
            return False
        else:
            masked_key = f"tvly-{tavily_key.split('-')[1][:4]}...{tavily_key[-4:]}"
            print(f"✅ TAVILY_API_KEY: {masked_key}")
            
        return True
    
    def initialize_tool(self):
        """初始化Tavily搜索工具"""
        try:
            from app.agents.langgraph.agent_tools import get_search_tool
            self.search_tool = get_search_tool()
            
            print(f"✅ 搜索工具初始化成功")
            print(f"   工具名称: {self.search_tool.name}")
            print(f"   工具描述: {self.search_tool.description}")
            
            # 检查是否是Tavily工具
            if hasattr(self.search_tool, 'tavily_api_key'):
                print(f"✅ 使用Tavily搜索工具")
                return True
            else:
                print(f"⚠️ 使用备选搜索工具 (DuckDuckGo)")
                return True
                
        except Exception as e:
            print(f"❌ 搜索工具初始化失败: {e}")
            return False
    
    async def test_basic_search(self):
        """测试基础搜索功能"""
        print("\n🔍 基础搜索测试")
        print("=" * 40)
        
        test_queries = [
            {
                "query": "MIT computer science admission requirements 2024",
                "description": "MIT计算机科学申请要求",
                "expected_keywords": ["MIT", "computer science", "admission", "GPA", "GRE"]
            },
            {
                "query": "Stanford University CS masters program",
                "description": "斯坦福大学CS硕士项目",
                "expected_keywords": ["Stanford", "computer science", "masters", "program"]
            },
            {
                "query": "US university computer science ranking 2024",
                "description": "2024年美国大学计算机科学排名",
                "expected_keywords": ["ranking", "computer science", "university", "2024"]
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n📝 测试 {i}: {test_case['description']}")
            print(f"查询: {test_case['query']}")
            
            try:
                start_time = time.time()
                
                # 调用搜索工具
                search_result = self.search_tool.run(test_case['query'])
                
                execution_time = time.time() - start_time
                
                # 分析结果
                result_length = len(search_result) if search_result else 0
                keywords_found = []
                
                if search_result:
                    search_lower = search_result.lower()
                    keywords_found = [
                        kw for kw in test_case['expected_keywords'] 
                        if kw.lower() in search_lower
                    ]
                
                test_result = {
                    "query": test_case["query"],
                    "success": result_length > 50,  # 至少50字符的结果
                    "execution_time": execution_time,
                    "result_length": result_length,
                    "keywords_found": len(keywords_found),
                    "keywords_expected": len(test_case["expected_keywords"]),
                    "keywords_matched": keywords_found
                }
                
                results.append(test_result)
                
                # 显示结果
                status = "✅" if test_result["success"] else "❌"
                print(f"{status} 执行时间: {execution_time:.2f}秒")
                print(f"📄 结果长度: {result_length}字符")
                print(f"🎯 关键词匹配: {len(keywords_found)}/{len(test_case['expected_keywords'])}")
                if keywords_found:
                    print(f"   匹配关键词: {', '.join(keywords_found)}")
                
                # 显示结果预览
                if search_result:
                    preview = search_result[:200] + "..." if len(search_result) > 200 else search_result
                    print(f"📋 结果预览: {preview}")
                else:
                    print("📋 无搜索结果")
                    
            except Exception as e:
                print(f"❌ 搜索失败: {e}")
                results.append({
                    "query": test_case["query"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def test_performance(self):
        """测试性能表现"""
        print("\n⚡ 性能测试")
        print("=" * 40)
        
        performance_queries = [
            "Harvard University admission requirements",
            "Stanford computer science program",
            "Yale University application deadline",
            "Princeton engineering school",
            "Columbia University tuition fees"
        ]
        
        execution_times = []
        
        for i, query in enumerate(performance_queries, 1):
            print(f"🏃 性能测试 {i}: {query}")
            
            try:
                start_time = time.time()
                result = self.search_tool.run(query)
                execution_time = time.time() - start_time
                
                execution_times.append(execution_time)
                
                status = "✅" if result and len(result) > 20 else "❌"
                print(f"   {status} {execution_time:.2f}秒 ({len(result) if result else 0}字符)")
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            print(f"\n📊 性能统计:")
            print(f"   平均时间: {avg_time:.2f}秒")
            print(f"   最快时间: {min_time:.2f}秒")
            print(f"   最慢时间: {max_time:.2f}秒")
            print(f"   总测试数: {len(execution_times)}")
            
            return {
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "total_tests": len(execution_times)
            }
        
        return {}
    
    async def test_search_quality(self):
        """测试搜索质量"""
        print("\n🎯 搜索质量测试")
        print("=" * 40)
        
        quality_tests = [
            {
                "query": "MIT computer science PhD admission requirements GPA GRE TOEFL",
                "description": "复杂查询测试",
                "quality_indicators": [
                    "具体的GPA要求",
                    "GRE分数要求", 
                    "语言成绩要求",
                    "申请截止日期",
                    "推荐信要求"
                ]
            },
            {
                "query": "best computer science universities USA 2024 ranking",
                "description": "排名查询测试",
                "quality_indicators": [
                    "排名列表",
                    "2024年数据",
                    "多所大学",
                    "排名标准",
                    "具体位置"
                ]
            }
        ]
        
        quality_results = []
        
        for test in quality_tests:
            print(f"\n🧪 {test['description']}")
            print(f"查询: {test['query']}")
            
            try:
                start_time = time.time()
                result = self.search_tool.run(test['query'])
                execution_time = time.time() - start_time
                
                if result:
                    # 分析搜索质量
                    result_lower = result.lower()
                    quality_score = 0
                    found_indicators = []
                    
                    for indicator in test['quality_indicators']:
                        indicator_words = indicator.lower().split()
                        if any(word in result_lower for word in indicator_words):
                            quality_score += 1
                            found_indicators.append(indicator)
                    
                    quality_percentage = (quality_score / len(test['quality_indicators'])) * 100
                    
                    print(f"✅ 执行时间: {execution_time:.2f}秒")
                    print(f"📊 质量得分: {quality_score}/{len(test['quality_indicators'])} ({quality_percentage:.1f}%)")
                    print(f"🎯 发现指标: {', '.join(found_indicators)}")
                    
                    # 显示详细结果
                    preview = result[:300] + "..." if len(result) > 300 else result
                    print(f"📋 结果预览: {preview}")
                    
                    quality_results.append({
                        "test": test['description'],
                        "quality_score": quality_score,
                        "max_score": len(test['quality_indicators']),
                        "quality_percentage": quality_percentage,
                        "execution_time": execution_time
                    })
                else:
                    print(f"❌ 无搜索结果")
                    quality_results.append({
                        "test": test['description'],
                        "quality_score": 0,
                        "max_score": len(test['quality_indicators']),
                        "quality_percentage": 0,
                        "execution_time": execution_time
                    })
                    
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        
        return quality_results
    
    def generate_report(self, basic_results, performance_results, quality_results):
        """生成测试报告"""
        print("\n📊 Tavily搜索工具测试报告")
        print("=" * 50)
        
        # 基础功能统计
        if basic_results:
            successful_searches = sum(1 for r in basic_results if r.get('success', False))
            total_searches = len(basic_results)
            success_rate = (successful_searches / total_searches * 100) if total_searches > 0 else 0
            
            avg_time = sum(r.get('execution_time', 0) for r in basic_results) / len(basic_results)
            avg_length = sum(r.get('result_length', 0) for r in basic_results) / len(basic_results)
            
            print(f"🔍 基础搜索功能:")
            print(f"   成功率: {successful_searches}/{total_searches} ({success_rate:.1f}%)")
            print(f"   平均响应时间: {avg_time:.2f}秒")
            print(f"   平均结果长度: {avg_length:.0f}字符")
        
        # 性能统计
        if performance_results:
            print(f"\n⚡ 性能表现:")
            print(f"   平均响应时间: {performance_results.get('average_time', 0):.2f}秒")
            print(f"   最快响应: {performance_results.get('min_time', 0):.2f}秒")
            print(f"   最慢响应: {performance_results.get('max_time', 0):.2f}秒")
        
        # 质量评估
        if quality_results:
            avg_quality = sum(r.get('quality_percentage', 0) for r in quality_results) / len(quality_results)
            print(f"\n🎯 搜索质量:")
            print(f"   平均质量得分: {avg_quality:.1f}%")
            
            for result in quality_results:
                print(f"   {result['test']}: {result['quality_percentage']:.1f}%")
        
        # 总体评估
        print(f"\n🏆 总体评估:")
        
        if basic_results and len([r for r in basic_results if r.get('success', False)]) >= len(basic_results) * 0.8:
            print("✅ 基础功能: 优秀")
        else:
            print("⚠️ 基础功能: 需要改进")
        
        if performance_results and performance_results.get('average_time', 10) < 5:
            print("✅ 响应速度: 优秀")
        else:
            print("⚠️ 响应速度: 一般")
        
        if quality_results and sum(r.get('quality_percentage', 0) for r in quality_results) / len(quality_results) > 60:
            print("✅ 搜索质量: 优秀")
        else:
            print("⚠️ 搜索质量: 需要改进")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🔍 Tavily网络搜索工具综合测试")
        print("=" * 50)
        
        # 环境检查
        if not self.check_environment():
            print("\n❌ 环境检查失败，无法继续测试")
            print("💡 请确保在 .env 文件中设置有效的 TAVILY_API_KEY")
            return False
        
        # 初始化工具
        if not self.initialize_tool():
            return False
        
        # 运行测试
        print("\n🚀 开始运行测试...")
        
        basic_results = await self.test_basic_search()
        performance_results = await self.test_performance()
        quality_results = await self.test_search_quality()
        
        # 生成报告
        self.generate_report(basic_results, performance_results, quality_results)
        
        return True

async def main():
    """主函数"""
    tester = TavilyTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
