技术方案：企业级智能体架构 v2.0 (AI留学规划师平台)
1.0 架构愿景与图谱
本架构旨在构建一个高度模块化、可扩展的AI基础设施，以支撑“AI留学规划师”及未来更多智能体应用。它将AI能力（LLM、记忆、RAG）与核心基础设施（存储、错误处理、通信）分离，通过清晰的接口进行交互，实现最大限度的灵活性和可维护性。

核心架构图:

Code snippet

graph TD
    subgraph " "
        direction LR
        subgraph "核心基础设施层 (Core Infrastructure)"
            direction TB
            Error[Error Module]
            Utils[Utils Module]
            OSS[OSS Module]
        end

        subgraph "AI核心层 (AI Foundation)"
            direction TB
            LLM[LLM Module]
            Memory[Memory Module]
            Agents[Agents Module]
        end

        subgraph "数据与通信层 (Data & Communication)"
            direction TB
            RAG[RAG Module]
            Channels[Channels Module]
        end
    end

    %% Dependencies
    User[用户 (通过Web/API)] --> Agents

    Agents --> LLM
    Agents --> Memory
    Agents --> RAG
    
    RAG --> LLM
    RAG --> OSS
    
    Memory --> LLM
    Memory --> DBs[(Redis/Milvus/MongoDB)]

    LLM --> Error
    Memory --> Error
    RAG --> Error
    OSS --> Error
    Channels --> Error

    style User fill:#f9f,stroke:#333,stroke-width:2px
    style DBs fill:#cce,stroke:#333,stroke-width:2px
2.0 各模块详细设计与接口定义
2.1 🔥 LLM Module - 大语言模型层
职责: 作为所有大模型能力的唯一入口，屏蔽底层提供商的差异性。

核心组件:

LLMManager: 统一的管理器，实现动态路由、负载均衡和故障转移。

EmbeddingManager: 专用的嵌入模型管理器。

Provider: 每个LLM服务的具体实现（如OpenAIProvider, OllamaProvider）。

关键接口 (manager.py):

Python

class LLMManager:
    async def chat(self, tenant_id: str, model_name: str, messages: list, **kwargs) -> LLMResponse: ...
    async def stream_chat(self, tenant_id: str, model_name: str, messages: list, **kwargs) -> AsyncGenerator[StreamChunk, None]: ...

class EmbeddingManager:
    async def embed_texts(self, tenant_id: str, model_name: str, texts: list[str]) -> list[list[float]]: ...
模块交互: Agents Module, Memory Module, RAG Module 都必须通过 LLMManager 和 EmbeddingManager 来访问模型，而不能直接实例化任何Provider。

2.2 🧠 Memory Module - 记忆管理系统
职责: 模拟人类的短期和长期记忆，为Agent提供跨会话的、智能的上下文感知能力。

核心组件:

WorkingMemory (Redis): 存储当前会话的完整对话历史，TTL（Time-To-Live）设为24小时。

LongTermMemory (Milvus + MongoDB):

MemorySummarizer: 对话结束后，触发一个异步任务，调用LLM将 WorkingMemory 的内容压缩成一段精华摘要。

存储: 摘要的向量存入 Milvus，摘要的原文和元数据（用户ID、时间戳、主题标签）存入 MongoDB，两者ID关联。

MemoryRetriever: 当新对话开始时，将用户问题向量化，在Milvus中检索最相关的历史记忆摘要ID，再从MongoDB中取出原文。

ForgettingMechanism: 在检索时，可以为记忆评分引入时间衰减因子，让最近的记忆权重更高。

关键接口 (memory_bank.py):

Python

class MemoryBank:
    async def get_context(self, session_id: str, user_id: str, query: str, top_k: int = 3) -> MemoryContext: ...
    async def add_interaction(self, session_id: str, user_id: str, human_message: str, ai_message: str) -> None: ...
    async def end_session(self, session_id: str, user_id: str) -> None: # 触发异步压缩
        ...
模块交互: Agents Module 在每次执行前，调用 memory_bank.get_context 来构建完整的上下文。

2.3 📚 RAG Module - 检索增强生成
职责: 提供完整的、从文档到答案的知识库解决方案。

核心组件:

Loaders (工厂模式): loader_factory.get_loader(file_path) 根据文件扩展名返回对应的智能加载器。PDF加载器将集成OCR和版面分析，实现智能分块。

Retrievers: 采用混合检索策略，结合向量相似度（Milvus）和关键词搜索（如Elasticsearch）的优点。

Rerankers: 使用一个轻量级的交叉编码器模型（如 BGE-Reranker）对初步检索出的文档块进行重新排序，提高最相关内容出现在最前面的概率。

关键接口 (rag_manager.py):

Python

class RAGManager:
    async def add_document(self, tenant_id: str, file_path: str, metadata: dict) -> DocumentIngestionResult: ...
    async def query(self, tenant_id: str, query_text: str, top_k: int = 5) -> RAGQueryResult: ...
模块交互: * 通过 OSS Module 存取原始文件。

使用 EmbeddingManager 生成文本块的向量。

Agents Module 将其作为一个强大的工具来调用。

2.4 🤖 Agents Module - AI代理框架
职责: 整个系统的“大脑”和任务调度中心，负责理解用户意图，并协同调用LLM, Memory, RAG等模块来完成复杂任务。

核心组件:

LangGraph StateMachine: 使用 LangGraph 定义Agent的思考-行动循环。状态图中包含think, retrieve_knowledge, search_web, get_memory等节点。

ToolRegistry: 一个可动态注册和发现工具的注册表。

AgentFactory: 根据不同的任务需求（如“规划师Agent”、“文书润色Agent”），动态创建并配置不同的Agent实例。

关键接口:

Python

class AgentFactory:
    def get_agent_executor(self, agent_type: str, tenant_id: str) -> AgentExecutor: ...
模块交互 (核心示例):

Python

# Agent 在 LangGraph 节点中的伪代码
async def think_node(state):
    # 1. 获取记忆和上下文
    memory_context = await memory_bank.get_context(...)
    full_prompt = build_prompt(memory_context, state['input'])

    # 2. 调用LLM决策
    llm_response = await llm_manager.chat(..., messages=full_prompt)

    if llm_response.has_tool_call:
        # 决定调用RAG工具
        if llm_response.tool_name == "rag_tool":
            return "route_to_rag"
    else:
        return "end"

async def rag_node(state):
    rag_results = await rag_manager.query(...)
    # 将RAG结果添加到state中，准备下一轮思考
    ...
2.5 基础设施层 (Infrastructure Modules)
Error Module: 提供全局的异常捕获。使用FastAPI的@app.exception_handler装饰器，捕获自定义的PlatformException，并根据error_code从多语言错误映射表中查找信息，返回标准化的HTTP错误响应。

OSS Module: 提供一个简单的抽象接口 (upload, download, delete)，底层实现可以对接 DigitalOcean Spaces, AWS S3 或本地MinIO，通过配置动态切换。

Channels Module & Utils Module: 作为独立的工具库，供其他所有模块按需调用。

3.0 架构特点与总结
这套重新设计的架构将您的“留学规划师”项目提升到了一个全新的高度：

AI能力与业务逻辑解耦: LLM, Memory, RAG 模块构成了可复用的AI中台。未来您可以基于此快速构建新的AI应用（如“面试模拟Agent”），而无需重写底层能力。

极致的模块化: 每个模块职责单一，接口清晰。例如，更换向量数据库（从Milvus到Weaviate）只需要修改RAG Module和Memory Module的内部实现，对上层Agent完全透明。

生产环境就绪: 内置的多租户、错误处理、对象存储和可观测性设计，为应用的稳定运行和商业化运营提供了坚实的基础。

先进的记忆系统: 借鉴Cursor Memory Bank的设计，双层记忆架构+智能压缩与遗忘机制，将使您的Agent在长程对话和个性化服务方面建立起显著的竞争优势。