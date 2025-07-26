#!/usr/bin/env python3
"""
AI留学规划师Agent实时交互测试脚本
直接与Agent对话，观察实时响应
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class InteractiveAgentTester:
    """交互式Agent测试器"""
    
    def __init__(self):
        self.agent = None
        self.chat_history = []
        self.session_id = "interactive_session"
        self.user_id = "interactive_user"
    
    async def initialize(self):
        """初始化Agent"""
        try:
            from app.agents.langgraph.agent_graph import get_advanced_agent
            self.agent = get_advanced_agent()
            print("✅ Agent初始化成功")
            return True
        except Exception as e:
            print(f"❌ Agent初始化失败: {e}")
            return False
    
    def display_welcome(self):
        """显示欢迎信息"""
        print("🎓 AI留学规划师 - 交互式测试")
        print("=" * 50)
        print("💡 使用提示:")
        print("  - 直接输入问题开始对话")
        print("  - 输入 'quit' 或 'exit' 退出")
        print("  - 输入 'clear' 清空对话历史")
        print("  - 输入 'help' 查看测试建议")
        print("  - 输入 'status' 查看系统状态")
        print()
        
        # 显示环境状态
        langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2") == "true"
        openai_key = "✅ 已配置" if os.getenv("OPENAI_API_KEY") else "❌ 未配置"
        tavily_key = "✅ 已配置" if os.getenv("TAVILY_API_KEY") else "❌ 未配置"
        
        print(f"🔍 LangSmith追踪: {'✅ 启用' if langsmith_enabled else '❌ 未启用'}")
        print(f"🤖 OpenAI API: {openai_key}")
        print(f"🔍 Tavily搜索: {tavily_key}")
        print()
    
    def show_test_suggestions(self):
        """显示测试建议"""
        suggestions = [
            "🎯 基础咨询测试:",
            "  • 我想申请美国的计算机科学硕士，需要什么条件？",
            "  • 英国和美国的留学费用大概是多少？",
            "",
            "🔧 工具调用测试:",
            "  • 2024年美国大学计算机专业排名前10是哪些？",
            "  • Spring Boot框架有哪些核心特性？",
            "  • 有哪些计算机科学相关的导师或服务？",
            "",
            "💬 对话连续性测试:",
            "  • 我想申请美国研究生",
            "  • 我的专业是计算机科学",
            "  • 我的GPA是3.5，托福100分",
            "  • 你觉得我应该申请哪些学校？",
            "",
            "🚨 边界情况测试:",
            "  • (空输入)",
            "  • 非留学相关问题：今天天气怎么样？",
            "  • 复杂问题：我想同时申请10个不同专业..."
        ]
        
        for suggestion in suggestions:
            print(suggestion)
        print()
    
    def show_system_status(self):
        """显示系统状态"""
        print("📊 系统状态")
        print("-" * 30)
        print(f"💾 对话历史: {len(self.chat_history)} 条消息")
        print(f"👤 用户ID: {self.user_id}")
        print(f"🔑 会话ID: {self.session_id}")
        
        # 环境变量检查
        env_status = {
            "OPENAI_API_KEY": "✅" if os.getenv("OPENAI_API_KEY") else "❌",
            "TAVILY_API_KEY": "✅" if os.getenv("TAVILY_API_KEY") else "❌", 
            "LANGCHAIN_TRACING_V2": "✅" if os.getenv("LANGCHAIN_TRACING_V2") == "true" else "❌",
            "SUPABASE_URL": "✅" if os.getenv("SUPABASE_URL") else "❌"
        }
        
        print("\n🌍 环境配置:")
        for key, status in env_status.items():
            print(f"  {key}: {status}")
        print()
    
    async def process_input(self, user_input: str):
        """处理用户输入"""
        if not user_input.strip():
            return "请输入有效的问题或命令"
        
        # 特殊命令处理
        if user_input.lower() in ['quit', 'exit']:
            return "QUIT"
        elif user_input.lower() == 'clear':
            self.chat_history = []
            return "✅ 对话历史已清空"
        elif user_input.lower() == 'help':
            self.show_test_suggestions()
            return ""
        elif user_input.lower() == 'status':
            self.show_system_status()
            return ""
        
        # Agent处理
        try:
            print(f"🤔 正在思考...")
            
            import time
            start_time = time.time()
            
            result = await self.agent.ainvoke({
                "input": user_input,
                "chat_history": self.chat_history,
                "user_id": self.user_id
            })
            
            execution_time = time.time() - start_time
            
            if isinstance(result, dict):
                output = result.get("output", str(result))
                metadata = result.get("metadata", {})
                session_id = result.get("session_id", self.session_id)
                
                # 更新对话历史
                self.chat_history.extend([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": output}
                ])
                
                # 显示元数据
                print(f"\n📊 执行信息:")
                print(f"  ⏱️ 执行时间: {execution_time:.2f}秒")
                print(f"  🔧 工具调用: {metadata.get('tool_calls', 0)}次")
                print(f"  🔍 LangSmith: {'启用' if metadata.get('langsmith_enabled') else '未启用'}")
                print(f"  🔑 会话ID: {session_id}")
                print(f"  📝 响应长度: {len(output)}字符")
                
                return output
            else:
                # 处理非字典结果
                output = str(result)
                self.chat_history.extend([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": output}
                ])
                return output
                
        except Exception as e:
            error_msg = f"❌ 处理失败: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def run(self):
        """运行交互式测试"""
        if not await self.initialize():
            return
        
        self.display_welcome()
        
        print("🚀 Agent已准备就绪，开始对话吧！")
        print("=" * 50)
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n🙋 您: ").strip()
                
                if not user_input:
                    continue
                
                # 处理输入
                response = await self.process_input(user_input)
                
                if response == "QUIT":
                    print("👋 谢谢使用，再见！")
                    break
                elif response:
                    print(f"\n🤖 AI留学规划师: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 收到中断信号，正在退出...")
                break
            except Exception as e:
                print(f"\n❌ 系统错误: {e}")
                continue

async def main():
    """主函数"""
    tester = InteractiveAgentTester()
    await tester.run()

if __name__ == "__main__":
    asyncio.run(main())
