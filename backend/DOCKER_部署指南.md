# 🐳 PeerPortal AI智能体系统 - Docker部署指南

## 📖 概述

本指南帮助你使用Docker快速部署**PeerPortal AI智能体系统 v2.0**，包含留学规划师和留学咨询师两个核心AI智能体。

### 🎯 部署模式

| 模式 | 描述 | 包含服务 | 适用场景 |
|------|------|----------|----------|
| **快速启动** | 基础AI功能 | AI Agent + Redis | 开发测试 |
| **完整部署** | 企业级功能 | 上述 + Milvus + MongoDB | 生产环境 |
| **生产部署** | 包含反向代理 | 上述 + Nginx | 公网服务 |

---

## 🚀 快速开始 (30秒部署)

### 1. 前置要求

```bash
# 检查Docker版本
docker --version          # >= 20.10.0
docker-compose --version  # >= 1.29.0
```

### 2. 一键部署

```bash
# 1. 克隆项目 (如果还没有)
git clone https://github.com/yourrepo/peerpotal.git
cd peerpotal/backend

# 2. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 3. 选择 "1. 🚀 快速启动" 模式
```

### 3. 验证部署

```bash
# 检查服务状态
curl http://localhost:8000/health

# 测试AI对话
curl -X POST "http://localhost:8000/api/v2/agents/planner/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下你的功能", "user_id": "test_user"}'
```

---

## ⚙️ 手动部署

### 1. 环境配置

```bash
# 复制环境变量模板
cp docker-env-example.txt .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

**必需配置项**：
```bash
# OpenAI API密钥 (必须设置)
OPENAI_API_KEY=sk-proj-your-actual-api-key

# Supabase数据库配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_DB_PASSWORD=your-database-password
```

### 2. 构建镜像

```bash
# 构建AI Agent镜像
docker-compose build ai-agent

# 或强制重新构建
docker-compose build --no-cache ai-agent
```

### 3. 启动服务

#### 基础部署
```bash
docker-compose up -d ai-agent redis
```

#### 完整部署
```bash
docker-compose --profile full-stack up -d
```

#### 生产部署
```bash
docker-compose --profile production up -d
```

---

## 📊 服务架构

### 基础架构图
```
┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │     Redis       │
│   :8000         │◄──►│     :6379       │
│                 │    │   (短期记忆)     │
└─────────────────┘    └─────────────────┘
```

### 完整架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │     Redis       │    │    MongoDB      │
│   :8000         │◄──►│     :6379       │◄──►│     :27017      │
│                 │    │   (短期记忆)     │    │   (文档存储)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Milvus      │    │      Etcd       │    │     MinIO       │
│    :19530       │◄──►│     :2379       │    │   :9000/:9001   │
│   (向量数据库)   │    │   (协调服务)     │    │   (对象存储)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔧 配置说明

### 环境变量详解

#### 🔑 必需配置
```bash
# OpenAI API配置
OPENAI_API_KEY=sk-proj-xxx           # OpenAI API密钥
DEFAULT_MODEL=gpt-4o-mini            # 默认模型 (经济高效)
DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002

# 数据库配置
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx
```

#### ⚡ 性能配置
```bash
# Agent性能
AGENT_MAX_ITERATIONS=10              # 最大迭代次数
AGENT_TIMEOUT_SECONDS=300            # 超时时间(秒)

# 记忆系统
MEMORY_SESSION_TTL=86400             # 会话过期时间(24小时)

# Redis配置
REDIS_MAX_MEMORY=256mb               # Redis最大内存
```

#### 🔍 可选服务
```bash
# 向量数据库 (企业级)
MILVUS_PORT=19530
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# 监控追踪
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

### 数据卷配置

```yaml
volumes:
  - ./knowledge_base:/app/knowledge_base:ro    # 知识库(只读)
  - ./uploads:/app/uploads                     # 文件上传
  - ./logs:/app/logs                           # 日志文件
  - vector_store:/app/vector_store             # 向量存储
```

---

## 🛠️ 运维操作

### 日常管理

```bash
# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f ai-agent

# 重启特定服务
docker-compose restart ai-agent

# 更新服务
docker-compose pull
docker-compose up -d
```

### 性能监控

```bash
# 查看资源使用
docker stats

# 查看AI Agent日志
docker-compose logs ai-agent | grep "LLM_CALL"

# 检查健康状态
curl http://localhost:8000/health
curl http://localhost:8000/api/v2/agents/status
```

### 备份恢复

```bash
# 备份数据卷
docker run --rm -v peerportal_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .

# 恢复数据卷
docker run --rm -v peerportal_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz -C /data
```

---

## 🚨 故障排除

### 常见问题

#### Q1: AI Agent启动失败
```bash
# 检查日志
docker-compose logs ai-agent

# 常见原因:
# 1. OPENAI_API_KEY未设置或无效
# 2. 端口被占用
# 3. 内存不足
```

#### Q2: Redis连接失败
```bash
# 检查Redis状态
docker-compose ps redis

# 测试连接
docker-compose exec redis redis-cli ping

# 重启Redis
docker-compose restart redis
```

#### Q3: 响应缓慢
```bash
# 检查资源使用
docker stats

# 优化建议:
# 1. 增加Redis内存限制
# 2. 使用更快的模型 (gpt-4o-mini)
# 3. 增加系统内存
```

### 调试模式

```bash
# 启用调试模式
echo "DEBUG=true" >> .env
docker-compose restart ai-agent

# 查看详细日志
docker-compose logs -f ai-agent
```

### 重置系统

```bash
# 停止并清理所有数据
docker-compose down -v
docker volume prune -f

# 重新部署
./deploy.sh
```

---

## 🌐 生产部署

### 1. 安全配置

```bash
# 更新安全密钥
SECRET_KEY=your-super-secret-key-for-production

# 禁用调试模式
DEBUG=false

# 配置HTTPS (如果使用Nginx)
NGINX_SSL_PORT=443
```

### 2. 性能优化

```bash
# 增加并发工作进程
# 修改docker-compose.yml中的CMD:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# 增加资源限制
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2'
```

### 3. 监控配置

```bash
# 启用LangSmith监控
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=PeerPortal-AI-Agent-Production
```

### 4. 备份策略

```bash
# 创建定时备份脚本
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T mongodb mongodump --archive | gzip > backup_${DATE}.gz
```

---

## 📋 部署检查清单

### 部署前检查
- [ ] Docker和Docker Compose已安装
- [ ] OPENAI_API_KEY已配置
- [ ] Supabase数据库已配置
- [ ] 端口8000未被占用
- [ ] 系统内存 >= 4GB

### 部署后验证
- [ ] AI Agent服务正常运行 (`curl http://localhost:8000/health`)
- [ ] Redis缓存正常工作
- [ ] API文档可访问 (`http://localhost:8000/docs`)
- [ ] AI对话功能正常
- [ ] 日志无错误信息

### 生产环境额外检查
- [ ] HTTPS配置正确
- [ ] 防火墙规则已设置
- [ ] 备份策略已实施
- [ ] 监控告警已配置
- [ ] 负载均衡已配置 (如需要)

---

## 📞 技术支持

### 文档资源
- **完整文档**: `docs/AI_AGENT_SYSTEM_V2_文档.md`
- **快速入门**: `AI_AGENT_快速入门.md`
- **API文档**: `http://localhost:8000/docs`

### 常用命令参考
```bash
# 部署相关
./deploy.sh                           # 交互式部署
docker-compose up -d                  # 后台启动
docker-compose down                   # 停止服务
docker-compose restart ai-agent      # 重启AI服务

# 监控相关
docker-compose ps                     # 查看服务状态
docker-compose logs -f ai-agent      # 查看实时日志
docker stats                         # 查看资源使用

# 测试相关
curl http://localhost:8000/health     # 健康检查
python test_v2_config.py             # 本地测试
```

---

**🚀 开始你的AI智能体之旅！**

*最后更新: 2024年12月* 