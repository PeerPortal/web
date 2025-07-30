# PeerPortal AI智能体系统 v2.0 启动和测试指南

## 🎯 系统概述

PeerPortal AI智能体系统 v2.0 是专注于留学规划和咨询的智能体平台，提供两个核心智能体：

- **🎓 留学规划师 (Study Planner)**: 个性化申请策略、选校建议、时间规划
- **💬 留学咨询师 (Study Consultant)**: 留学问答、政策解读、经验分享

## 🚀 快速启动

### 方法1：一键启动脚本（推荐）

```bash
# 在backend目录下执行
./start_agents_v2.sh
```

然后选择启动选项：
- `[1]` 前台启动服务器（适合开发调试）
- `[2]` 后台启动服务器（适合生产环境）
- `[3]` 运行系统配置测试
- `[4]` 运行API功能测试

### 方法2：手动启动

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 加载环境变量
set -a && source .env && set +a

# 3. 启动服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 测试系统

### 1. 系统配置测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行配置测试
python test_v2_config.py
```

**期望结果**：
- ✅ 环境变量配置正确
- ✅ 智能体系统初始化成功
- ✅ 智能体创建成功
- ✅ 工具导入成功

### 2. API功能测试

```bash
# 确保服务器已启动，然后运行
python test_agents_api.py
```

**测试项目**：
- 🔍 服务器健康检查
- 🤖 智能体系统状态
- 🏗️ 架构信息获取
- 🩺 智能体健康检查
- 🎓 留学规划师功能
- 💬 留学咨询师功能

### 3. 手动API测试

服务器启动后，访问以下地址：

#### 📊 系统状态检查
```bash
curl http://localhost:8000/api/v2/agents/status
```

#### 🎓 测试留学规划师
```bash
curl -X POST "http://localhost:8000/api/v2/agents/planner/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想申请美国大学的计算机科学专业，请给我一些建议",
    "user_id": "test_user_123"
  }'
```

#### 💬 测试留学咨询师
```bash
curl -X POST "http://localhost:8000/api/v2/agents/consultant/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "留学美国的总费用大概是多少？",
    "user_id": "test_user_456"
  }'
```

## 🌐 Web界面测试

### API文档界面

访问 **http://localhost:8000/docs** 获得交互式API文档，可以直接测试所有API端点。

### 主要API端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/agents/status` | GET | 获取系统状态 |
| `/api/v2/agents/info` | GET | 获取架构信息 |
| `/api/v2/agents/health` | GET | 健康检查 |
| `/api/v2/agents/planner/chat` | POST | 留学规划师对话 |
| `/api/v2/agents/consultant/chat` | POST | 留学咨询师对话 |
| `/api/v2/agents/chat` | POST | 自动选择智能体 |

## 🔧 配置要求

### 必需配置

```bash
# .env文件
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 可选配置（增强功能）

```bash
# Redis缓存（提升记忆性能）
REDIS_URL=redis://localhost:6379

# 向量数据库（企业级知识库）
MILVUS_HOST=localhost
MILVUS_PORT=19530

# 文档数据库（长期记忆）
MONGODB_URL=mongodb://localhost:27017

# 搜索引擎（高级检索）
ELASTICSEARCH_URL=http://localhost:9200

# 调试模式
DEBUG=true
```

## 🐛 故障排除

### 常见问题

#### 1. 服务器启动失败

**问题**：`ImportError: No module named 'xxx'`
**解决**：
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. OpenAI API错误

**问题**：`Authentication Error`
**解决**：检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确

#### 3. 端口被占用

**问题**：`Address already in use`
**解决**：
```bash
# 查找占用端口的进程
lsof -i :8000

# 终止进程
kill -9 <PID>
```

#### 4. 智能体对话失败

**问题**：对话返回错误或空回复
**检查**：
- OpenAI API Key是否有效
- 网络连接是否正常
- 查看服务器日志：`tail -f server.log`

### 日志查看

```bash
# 实时查看服务器日志
tail -f server.log

# 查看最近的错误
grep "ERROR" server.log | tail -10
```

## 📈 性能优化

### 基础配置（最小启动）
- 只需要 OpenAI API Key
- 使用内存缓存和模拟存储

### 增强配置（推荐）
- 添加 Redis 提升记忆性能
- 支持跨会话对话记忆

### 完整配置（企业级）
- 部署 Milvus、MongoDB、Elasticsearch
- 获得完整的知识库和检索功能

## 🎯 使用场景

### 留学规划师使用示例

```json
{
  "message": "我想申请美国大学的计算机科学专业，我的GPA是3.5，托福100分，请帮我制定申请策略",
  "user_id": "student_001"
}
```

**期望回复**：详细的申请策略，包括学校推荐、时间规划、材料准备等。

### 留学咨询师使用示例

```json
{
  "message": "请问美国研究生申请需要哪些材料？签证流程是怎样的？",
  "user_id": "student_002"
}
```

**期望回复**：详细的材料清单和签证流程说明。

## 🔄 版本兼容性

v2.0系统保持了向后兼容性：

- 旧版API路径 `/api/v1/planner/invoke` 仍然可用
- v1和v2可以同时运行
- 前端可以渐进式迁移到v2 API

## 📞 技术支持

如果遇到问题：

1. 📖 查阅本指南的故障排除部分
2. 🔍 检查 `server.log` 日志文件
3. 🧪 运行 `python test_v2_config.py` 诊断配置
4. 🌐 访问 http://localhost:8000/docs 测试API

---

## 🎉 快速开始checklist

- [ ] ✅ 激活虚拟环境：`source venv/bin/activate`
- [ ] ✅ 配置环境变量：确保 `.env` 文件包含 `OPENAI_API_KEY`
- [ ] ✅ 启动服务器：`./start_agents_v2.sh` 或手动启动
- [ ] ✅ 访问API文档：http://localhost:8000/docs
- [ ] ✅ 测试智能体：运行 `python test_agents_api.py`
- [ ] ✅ 开始使用：调用 `/api/v2/agents/planner/chat` 或 `/api/v2/agents/consultant/chat`

恭喜！您的PeerPortal AI智能体系统 v2.0 已经可以使用了！🚀 