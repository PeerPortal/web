"""
简化版高级AI留学规划师测试脚本
直接测试Agent的核心功能，不使用复杂的LangGraph状态管理
"""

import asyncio
import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agents.langgraph.agent_tools import agent_tools
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class SimpleAdvancedAgentTester:
    """简化版高级Agent测试器"""
    
    def __init__(self):
        self.agent_executor = None
        self.setup_agent()
    
    def setup_agent(self):
        """设置简化版Agent"""
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.1
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业、友善的AI留学规划师，名叫"启航AI"。

🎯 你的核心能力：
- 根据用户需求智能选择合适的工具来获取信息
- 优先从私有知识库获取专业的留学指导信息
- 当知识库无法回答时，使用网络搜索获取最新信息
- 查询平台数据库匹配合适的引路人和服务
- 提供个性化的留学申请建议和规划

🛠️ 工具使用策略：
1. **知识库优先**: 对于留学申请策略、文书写作、成功案例等问题，优先使用知识库检索
2. **网络搜索补充**: 对于最新排名、申请要求变更、时事新闻等，使用网络搜索
3. **平台数据查询**: 对于寻找引路人、服务推荐等，使用平台数据库工具

💬 对话风格：
- 专业但亲切，像经验丰富的学长学姐
- 信息准确，基于事实和数据
- 结构清晰，条理分明
- 主动推荐平台资源和服务"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建agent
        agent = create_tool_calling_agent(llm, agent_tools, prompt)
        
        # 创建executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=agent_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            max_execution_time=30
        )
    
    async def test_question(self, question: str, chat_history=None):
        """测试单个问题"""
        print(f"\n🧑 用户: {question}")
        print("-" * 60)
        
        try:
            result = await self.agent_executor.ainvoke({
                "input": question,
                "chat_history": chat_history or []
            })
            
            output = result.get("output", "无回答")
            print(f"🤖 AI: {output}")
            return output
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 简化版高级AI留学规划师测试")
        print("=" * 60)
        
        # 测试问题列表
        test_questions = [
            "你好，请介绍一下你的功能",
            "平台上有多少引路人？",
            "知识库里有哪些文档？",
            "根据知识库，申请计算机科学硕士需要什么条件？",
            "有什么价格在500元以内的语言学习服务吗？",
            "最新的托福考试有什么变化？"
        ]
        
        chat_history = []
        success_count = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*20} 测试 {i}/{len(test_questions)} {'='*20}")
            
            result = await self.test_question(question, chat_history)
            
            if result:
                success_count += 1
                # 更新对话历史
                from langchain_core.messages import HumanMessage, AIMessage
                chat_history.append(HumanMessage(content=question))
                chat_history.append(AIMessage(content=result))
        
        # 测试总结
        print(f"\n{'='*60}")
        print(f"📊 测试完成: {success_count}/{len(test_questions)} 成功")
        
        if success_count == len(test_questions):
            print("🎉 所有测试通过！Agent工作正常！")
        else:
            print("⚠️ 部分测试失败，需要进一步调试")

async def main():
    """主函数"""
    tester = SimpleAdvancedAgentTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
