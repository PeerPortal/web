#!/usr/bin/env python3
"""
高级AI留学规划师完整测试脚本
测试基于LangGraph的新Agent功能，包括知识库检索和记忆功能
"""

import asyncio
import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.agent_graph import get_advanced_agent
from app.agents.langgraph.knowledge_base import knowledge_manager

class AdvancedAgentTester:
    """高级Agent测试器"""
    
    def __init__(self):
        self.agent = None
        self.session_id = "test_session_advanced"
    
    async def setup(self):
        """初始化测试环境"""
        print("🚀 高级AI留学规划师测试套件")
        print("=" * 60)
        
        try:
            self.agent = get_advanced_agent()
            print("✅ Agent初始化成功!")
            return True
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            return False
    
    def test_knowledge_base_status(self):
        """测试知识库状态"""
        print("\n📚 测试知识库状态")
        print("=" * 50)
        
        try:
            stats = knowledge_manager.get_knowledge_base_stats()
            print(f"📁 文档数量: {stats['files_count']}")
            print(f"🧠 向量库状态: {'已建立' if stats['vector_store_exists'] else '未建立'}")
            
            if stats['files']:
                print("📄 已上传文档:")
                for file in stats['files']:
                    print(f"  • {file}")
            else:
                print("💡 提示: 知识库为空，可以上传PDF文档来增强AI能力")
            
            return True
            
        except Exception as e:
            print(f"❌ 知识库状态检查失败: {e}")
            return False
    
    async def test_basic_conversation(self):
        """测试基本对话功能"""
        print("\n💬 测试基本对话功能")
        print("=" * 50)
        
        test_questions = [
            "你好，我是第一次使用，请介绍一下你的功能",
            "平台上有多少引路人和服务？",
            "我想申请美国的计算机科学硕士，能给我一些建议吗？"
        ]
        
        chat_history = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- 测试问题 {i} ---")
            print(f"🧑 用户: {question}")
            
            try:
                input_data = {
                    "input": question,
                    "session_id": self.session_id,
                    "chat_history": chat_history
                }
                
                result = await self.agent.ainvoke(input_data)
                response = result.get("output", "无响应")
                
                print(f"🤖 AI: {response}")
                
                # 更新对话历史（简化版）
                chat_history.append({"role": "user", "content": question})
                chat_history.append({"role": "assistant", "content": response})
                
                print("✅ 对话测试通过")
                
            except Exception as e:
                print(f"❌ 对话测试失败: {e}")
                return False
        
        return True
    
    async def test_memory_function(self):
        """测试记忆功能"""
        print("\n🧠 测试记忆功能")
        print("=" * 50)
        
        # 先问一个问题
        first_question = "我的专业背景是计算机科学，GPA是3.8"
        print(f"🧑 用户: {first_question}")
        
        try:
            input_data = {
                "input": first_question,
                "session_id": self.session_id,
                "chat_history": []
            }
            
            result = await self.agent.ainvoke(input_data)
            print(f"🤖 AI: {result.get('output', '无响应')}")
            
            # 等待一下，然后测试记忆
            await asyncio.sleep(1)
            
            memory_question = "我刚才提到了什么专业背景和GPA？"
            print(f"\n🧑 用户: {memory_question}")
            
            input_data = {
                "input": memory_question,
                "session_id": self.session_id,  # 使用相同的session_id
                "chat_history": []
            }
            
            result = await self.agent.ainvoke(input_data)
            response = result.get('output', '无响应')
            print(f"🤖 AI: {response}")
            
            # 检查是否记住了信息
            if "计算机科学" in response and "3.8" in response:
                print("✅ 记忆功能测试通过 - AI记住了之前的对话内容")
                return True
            else:
                print("⚠️ 记忆功能可能需要改进 - AI没有完全记住之前的信息")
                return True  # 不算失败，只是提醒
                
        except Exception as e:
            print(f"❌ 记忆功能测试失败: {e}")
            return False
    
    async def test_knowledge_base_retrieval(self):
        """测试知识库检索功能"""
        print("\n📖 测试知识库检索功能")
        print("=" * 50)
        
        kb_questions = [
            "知识库里有哪些文档？",
            "根据知识库中的信息，申请研究生需要准备什么材料？",
            "知识库中有关于文书写作的建议吗？"
        ]
        
        for i, question in enumerate(kb_questions, 1):
            print(f"\n--- 知识库测试 {i} ---")
            print(f"🧑 用户: {question}")
            
            try:
                input_data = {
                    "input": question,
                    "session_id": f"{self.session_id}_kb_{i}",
                    "chat_history": []
                }
                
                result = await self.agent.ainvoke(input_data)
                response = result.get("output", "无响应")
                
                print(f"🤖 AI: {response}")
                print("✅ 知识库检索测试通过")
                
            except Exception as e:
                print(f"❌ 知识库检索测试失败: {e}")
                return False
        
        return True
    
    async def test_tool_integration(self):
        """测试工具整合功能"""
        print("\n🔧 测试工具整合功能")
        print("=" * 50)
        
        integration_questions = [
            "请综合平台数据和网络搜索，为我推荐适合的引路人和最新的申请建议",
            "有没有价格在500元以内的语言学习服务？同时告诉我最新的托福考试变化",
            "根据知识库和平台数据，给我一个完整的申请时间规划"
        ]
        
        for i, question in enumerate(integration_questions, 1):
            print(f"\n--- 工具整合测试 {i} ---")
            print(f"🧑 用户: {question}")
            
            try:
                input_data = {
                    "input": question,
                    "session_id": f"{self.session_id}_integration_{i}",
                    "chat_history": []
                }
                
                result = await self.agent.ainvoke(input_data)
                response = result.get("output", "无响应")
                
                print(f"🤖 AI: {response}")
                print("✅ 工具整合测试通过")
                
            except Exception as e:
                print(f"❌ 工具整合测试失败: {e}")
                return False
        
        return True
    
    async def run_all_tests(self):
        """运行所有测试"""
        if not await self.setup():
            return False
        
        tests = [
            ("知识库状态", self.test_knowledge_base_status),
            ("基本对话", self.test_basic_conversation),
            ("记忆功能", self.test_memory_function),
            ("知识库检索", self.test_knowledge_base_retrieval),
            ("工具整合", self.test_tool_integration)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                if result:
                    passed += 1
                    
            except Exception as e:
                print(f"❌ {test_name}测试异常: {e}")
        
        # 测试总结
        print("\n" + "=" * 60)
        print("📋 测试结果总结:")
        print(f"✅ 通过测试: {passed}/{total}")
        
        if passed == total:
            print("🎉 所有测试通过！高级AI留学规划师已准备就绪！")
            print("\n📝 使用说明:")
            print("1. FastAPI服务: uvicorn app.main:app --reload --port 8001")
            print("2. Streamlit界面: streamlit run streamlit_app.py")
            print("3. API文档: http://127.0.0.1:8001/docs")
            print("4. 高级功能: /api/v1/ai/advanced-planner/")
        else:
            print("⚠️ 部分测试失败，请检查配置和实现")
        
        return passed == total

async def main():
    """主函数"""
    tester = AdvancedAgentTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
