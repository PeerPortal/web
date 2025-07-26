# 🛠️ PeerPortal AI智能体系统 v2.0 配置指南

## 📋 配置概览

新的v2.0智能体系统支持灵活的配置方式，既可以只使用基础功能，也可以配置完整的企业级功能。

### 🎯 配置层级

| 配置级别 | 描述 | 所需服务 | 适用场景 |
|----------|------|----------|----------|
| **🟢 基础配置** | 仅AI功能 | OpenAI API | 开发测试 |
| **🟡 增强配置** | +记忆缓存 | OpenAI + Redis | 生产环境 |
| **🔴 完整配置** | 全部功能 | OpenAI + Redis + Milvus + MongoDB + ES | 企业级部署 |

---

## 🚀 快速开始（基础配置）

### 1. 环境变量配置

创建 `.env` 文件，添加必需的配置：

```bash
# === 必需配置 ===
# OpenAI API密钥（必需）
OPENAI_API_KEY=sk-your-openai-api-key-here

# 应用基础配置
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

# Supabase配置（如果使用现有数据库）
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
SUPABASE_DB_PASSWORD=your-database-password
```

### 2. 基础初始化

```python
# 方式1：在FastAPI应用中初始化
from app.agents.v2.config import init_v2_from_settings
from app.core.config import settings

async def startup_event():
    success = await init_v2_from_settings(settings)
    if success:
        print("✅ v2.0智能体系统已就绪")
    else:
        print("❌ 初始化失败")

# 方式2：直接从环境变量初始化
from app.agents.v2.config import init_v2_from_env

async def init():
    success = await init_v2_from_env()
    return success
```

### 3. 立即使用

```python
from app.agents.v2 import create_study_planner

# 创建智能体
agent = create_study_planner("user_123")

# 开始对话
response = await agent.execute("我想申请美国大学")
print(response)
```

---

## 🔧 详细配置选项

### 必需配置

```bash
# OpenAI API密钥 - 核心AI功能必需
OPENAI_API_KEY=sk-your-openai-api-key-here

# 基础应用配置
DEBUG=true                          # 调试模式
SECRET_KEY=your-secret-key         # JWT密钥
```

### 可选增强配置

```bash
# === 记忆系统配置 ===
# Redis - 用于短期记忆缓存（推荐）
REDIS_URL=redis://localhost:6379

# === 知识库配置 ===
# Milvus - 向量数据库，用于长期记忆和RAG
MILVUS_HOST=localhost
MILVUS_PORT=19530

# MongoDB - 文档数据库，用于记忆摘要存储
MONGODB_URL=mongodb://localhost:27017/peerportal

# Elasticsearch - 搜索引擎，用于关键词检索
ELASTICSEARCH_URL=http://localhost:9200

# === LangSmith配置（AI监控）===
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_your_api_key
LANGCHAIN_PROJECT=PeerPortal-v2
```

### Agent性能配置

```bash
# Agent执行配置
AGENT_MAX_ITERATIONS=10           # 最大思考轮数
AGENT_TIMEOUT_SECONDS=300         # 超时时间

# 模型配置
DEFAULT_MODEL=gpt-4o-mini         # 默认模型
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002

# 记忆配置
MEMORY_SESSION_TTL=86400          # 会话记忆保持时间（秒）
MEMORY_DECAY_DAYS=30              # 长期记忆衰减周期（天）

# RAG配置
RAG_CHUNK_SIZE=1000               # 文档分块大小
RAG_CHUNK_OVERLAP=200             # 分块重叠长度
RAG_TOP_K=5                       # 默认检索数量
```

---

## 📊 配置方案对比

### 🟢 基础配置

**适用**: 开发测试、个人使用

```bash
# 最小配置
OPENAI_API_KEY=sk-xxx
DEBUG=true
SECRET_KEY=your-secret-key
```

**功能**:
- ✅ AI对话
- ✅ 4种专业智能体
- ✅ 工具调用
- ❌ 记忆功能（仅会话内记忆）
- ❌ 知识库检索
- ❌ 长期记忆

### 🟡 增强配置

**适用**: 小团队、生产环境

```bash
# 基础配置 +
REDIS_URL=redis://localhost:6379
```

**功能**:
- ✅ 基础配置所有功能
- ✅ 短期记忆缓存
- ✅ 会话管理
- ❌ 长期记忆
- ❌ 知识库检索

### 🔴 完整配置

**适用**: 企业级部署

```bash
# 增强配置 +
MILVUS_HOST=localhost
MONGODB_URL=mongodb://localhost:27017
ELASTICSEARCH_URL=http://localhost:9200
```

**功能**:
- ✅ 所有功能
- ✅ 智能记忆系统
- ✅ RAG知识库
- ✅ 混合检索
- ✅ 记忆压缩和遗忘

---

## 🐳 Docker部署配置

### docker-compose.yml

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - MILVUS_HOST=milvus
      - MONGODB_URL=mongodb://mongodb:27017/peerportal
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    depends_on:
      - redis
      - milvus
      - mongodb
      - elasticsearch

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  milvus:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"

  elasticsearch:
    image: elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
```

### 启动命令

```bash
# 创建.env文件
echo "OPENAI_API_KEY=your-api-key" > .env

# 启动服务栈
docker-compose up -d

# 查看日志
docker-compose logs -f app
```

---

## 🧪 配置验证

### 1. 创建测试脚本

```python
# test_v2_config.py
import asyncio
from app.agents.v2.config import config_manager, init_v2_from_env
from app.agents.v2 import create_study_planner

async def test_configuration():
    """测试v2.0配置"""
    print("🧪 测试v2.0智能体系统配置...")
    
    # 1. 初始化系统
    success = await init_v2_from_env()
    if not success:
        print("❌ 初始化失败")
        return
    
    # 2. 检查配置状态
    status = config_manager.get_config_status()
    print(f"📊 配置状态: {status}")
    
    # 3. 测试智能体创建
    try:
        agent = create_study_planner("test_user")
        print("✅ 智能体创建成功")
    except Exception as e:
        print(f"❌ 智能体创建失败: {e}")
        return
    
    # 4. 测试基本对话
    try:
        response = await agent.execute("你好，请介绍一下你的功能")
        print(f"✅ 对话测试成功: {response[:100]}...")
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        return
    
    print("🎉 所有测试通过！v2.0系统配置正确")

if __name__ == "__main__":
    asyncio.run(test_configuration())
```

### 2. 运行测试

```bash
cd backend
python test_v2_config.py
```

### 3. 预期输出

```
🧪 测试v2.0智能体系统配置...

🎯 PeerPortal AI智能体架构v2.0 配置摘要
==================================================
🤖 LLM模型: 3个
📊 嵌入模型: 3个
💾 Redis缓存: ✅ 已配置
🔍 Milvus向量库: ✅ 已配置
📄 MongoDB文档库: ✅ 已配置
🔎 Elasticsearch搜索: ✅ 已配置
🐛 调试模式: ✅ 开启
==================================================

✅ PeerPortal AI智能体架构v2.0初始化完成
📊 配置状态: {'is_initialized': True, 'config_loaded': True, ...}
✅ 智能体创建成功
✅ 对话测试成功: 你好！我是PeerPortal的AI留学规划师...
🎉 所有测试通过！v2.0系统配置正确
```

---

## 🔗 集成到现有应用

### FastAPI集成

```python
# app/main.py
from fastapi import FastAPI
from app.agents.v2.config import init_v2_from_settings
from app.core.config import settings

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化v2.0系统"""
    print("🚀 初始化AI智能体系统v2.0...")
    success = await init_v2_from_settings(settings)
    if success:
        print("✅ v2.0智能体系统已就绪")
    else:
        print("❌ v2.0系统初始化失败，使用降级模式")

# 新的v2.0 API端点
@app.post("/api/v2/agent/chat")
async def chat_with_agent(request: ChatRequest):
    from app.agents.v2 import create_study_planner
    
    agent = create_study_planner(request.user_id)
    response = await agent.execute(request.message)
    
    return {"response": response}
```

### 现有路由器更新

```python
# app/api/routers/planner_router.py
from app.agents.v2 import create_study_planner
from app.agents.v2.config import config_manager

@router.post("/invoke/v2")
async def invoke_agent_v2(request: PlannerRequest):
    """v2.0智能体调用接口"""
    if not config_manager.is_initialized:
        raise HTTPException(status_code=503, detail="v2.0系统未初始化")
    
    # 根据需求选择智能体类型
    if request.agent_type == "study_planner":
        agent = create_study_planner(request.session_id)
    elif request.agent_type == "essay_reviewer":
        from app.agents.v2 import create_essay_reviewer
        agent = create_essay_reviewer(request.session_id)
    # ... 其他类型
    
    response = await agent.execute(request.input)
    
    return {
        "output": response,
        "version": "v2.0",
        "agent_type": request.agent_type
    }
```

---

## ⚠️ 故障排除

### 常见问题

1. **OpenAI API Key错误**
```bash
Error: Invalid OpenAI API key
解决: 检查OPENAI_API_KEY环境变量是否正确设置
```

2. **Redis连接失败**
```bash
Warning: redis package not installed, using local memory for caching
解决: pip install redis 或忽略（会使用本地内存）
```

3. **导入错误**
```bash
ImportError: No module named 'app.agents.v2'
解决: 确保从正确的目录运行，或检查PYTHONPATH
```

4. **初始化失败**
```bash
❌ v2.0架构初始化失败
解决: 检查日志，通常是配置问题或依赖缺失
```

### 诊断工具

```python
# 快速诊断
from app.agents.v2.config import config_manager

# 检查配置状态
status = config_manager.get_config_status()
print(status)

# 检查环境变量
import os
required_vars = ['OPENAI_API_KEY']
for var in required_vars:
    value = os.getenv(var)
    print(f"{var}: {'✅ 已设置' if value else '❌ 未设置'}")
```

---

## 📈 性能优化配置

### 生产环境优化

```bash
# 性能配置
DEBUG=false                        # 关闭调试模式
AGENT_TIMEOUT_SECONDS=60          # 降低超时时间
AGENT_MAX_ITERATIONS=5            # 限制思考轮数

# 连接池配置
DB_POOL_MIN_SIZE=5                # 数据库连接池
DB_POOL_MAX_SIZE=20

# 缓存配置
REDIS_MAX_CONNECTIONS=20          # Redis连接池
REDIS_RETRY_ON_TIMEOUT=true       # 重试机制
```

### 模型选择

```python
# 成本优化：使用更便宜的模型
DEFAULT_MODEL=gpt-3.5-turbo       # 而不是gpt-4

# 性能优化：使用更快的模型
DEFAULT_MODEL=gpt-4o-mini         # 平衡性能和成本

# 质量优化：使用最好的模型
DEFAULT_MODEL=gpt-4               # 最高质量
```

---

## 🎯 总结

**v2.0智能体系统配置的关键点**：

1. **🟢 基础配置**: 只需要`OPENAI_API_KEY`就能运行
2. **🔄 渐进式增强**: 可以逐步添加更多服务
3. **🛡️ 优雅降级**: 外部服务不可用时会自动使用本地替代
4. **📊 状态监控**: 提供详细的配置状态信息
5. **🧪 易于测试**: 内置测试和验证工具

**推荐配置路径**：
```
基础配置（开发） → 增强配置（测试） → 完整配置（生产）
```

现在您可以根据需求选择合适的配置级别，快速启动v2.0智能体系统！🚀

有什么具体的配置问题需要解决吗？ 