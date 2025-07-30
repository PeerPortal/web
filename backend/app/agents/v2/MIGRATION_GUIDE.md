# PeerPortal AI智能体架构 v2.0 迁移指南

## 📋 迁移概览

本指南将帮助您从现有的agents架构迁移到全新的企业级智能体架构v2.0。新架构提供了更好的模块化、可扩展性和生产就绪特性。

### 🎯 迁移目标

- ✅ **模块化架构**: 将AI能力与基础设施分离
- ✅ **统一接口**: 通过管理器统一访问LLM、Memory、RAG
- ✅ **企业特性**: 多租户、错误处理、监控
- ✅ **可扩展性**: 支持多种模型提供商和工具

## 📁 架构对比

### 原架构结构
```
app/agents/
├── langgraph/
│   ├── agent_graph.py
│   ├── agent_state.py
│   ├── agent_tools.py
│   └── knowledge_base.py
├── tools/
│   └── database_tools.py
└── planner_agent.py
```

### 新架构结构 (v2.0)
```
app/agents/v2/
├── core_infrastructure/
│   ├── error/exceptions.py
│   ├── utils/helpers.py
│   └── oss/storage_manager.py
├── ai_foundation/
│   ├── llm/manager.py
│   ├── memory/memory_bank.py
│   └── agents/agent_factory.py
└── data_communication/
    ├── rag/rag_manager.py
    └── channels/communication.py
```

## 🔄 核心组件迁移

### 1. LLM调用迁移

#### 原方式 (v1.0)
```python
# 直接调用OpenAI
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages
)
```

#### 新方式 (v2.0)
```python
# 通过LLM管理器统一调用
from app.agents.v2 import LLMManager

response = await llm_manager.chat(
    tenant_id="user_123",
    model_name="gpt-4o-mini", 
    messages=messages
)
```

### 2. 记忆系统迁移

#### 原方式 (v1.0)
```python
# 手动管理会话历史
session_history = []
session_history.append({"role": "user", "content": user_input})
session_history.append({"role": "assistant", "content": ai_response})
```

#### 新方式 (v2.0)
```python
# 智能记忆管理
from app.agents.v2 import MemoryBank

# 获取上下文
context = await memory_bank.get_context(
    session_id="session_123",
    user_id="user_123", 
    query=user_input
)

# 添加交互
await memory_bank.add_interaction(
    session_id="session_123",
    user_id="user_123",
    human_message=user_input,
    ai_message=ai_response
)
```

### 3. RAG系统迁移

#### 原方式 (v1.0)
```python
# 手动处理文档加载和检索
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma

loader = PyPDFLoader(file_path)
docs = loader.load()
vectorstore = Chroma.from_documents(docs)
results = vectorstore.similarity_search(query)
```

#### 新方式 (v2.0)
```python
# 统一RAG管理
from app.agents.v2 import RAGManager

# 添加文档
result = await rag_manager.add_document(
    tenant_id="user_123",
    file_path="document.pdf"
)

# 查询知识库
results = await rag_manager.query(
    tenant_id="user_123",
    query_text=query,
    top_k=5
)
```

### 4. Agent构建迁移

#### 原方式 (v1.0)
```python
# 手动构建LangGraph
from langgraph.graph import StateGraph
from app.agents.langgraph.agent_state import AgentState

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
# ... 手动添加节点和边
```

#### 新方式 (v2.0)
```python
# 使用工厂模式
from app.agents.v2 import AgentFactory, AgentConfig, AgentType

config = AgentConfig(
    agent_type=AgentType.STUDY_PLANNER,
    tenant_id="user_123",
    model_name="gpt-4o-mini"
)

executor = agent_factory.get_agent_executor(config)
response = await executor.execute(user_input)
```

## 📋 分步迁移计划

### 阶段1: 基础设施准备

1. **初始化v2架构**
```bash
# 创建必要的__init__.py文件
touch app/agents/v2/core_infrastructure/__init__.py
touch app/agents/v2/ai_foundation/__init__.py  
touch app/agents/v2/data_communication/__init__.py
```

2. **配置管理器**
```python
# app/agents/v2/config.py
from .ai_foundation.llm.manager import llm_manager, embedding_manager
from .ai_foundation.memory.memory_bank import memory_bank
from .ai_foundation.agents.agent_factory import agent_factory
from .data_communication.rag.rag_manager import rag_manager

async def initialize_v2_architecture():
    """初始化v2架构"""
    # 配置LLM模型
    model_configs = [
        ModelConfig(
            name="gpt-4o-mini",
            provider=ModelProvider.OPENAI,
            api_key=settings.OPENAI_API_KEY
        )
    ]
    
    await llm_manager.initialize(model_configs)
    
    # 设置依赖关系
    memory_bank.llm_manager = llm_manager
    memory_bank.embedding_manager = embedding_manager
    agent_factory.llm_manager = llm_manager
    agent_factory.memory_bank = memory_bank
    agent_factory.rag_manager = rag_manager
```

### 阶段2: 现有代码迁移

1. **迁移agent_graph.py**
```python
# 原文件内容整合到新的AgentExecutor中
# 将现有的节点逻辑迁移到AgentExecutor的节点方法中
```

2. **迁移agent_tools.py**
```python
# 将工具注册到新的ToolRegistry中
from app.agents.v2.ai_foundation.agents.agent_factory import agent_factory

# 注册现有工具
async def migrate_tools():
    # 迁移数据库工具
    from app.agents.tools.database_tools import search_mentors
    agent_factory.register_tool("search_mentors", search_mentors)
    
    # 迁移其他工具...
```

3. **迁移knowledge_base.py**
```python
# 现有知识库逻辑迁移到RAGManager中
# 使用新的文档加载和检索接口
```

### 阶段3: API适配

1. **更新路由器**
```python
# app/api/routers/planner_router.py
from app.agents.v2 import AgentFactory, AgentConfig, AgentType

@router.post("/invoke")
async def invoke_agent_v2(request: PlannerRequest):
    config = AgentConfig(
        agent_type=AgentType.STUDY_PLANNER,
        tenant_id=request.session_id,
        model_name="gpt-4o-mini"
    )
    
    executor = agent_factory.get_agent_executor(config)
    response = await executor.execute(request.input)
    
    return {"output": response}
```

2. **兼容性支持**
```python
# 保持v1 API兼容性
@router.post("/invoke/v1")
async def invoke_agent_v1(request: PlannerRequest):
    # 使用v1逻辑（过渡期间）
    pass

@router.post("/invoke/v2") 
async def invoke_agent_v2(request: PlannerRequest):
    # 使用v2架构
    pass
```

### 阶段4: 测试和验证

1. **创建迁移测试**
```python
# test/agents/test_v2_migration.py
import pytest
from app.agents.v2 import AgentFactory, AgentConfig, AgentType

@pytest.mark.asyncio
async def test_v2_agent_execution():
    config = AgentConfig(
        agent_type=AgentType.STUDY_PLANNER,
        tenant_id="test_user",
        model_name="gpt-4o-mini"
    )
    
    executor = agent_factory.get_agent_executor(config)
    response = await executor.execute("我想申请美国大学")
    
    assert response is not None
    assert len(response) > 0
```

2. **性能对比测试**
```python
# 比较v1和v2的性能差异
async def benchmark_v1_vs_v2():
    # 测试响应时间、内存使用等
    pass
```

## 🔧 迁移工具

### 自动迁移脚本
```python
# migrate_to_v2.py
import os
import shutil
from pathlib import Path

class AgentMigrator:
    def __init__(self):
        self.v1_path = Path("app/agents")
        self.v2_path = Path("app/agents/v2")
    
    async def migrate_tools(self):
        """迁移工具函数"""
        # 分析现有工具并生成新的注册代码
        pass
    
    async def migrate_prompts(self):
        """迁移提示词"""
        # 提取现有提示词并转换为新格式
        pass
    
    async def generate_config(self):
        """生成v2配置文件"""
        # 基于现有配置生成新的配置
        pass

# 运行迁移
migrator = AgentMigrator()
await migrator.migrate_all()
```

## ⚠️ 注意事项

### 兼容性问题

1. **API变更**
   - 响应格式可能有变化
   - 需要更新前端调用

2. **依赖变更**
   - 可能需要安装新的依赖包
   - 检查requirements.txt

3. **配置变更**
   - 环境变量可能需要调整
   - 数据库表结构可能需要更新

### 回滚计划

```python
# 保留v1代码作为备份
# 重命名而不是删除
mv app/agents/langgraph app/agents/langgraph_v1_backup
mv app/agents/planner_agent.py app/agents/planner_agent_v1_backup.py
```

## 📊 迁移检查清单

### 迁移前检查
- [ ] 备份现有代码
- [ ] 记录当前API响应格式
- [ ] 测试现有功能
- [ ] 确认依赖版本

### 迁移过程中
- [ ] 逐步迁移核心组件
- [ ] 保持API兼容性
- [ ] 编写迁移测试
- [ ] 监控性能变化

### 迁移后验证
- [ ] 所有测试通过
- [ ] API响应正常
- [ ] 性能符合预期
- [ ] 清理旧代码

## 🎯 迁移完成标准

### 功能完整性
- ✅ 所有原有功能正常工作
- ✅ 新增功能按预期运行
- ✅ API响应格式正确

### 性能指标
- ✅ 响应时间 <= 原架构的120%
- ✅ 内存使用合理
- ✅ 并发处理能力不降低

### 代码质量
- ✅ 代码覆盖率 >= 80%
- ✅ 没有重大安全漏洞
- ✅ 文档完整

## 🚀 迁移后的优势

### 立即收益
- 🎯 **统一接口**: 所有AI能力通过管理器访问
- 🔒 **错误处理**: 标准化的异常处理
- 📊 **监控支持**: 内置使用统计和监控

### 长期收益  
- 🏗️ **可扩展性**: 轻松添加新模型和工具
- 🏢 **企业特性**: 多租户、权限控制
- 🔄 **维护性**: 模块化架构便于维护

---

**🎊 迁移完成后，您将拥有一个企业级的AI智能体基础设施！** 