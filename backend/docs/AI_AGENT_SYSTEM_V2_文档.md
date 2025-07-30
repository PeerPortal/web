# 🤖 PeerPortal AI智能体系统 v2.0 - 完整文档

## 📖 系统概述

**PeerPortal AI智能体系统 v2.0** 是一个专注于留学规划和咨询的智能化AI服务平台。系统基于先进的大语言模型和LangGraph架构，提供个性化的留学申请策略、专业咨询服务和智能化工具支持。

### 🎯 核心价值

- **个性化规划**: 基于用户背景提供定制化留学申请策略
- **专业咨询**: 覆盖留学申请全流程的专业指导
- **智能记忆**: 跨会话的对话记忆和上下文理解
- **工具集成**: 集成多种实用工具提升服务质量
- **可扩展架构**: 模块化设计支持功能扩展

---

## 🏗️ 系统架构

### 总体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI 应用层                           │
├─────────────────────────────────────────────────────────────┤
│                AI智能体系统 v2.0                            │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   留学规划师    │    │   留学咨询师    │                │
│  │ StudyPlanner    │    │StudyConsultant  │                │
│  └─────────────────┘    └─────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│                    核心基础设施层                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  LLM管理 │ │ 记忆银行 │ │ RAG系统  │ │ 工具注册 │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    数据通信层                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │
│  │  Redis   │ │  Milvus  │ │ MongoDB  │                   │
│  └──────────┘ └──────────┘ └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### 核心模块

#### 1. **AI Foundation Layer (AI基础层)**
- **LLM Manager**: 大语言模型统一管理
- **Memory Bank**: 双层记忆架构（短期+长期）
- **Agent Factory**: 智能体动态创建工厂
- **Embedding Manager**: 向量嵌入服务

#### 2. **Core Infrastructure (核心基础设施)**
- **Error Handling**: 统一异常处理
- **Storage Manager**: 对象存储管理
- **Utilities**: 通用工具函数

#### 3. **Data Communication (数据通信)**
- **RAG Manager**: 检索增强生成
- **Channels**: 通信渠道管理

#### 4. **Tools Layer (工具层)**
- **Study Tools**: 留学专用工具集
- **External APIs**: 外部服务集成

---

## 🎓 智能体类型

### 1. 留学规划师 (StudyPlannerAgent)

**核心功能**:
- 🎯 个性化申请策略制定
- 🏫 院校和专业推荐
- 📅 申请时间规划
- 📋 材料准备指导

**特色能力**:
- 基于学术背景分析最佳申请路径
- 结合历史数据提供录取概率评估  
- 制定详细的申请时间线
- 提供个性化的背景提升建议

**使用场景**:
```
用户: "我想申请美国大学的计算机科学专业，请给我一些建议"
规划师: "当然可以！为了更好地为你提供个性化的建议，我需要了解一些关于你的背景信息..."
```

### 2. 留学咨询师 (StudyConsultantAgent)

**核心功能**:
- 💬 留学政策解读
- 🌍 各国教育体系介绍
- 💰 费用和奖学金咨询
- 🏠 生活和文化指导

**特色能力**:
- 实时政策信息获取
- 多国留学方案对比
- 签证申请流程指导
- 海外生活经验分享

**使用场景**:
```
用户: "美国留学的费用大概是多少？"
咨询师: "美国留学费用因学校类型、地理位置和专业而异..."
```

---

## 🧠 核心技术特性

### 1. 双层记忆架构

#### 短期记忆 (Working Memory)
- **存储**: Redis / 本地缓存
- **内容**: 当前会话历史
- **生命周期**: 24小时
- **功能**: 维持对话连续性

#### 长期记忆 (Long-term Memory)  
- **存储**: Milvus + MongoDB
- **内容**: 压缩后的历史会话
- **生命周期**: 永久存储
- **功能**: 个性化知识积累

### 2. 检索增强生成 (RAG)

```python
# RAG 工作流程
用户查询 → 向量嵌入 → 相似度检索 → 知识增强 → 生成回答
```

**支持的文档类型**:
- PDF 文件
- Word 文档  
- 纯文本文件
- HTML 网页
- Markdown 文档

### 3. LangGraph 状态机

```python
# 智能体决策流程
思考节点 → 记忆检索 → 知识检索 → 工具调用 → 响应生成
```

**节点类型**:
- **Think Node**: 分析用户意图
- **Memory Node**: 检索历史记忆
- **Knowledge Node**: 获取相关知识
- **Tool Node**: 调用外部工具
- **Response Node**: 生成最终回答

### 4. 智能工具集成

#### 内置工具
- **find_mentors_tool**: 查找引路人
- **find_services_tool**: 查找服务
- **get_platform_stats_tool**: 平台统计
- **web_search_tool**: 网络搜索

#### 扩展能力
- 支持自定义工具注册
- 动态工具加载
- 工具调用链管理

---

## 🚀 快速开始

### 1. 环境配置

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp configs/env_example.txt .env
```

### 2. 必需环境变量

```bash
# OpenAI API (必需)
OPENAI_API_KEY=sk-proj-xxx

# 可选配置
REDIS_URL=redis://localhost:6379
MILVUS_HOST=localhost
MONGODB_URL=mongodb://localhost:27017
DEBUG=True
```

### 3. 快速测试

```python
# 测试系统配置
python test_v2_config.py

# 启动服务
python -m uvicorn app.main:app --reload
```

---

## 💻 API 使用指南

### 1. RESTful API

#### 留学规划师对话
```http
POST /api/v2/agents/planner/chat
Content-Type: application/json

{
  "message": "我想申请美国大学CS专业",
  "user_id": "user_123"
}
```

#### 留学咨询师对话
```http
POST /api/v2/agents/consultant/chat
Content-Type: application/json

{
  "message": "美国留学费用是多少？",
  "user_id": "user_123"
}
```

#### 系统状态检查
```http
GET /api/v2/agents/status
```

### 2. Python SDK

```python
from app.agents.v2 import create_study_planner, create_study_consultant

# 创建留学规划师
planner = create_study_planner("user_123")
response = await planner.execute("我想申请美国大学CS专业")

# 创建留学咨询师
consultant = create_study_consultant("user_123") 
response = await consultant.execute("美国留学的费用大概是多少？")
```

### 3. 流式响应

```python
# 流式对话（即将支持）
async for chunk in planner.stream("我的背景是..."):
    print(chunk.content)
```

---

## 🔧 系统配置

### 1. 模型配置

```python
# 支持的模型
LLM_MODELS = [
    "gpt-4o-mini",      # 默认模型（经济高效）
    "gpt-4",            # 高质量模型
    "gpt-3.5-turbo"     # 快速响应模型
]

EMBEDDING_MODELS = [
    "text-embedding-ada-002",    # 默认嵌入模型
    "text-embedding-3-small",    # 新版小型模型  
    "text-embedding-3-large"     # 新版大型模型
]
```

### 2. 记忆配置

```python
# 记忆系统配置
MEMORY_SETTINGS = {
    "session_ttl": 24 * 3600,      # 会话过期时间（秒）
    "max_session_history": 50,      # 最大历史记录数
    "compression_threshold": 10,     # 压缩触发阈值
    "relevance_threshold": 0.7       # 相关性阈值
}
```

### 3. RAG 配置

```python
# RAG 系统配置
RAG_SETTINGS = {
    "chunk_size": 1000,             # 文档块大小
    "chunk_overlap": 200,           # 重叠大小
    "top_k": 5,                     # 检索数量
    "similarity_threshold": 0.6      # 相似度阈值
}
```

---

## 📊 性能监控

### 1. 系统指标

```python
# 当前系统状态
{
    "🤖 LLM模型": 3,
    "📊 嵌入模型": 3, 
    "💾 Redis缓存": "✅ 已配置",
    "🔍 Milvus向量库": "⚪ 未配置",
    "📄 MongoDB文档库": "⚪ 未配置",
    "🐛 调试模式": "✅ 开启"
}
```

### 2. 性能优化

#### 响应时间优化
- 模型选择策略（经济 vs 质量）
- 缓存机制（Redis 短期记忆）
- 异步处理（并发请求支持）

#### 成本控制
- Token 使用监控
- 模型调用频率限制
- 智能路由（简单问题使用小模型）

---

## 🛠️ 扩展开发

### 1. 添加新智能体

```python
# 1. 定义智能体类型
class AgentType(str, Enum):
    ESSAY_REVIEWER = "essay_reviewer"     # 文书润色师
    INTERVIEW_COACH = "interview_coach"   # 面试指导师

# 2. 创建智能体类
class EssayReviewerAgent:
    def __init__(self, tenant_id: str):
        self.config = AgentConfig(
            agent_type=AgentType.ESSAY_REVIEWER,
            tenant_id=tenant_id,
            system_prompt="你是专业的留学文书指导师..."
        )

# 3. 注册路由
@router.post("/essay-reviewer/chat")
async def chat_with_essay_reviewer(request: ChatRequest):
    agent = create_essay_reviewer(request.user_id)
    return await agent.execute(request.message)
```

### 2. 添加自定义工具

```python
# 1. 定义工具函数
async def scholarship_search_tool(
    country: str, 
    field: str, 
    amount_min: int = 0
) -> str:
    """搜索奖学金信息"""
    # 实现搜索逻辑
    results = await search_scholarships(country, field, amount_min)
    return format_scholarship_results(results)

# 2. 注册工具
tool_registry.register_tool("scholarship_search", scholarship_search_tool)

# 3. 配置智能体工具
agent_config.tools = ["scholarship_search", "web_search_tool"]
```

### 3. 扩展记忆系统

```python
# 添加专业记忆类型
class ApplicationMemory(MemoryItem):
    application_status: str
    deadline: datetime
    progress: Dict[str, bool]

# 自定义记忆检索逻辑
class ApplicationMemoryBank(MemoryBank):
    async def get_application_context(self, user_id: str) -> ApplicationMemory:
        # 实现申请状态记忆检索
        pass
```

---

## 🔒 安全与隐私

### 1. 数据安全

- **API 认证**: JWT Token 验证
- **数据加密**: 敏感信息加密存储
- **访问控制**: 基于角色的权限管理
- **审计日志**: 完整的操作记录

### 2. 隐私保护

- **数据脱敏**: 个人信息匿名化处理
- **本地处理**: 敏感数据本地计算
- **删除权**: 用户数据删除接口
- **透明度**: 数据使用说明

---

## 🚨 故障排除

### 1. 常见问题

#### Q: 智能体响应缓慢
**A**: 检查以下配置
```bash
# 1. 检查 OpenAI API 连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     "https://api.openai.com/v1/models"

# 2. 检查 Redis 连接
redis-cli ping

# 3. 优化模型选择
DEFAULT_MODEL=gpt-4o-mini  # 使用更快的模型
```

#### Q: 记忆功能异常
**A**: 检查记忆组件状态
```python
# 检查记忆银行状态
memory_status = await memory_bank.health_check()
print(f"记忆系统状态: {memory_status}")

# 清除缓存
await memory_bank.clear_cache(user_id)
```

#### Q: RAG 检索效果差
**A**: 调整检索参数
```python
# 降低相似度阈值
RAG_SIMILARITY_THRESHOLD = 0.5

# 增加检索数量
RAG_TOP_K = 10

# 重新索引文档
await rag_manager.reindex_documents()
```

### 2. 日志分析

```bash
# 查看系统日志
tail -f logs/app.log

# 查看 AI 调用日志
grep "LLM_CALL" logs/app.log | tail -20

# 查看错误日志
grep "ERROR" logs/app.log | tail -10
```

---

## 📈 版本历史

### v2.0.0 (当前版本)
- ✅ 完整的双智能体系统
- ✅ LangGraph 状态机架构
- ✅ 双层记忆系统
- ✅ RAG 知识检索
- ✅ 工具集成框架
- ✅ FastAPI REST 接口

### 未来规划 (v2.1.0)
- 🔄 流式响应支持
- 🎯 更多智能体类型
- 🌐 多语言支持
- 📱 移动端优化
- 🔍 高级分析仪表板

---

## 🤝 贡献指南

### 1. 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/yourrepo/peerpotal.git

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black app/
isort app/
```

### 2. 提交规范

```bash
# 功能开发
git commit -m "feat: 添加文书润色智能体"

# Bug 修复  
git commit -m "fix: 修复记忆检索空指针异常"

# 文档更新
git commit -m "docs: 更新 API 使用指南"
```

### 3. 测试指南

```python
# 单元测试
pytest tests/test_agents.py

# 集成测试
pytest tests/test_integration.py

# 性能测试
pytest tests/test_performance.py --benchmark
```

---

## 📞 技术支持

### 官方资源
- **文档**: `/docs` 目录
- **API 文档**: `http://localhost:8000/docs`
- **测试工具**: `test_v2_config.py`

### 社区支持
- **GitHub Issues**: 问题报告和功能请求
- **讨论区**: 技术交流和经验分享
- **Wiki**: 详细的开发文档

---

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

**🎓 让 AI 成为每一位留学申请者的专业顾问！**

*最后更新: 2024年12月* 