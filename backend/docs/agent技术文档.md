

### **技术文档：高级AI留学规划师 (Powered by LangGraph & RAG)**

#### **项目概述**

我们将构建一个高级智能体，它不仅能上网搜索，还能**学习你上传的私有知识**（如PDF/DOC格式的留学案例、院校内部资料），并拥有**可跨会话的长期记忆**。我们将使用 `LangGraph` 来构建其核心的思考-行动循环，并用 `Streamlit` 搭建一个可交互的Web界面。

**核心技术栈:**

| 组件 | 技术 | 作用 |
| :--- | :--- | :--- |
| **智能体核心** | **LangGraph** | 构建健壮、可控的智能体工作流（ReAct循环）。 |
| **大语言模型** | OpenAI GPT-4 | 负责推理、决策和生成。 |
| **Web搜索工具** | Tavily AI | 提供专为AI优化的实时网络搜索能力。 |
| **文件处理** | `unstructured`, `pypdf` | 解析用户上传的PDF、DOC等文件内容。 |
| **知识库/长期记忆** | **ChromaDB** + OpenAI Embeddings | 将文件内容向量化后存入ChromaDB，实现长期记忆和RAG检索。 |
| **短期记忆** | LangChain Memory | 在单次会话中维持上下文。 |
| **Web界面** | **Streamlit** | 快速搭建一个支持文件上传和实时对话的交互式Web UI。 |
| **后端服务** | **FastAPI** | （可选集成）将Agent逻辑封装成API，供更复杂的系统调用。本教程将Streamlit作为主服务。 |

-----

### **第一步：项目设置与环境准备**

1.  **创建项目结构:**

    ```
    /advanced_study_agent
    |-- /knowledge_base           # 存放上传的PDF/DOC文件
    |-- /vector_store             # 存放ChromaDB的持久化数据
    |-- app/
    |   |-- agent_state.py        # 定义LangGraph的状态
    |   |-- agent_tools.py        # 定义所有工具 (搜索, RAG)
    |   |-- agent_graph.py        # 构建LangGraph的核心逻辑
    |-- config.py                 # 存放配置和API密钥
    |-- app.py                    # Streamlit应用主文件
    |-- requirements.txt          # 项目依赖
    ```

2.  **安装依赖:**
    创建 `requirements.txt` 文件并写入以下内容：

    ```txt
    langchain
    langchain-openai
    langgraph
    langchain_community
    streamlit
    fastapi
    uvicorn
    tavily-python
    chromadb
    unstructured[docx,pdf]
    pypdf
    python-dotenv
    ```

    然后通过pip安装：

    ```bash
    pip install -r requirements.txt
    ```

3.  **设置API密钥:**
    创建 `.env` 文件，并填入你的密钥：

    ```env
    OPENAI_API_KEY="sk-..."
    TAVILY_API_KEY="tvly-..."
    ```

    在 `config.py` 中加载这些密钥：

    ```python
    # config.py
    import os
    from dotenv import load_dotenv

    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    ```

-----

### **第二步：构建知识库与记忆系统 (RAG + ChromaDB)**

这是实现Agent“学习”能力和长期记忆的关键。

1.  **文件处理与向量化:**
    我们将创建一个函数，它能读取文件夹中的文档，将其分割成小块（Chunks），然后使用OpenAI的Embedding模型进行向量化，最后存入ChromaDB。

    ```python
    # 在 app/agent_tools.py 或一个新文件 knowledge_base.py 中
    import os
    from langchain_community.document_loaders import DirectoryLoader
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    VECTOR_STORE_PATH = "./vector_store"
    KNOWLEDGE_BASE_PATH = "./knowledge_base"

    def load_and_embed_knowledge_base():
        """加载、分割、嵌入并存储知识库文档。"""
        # 1. 加载文档
        loader = DirectoryLoader(KNOWLEDGE_BASE_PATH, glob="**/*.(pdf|docx|doc)", show_progress=True)
        documents = loader.load()

        if not documents:
            print("知识库为空，跳过嵌入过程。")
            return None

        # 2. 分割文档
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        # 3. 创建并持久化向量数据库
        print(f"正在创建并持久化向量数据库，共 {len(splits)} 个文档块...")
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=OpenAIEmbeddings(),
            persist_directory=VECTOR_STORE_PATH
        )
        print("向量数据库创建完成。")
        return vectorstore

    def get_retriever():
        """获取现有的向量数据库检索器。"""
        if not os.path.exists(VECTOR_STORE_PATH):
            return load_and_embed_knowledge_base().as_retriever()
        
        vectorstore = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=OpenAIEmbeddings()
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3}) # 返回最相关的3个结果

    ```

2.  **定义知识库检索工具 (`app/agent_tools.py`)**
    现在，我们把检索器封装成一个Agent可以调用的工具。

    ```python
    # app/agent_tools.py
    from langchain.tools import tool
    from typing import List

    # (接上文的 get_retriever 函数)

    @tool
    def knowledge_base_retriever(query: str) -> List[str]:
        """
        当需要回答关于留学申请策略、特定学校的内部信息、文书写作技巧或过往成功案例时，使用此工具。
        此工具能从平台的私有知识库中检索最相关的信息。
        """
        retriever = get_retriever()
        if retriever is None:
            return ["知识库为空，无法查询。"]
        
        docs = retriever.invoke(query)
        return [doc.page_content for doc in docs]
    ```

-----

### **第三步：定义Agent的工具集与核心逻辑 (LangGraph)**

1.  **添加其他工具 (`app/agent_tools.py`)**

    ```python
    # app/agent_tools.py (继续添加)
    from langchain_community.tools.tavily_search import TavilySearchResults

    # 1. 网络搜索工具
    web_search_tool = TavilySearchResults(max_results=3, name="web_search")

    # 2. 将所有工具放入一个列表
    agent_tools = [web_search_tool, knowledge_base_retriever]
    ```

2.  **定义Agent状态 (`app/agent_state.py`)**
    `LangGraph` 的核心是状态机。我们需要定义一个贯穿整个流程的状态对象。

    ```python
    # app/agent_state.py
    from typing import List, TypedDict
    from langchain_core.messages import BaseMessage

    class AgentState(TypedDict):
        # input是用户的原始输入
        input: str
        # chat_history是短期记忆
        chat_history: List[BaseMessage]
        # agent_outcome是Agent执行的结果
        agent_outcome: dict
        # intermediate_steps是工具调用的中间过程
        intermediate_steps: list
    ```

3.  **构建Agent图 (`app/agent_graph.py`)**
    这是最核心的部分。我们将定义图的节点（Nodes）和边（Edges）。

    ```python
    # app/agent_graph.py
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode

    from app.agent_state import AgentState
    from app.agent_tools import agent_tools
    import config

    # 1. 初始化LLM
    llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=config.OPENAI_API_KEY, temperature=0)

    # 2. 创建Agent的核心逻辑 (LLM + Prompt + Tools)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业、友善的AI留学规划师，名叫“启航AI”。
        你的任务是根据用户的提问，决策是使用网络搜索来获取最新信息，还是查询私有知识库来获取专业经验和案例。
        请优先使用知识库，因为那里有更专业的、经过验证的信息。只有在知识库无法回答，或者需要查询非常有时效性（比如今天的新闻、股价）的信息时，才使用网络搜索。
        请结合短期对话历史进行回答，以确保对话的连贯性。"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # 这个agent负责决策
    decider_agent = create_tool_calling_agent(llm, agent_tools, prompt)

    # 3. 定义图的节点
    # Agent节点：负责调用LLM进行决策
    def run_agent_node(state: AgentState):
        agent_outcome = decider_agent.invoke({
            "input": state["input"],
            "chat_history": state["chat_history"],
            "intermediate_steps": state["intermediate_steps"]
        })
        return {"agent_outcome": agent_outcome, "intermediate_steps": []}

    # Tool节点：负责执行工具
    tool_node = ToolNode(agent_tools)

    # 4. 定义图的边（路由逻辑）
    def should_continue(state: AgentState):
        if state["agent_outcome"].tool_calls:
            return "continue" # 如果有工具调用，则继续
        else:
            return "end" # 如果没有工具调用（代表已生成最终答案），则结束

    # 5. 构建图
    graph = StateGraph(AgentState)

    graph.add_node("agent", run_agent_node)
    graph.add_node("action", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )

    graph.add_edge("action", "agent")

    # 编译成可执行的应用
    agent_graph = graph.compile()
    ```

-----

### **第四步：构建交互式Web界面 (`app.py`)**

我们将使用 `Streamlit` 来创建一个用户友好的界面。

```python
# app.py
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
import os

from app.agent_graph import agent_graph
from app.agent_tools import load_and_embed_knowledge_base

st.set_page_config(page_title="AI留学规划师-启航AI", layout="wide")

st.title("AI留学规划师 - 启航AI 🚀")

# ---- 文件上传与知识库构建 ----
with st.sidebar:
    st.header("知识库管理")
    uploaded_files = st.file_uploader(
        "请上传PDF或DOCX文件",
        type=["pdf", "docx", "doc"],
        accept_multiple_files=True
    )
    if st.button("构建/更新知识库"):
        if uploaded_files:
            with st.spinner("正在处理文件，请稍候..."):
                # 将上传的文件保存到本地
                save_path = "./knowledge_base"
                os.makedirs(save_path, exist_ok=True)
                for file in uploaded_files:
                    with open(os.path.join(save_path, file.name), "wb") as f:
                        f.write(file.getbuffer())
                
                # 构建向量数据库
                load_and_embed_knowledge_base()
                st.success("知识库构建完成！")
        else:
            st.warning("请先上传文件。")

# ---- 对话状态管理 ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="您好！我是启航AI，您的专属留学规划师。无论您有什么关于选校、文书或申请策略的问题，都可以问我。您可以先在左侧上传您的背景资料或案例库。")
    ]

# ---- 对话界面 ----
for message in st.session_state.chat_history:
    with st.chat_message(message.type):
        st.write(message.content)

# ---- 用户输入 ----
user_prompt = st.chat_input("请输入您的问题...")
if user_prompt:
    st.session_state.chat_history.append(HumanMessage(content=user_prompt))
    with st.chat_message("human"):
        st.write(user_prompt)

    with st.chat_message("ai"):
        with st.spinner("启航AI正在思考..."):
            # 使用流式输出来实时显示Agent的思考过程
            response_container = st.empty()
            full_response = ""
            
            # 调用 LangGraph
            events = agent_graph.stream({
                "input": user_prompt,
                "chat_history": st.session_state.chat_history,
                "intermediate_steps": []
            })
            
            for event in events:
                # 打印所有事件，方便调试
                # print(event) 
                
                if "agent" in event:
                    outcome = event["agent"].get("agent_outcome")
                    if outcome:
                        # 如果是最终答案
                        if not outcome.tool_calls:
                            full_response = outcome.return_values['output']
                            response_container.markdown(full_response)
                        else: # 如果是工具调用
                            for tool_call in outcome.tool_calls:
                                tool_name = tool_call['name']
                                tool_args = tool_call['args']
                                full_response += f"正在调用工具: `{tool_name}`\n参数: `{tool_args}`\n\n"
                                response_container.markdown(full_response)
            
    st.session_state.chat_history.append(AIMessage(content=full_response))

```

-----

### **第五步：运行你的高级Agent**

1.  在项目根目录下创建一个 `.env` 文件并填入你的API密钥。
2.  创建一个 `knowledge_base` 文件夹。
3.  在终端中运行Streamlit应用：
    ```bash
    streamlit run app.py
    ```
4.  浏览器会自动打开一个Web界面。
      * **第一步：** 在左侧边栏上传你的PDF/DOC文件（如：名校申请成功案例、各项目介绍、文书写作指南等）。
      * **第二步：** 点击“构建/更新知识库”按钮，等待处理完成。
      * **第三步：** 在主对话框中开始与“启航AI”对话。

**测试问题示例：**

  * “根据知识库里的成功案例，申请CMU的CS项目，简历上应该突出哪些方面？” (会调用知识库)
  * “最近的US News计算机科学专业排名是怎样的？” (会调用网络搜索)
  * “我上一条问题问的是什么？” (测试短期记忆)