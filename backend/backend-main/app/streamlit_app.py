"""
AI留学规划师 - Streamlit Web界面
提供文件上传、知识库管理和对话交互功能
"""
import streamlit as st
import os
import asyncio
from langchain_core.messages import AIMessage, HumanMessage
from typing import List

import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.langgraph.agent_graph import get_advanced_agent
from app.agents.langgraph.knowledge_base import knowledge_manager

# 页面配置
st.set_page_config(
    page_title="AI留学规划师 - 启航AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .knowledge-stats {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .tool-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主函数"""
    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI留学规划师 - 启航AI</h1>
        <p>您的专属留学顾问，集成知识库学习和实时搜索能力</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏 - 知识库管理
    with st.sidebar:
        st.header("📚 知识库管理")
        
        # 知识库状态
        show_knowledge_stats()
        
        # 文件上传
        file_upload_section()
        
        # 系统信息
        show_system_info()
    
    # 主内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 对话界面
        chat_interface()
    
    with col2:
        # 功能说明
        show_capabilities()

def show_knowledge_stats():
    """显示知识库统计信息"""
    with st.container():
        st.subheader("📊 知识库状态")
        
        try:
            stats = knowledge_manager.get_knowledge_base_stats()
            
            # 状态指标
            col1, col2 = st.columns(2)
            with col1:
                st.metric("文档数量", stats["files_count"])
            with col2:
                status = "✅ 已建立" if stats["vector_store_exists"] else "❌ 未建立"
                st.metric("向量库", status)
            
            # 文件列表
            if stats["files"]:
                st.write("**已上传文档:**")
                for file in stats["files"]:
                    st.write(f"• {file}")
            else:
                st.info("暂无上传文档")
                
        except Exception as e:
            st.error(f"获取知识库状态失败: {e}")

def file_upload_section():
    """文件上传区域"""
    with st.container():
        st.subheader("📁 文档上传")
        
        uploaded_files = st.file_uploader(
            "上传PDF文件到知识库",
            type=["pdf"],
            accept_multiple_files=True,
            help="支持上传多个PDF文件，如留学案例、学校介绍、申请指南等"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 构建知识库", type="primary"):
                if uploaded_files:
                    build_knowledge_base(uploaded_files)
                else:
                    st.warning("请先选择文件")
        
        with col2:
            if st.button("🗑️ 清空知识库"):
                clear_knowledge_base()

def build_knowledge_base(uploaded_files):
    """构建知识库"""
    with st.spinner("正在处理文件，请稍候..."):
        try:
            # 保存上传的文件
            saved_files = []
            for file in uploaded_files:
                file_path = knowledge_manager.save_uploaded_file(
                    file.getbuffer(), file.name
                )
                saved_files.append(file.name)
            
            st.success(f"✅ 已保存 {len(saved_files)} 个文件")
            
            # 构建向量数据库
            with st.spinner("正在构建向量数据库..."):
                vectorstore = knowledge_manager.load_and_embed_knowledge_base()
                
                if vectorstore:
                    st.success("🎉 知识库构建完成！")
                    st.balloons()
                    # 刷新页面状态
                    st.rerun()
                else:
                    st.error("知识库构建失败")
                    
        except Exception as e:
            st.error(f"处理文件时出错: {e}")

def clear_knowledge_base():
    """清空知识库"""
    if st.session_state.get("confirm_clear"):
        try:
            import shutil
            
            # 删除知识库文件
            if os.path.exists("./knowledge_base"):
                shutil.rmtree("./knowledge_base")
            
            # 删除向量库
            if os.path.exists("./vector_store"):
                shutil.rmtree("./vector_store")
            
            st.success("🗑️ 知识库已清空")
            st.session_state["confirm_clear"] = False
            st.rerun()
            
        except Exception as e:
            st.error(f"清空知识库失败: {e}")
    else:
        st.session_state["confirm_clear"] = True
        st.warning("⚠️ 确定要清空知识库吗？再次点击确认删除。")

def show_system_info():
    """显示系统信息"""
    with st.expander("⚙️ 系统信息"):
        st.write("**模型**: GPT-4o-mini")
        st.write("**框架**: LangGraph + FastAPI")
        st.write("**向量库**: ChromaDB")
        st.write("**搜索**: Tavily AI / DuckDuckGo")

def chat_interface():
    """对话界面"""
    st.subheader("💬 智能对话")
    
    # 初始化对话历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="您好！我是启航AI，您的专属留学规划师。🚀\n\n我可以帮您：\n- 📚 基于知识库提供专业留学指导\n- 🔍 搜索最新的大学和申请信息\n- 👥 匹配平台上的学长学姐引路人\n- 🎯 制定个性化的申请策略\n\n有什么问题尽管问我吧！")
        ]
    
    # 显示对话历史
    for message in st.session_state.chat_history:
        with st.chat_message("assistant" if isinstance(message, AIMessage) else "user"):
            st.write(message.content)
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # AI回复
        with st.chat_message("assistant"):
            with st.spinner("启航AI正在思考..."):
                response = get_ai_response(prompt)
                st.write(response)
                
                # 添加AI消息到历史
                st.session_state.chat_history.append(AIMessage(content=response))

def get_ai_response(user_input: str) -> str:
    """获取AI回复"""
    try:
        # 获取Agent实例
        agent = get_advanced_agent()
        
        # 准备输入数据
        input_data = {
            "input": user_input,
            "chat_history": st.session_state.chat_history,
            "session_id": st.session_state.get("session_id", "streamlit_session")
        }
        
        # 调用Agent（同步调用）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent.ainvoke(input_data))
        loop.close()
        
        return result.get("output", "抱歉，我无法处理您的问题。")
        
    except Exception as e:
        return f"抱歉，处理您的问题时出现了错误：{str(e)}"

def show_capabilities():
    """显示功能说明"""
    st.subheader("🎯 功能特色")
    
    capabilities = [
        {
            "icon": "📚",
            "title": "知识库学习",
            "desc": "上传PDF文档，AI自动学习并提供专业建议"
        },
        {
            "icon": "🔍", 
            "title": "实时搜索",
            "desc": "获取最新的大学排名、申请要求等信息"
        },
        {
            "icon": "👥",
            "title": "引路人匹配", 
            "desc": "匹配平台上合适的学长学姐引路人"
        },
        {
            "icon": "🎯",
            "title": "个性化规划",
            "desc": "根据背景制定专属的留学申请策略"
        },
        {
            "icon": "🧠",
            "title": "智能记忆",
            "desc": "记住对话内容，提供连贯的咨询体验"
        },
        {
            "icon": "⚡",
            "title": "多工具融合",
            "desc": "智能选择最合适的信息源为您服务"
        }
    ]
    
    for cap in capabilities:
        with st.container():
            st.markdown(f"""
            <div class="tool-section">
                <h4>{cap['icon']} {cap['title']}</h4>
                <p>{cap['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 示例问题
    st.subheader("💡 试试这些问题")
    
    example_questions = [
        "平台上有多少位引路人？",
        "我想申请美国计算机科学硕士，有什么建议？",
        "有什么语言学习相关的服务吗？",
        "最新的QS世界大学排名如何？",
        "知识库里有哪些文档？",
        "我上一条问题问的是什么？"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{hash(question)}"):
            # 模拟用户输入
            st.session_state.chat_input = question
            st.rerun()

if __name__ == "__main__":
    # 初始化会话ID
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    
    main()
