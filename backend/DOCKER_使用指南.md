# PeerPortal AI智能体系统 v2.0 - Docker 使用指南

## 📋 目录

- [快速开始](#快速开始)
- [环境准备](#环境准备)
- [构建容器](#构建容器)
- [部署方式](#部署方式)
- [常用命令](#常用命令)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [安全建议](#安全建议)

## 🚀 快速开始

### 一键启动（推荐）

```bash
# 启动开发环境（支持热重载）
./docker-quick-start.sh dev

# 启动生产环境
./docker-quick-start.sh prod

# 查看帮助
./docker-quick-start.sh --help
```

### 传统方式启动

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 生产环境
docker-compose up -d
```

## 🔧 环境准备

### 1. 安装依赖

```bash
# macOS
brew install docker docker-compose

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp docker-env-example.txt .env

# 编辑配置
nano .env
```

**必需的环境变量：**

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here

# Supabase 数据库配置
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
SUPABASE_DB_PASSWORD=your_db_password

# 系统配置
SECRET_KEY=your_secret_key_change_in_production
DEBUG=false
```

### 3. 验证安装

```bash
# 检查 Docker 版本
docker --version
docker-compose --version

# 测试 Docker 运行
docker run hello-world
```

## 🏗️ 构建容器

### 使用构建脚本（推荐）

```bash
# 构建生产环境镜像
./docker-build.sh prod

# 构建开发环境镜像
./docker-build.sh dev

# 构建所有镜像
./docker-build.sh both

# 清理构建缓存
./docker-build.sh clean
```

### 手动构建

```bash
# 生产环境镜像
docker build -f Dockerfile -t peerportal-ai-agent:latest .

# 开发环境镜像
docker build -f Dockerfile.dev -t peerportal-ai-agent:dev .
```

### 构建选项说明

| 选项 | 说明 | 适用场景 |
|------|------|----------|
| `prod` | 生产环境镜像，多阶段构建，体积小 | 生产部署 |
| `dev` | 开发环境镜像，包含调试工具 | 本地开发 |
| `both` | 构建所有镜像 | 完整测试 |
| `clean` | 清理构建缓存 | 磁盘空间不足 |

## 🚀 部署方式

### 1. 开发环境部署

**特点：**
- 支持代码热重载
- 包含调试工具
- 较为宽松的健康检查

```bash
# 启动开发环境
./docker-quick-start.sh dev

# 启动并查看日志
./docker-quick-start.sh dev --logs

# 重新构建并启动
./docker-quick-start.sh dev --build
```

**可用服务：**
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- Redis：localhost:6380

### 2. 生产环境部署

**特点：**
- 优化的镜像大小
- 严格的健康检查
- 非特权用户运行

```bash
# 启动生产环境
./docker-quick-start.sh prod

# 启动完整生产环境（包含 Milvus）
./docker-quick-start.sh full
```

**可用服务：**
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- Redis：localhost:6379
- MongoDB：localhost:27017
- Milvus（full 模式）：localhost:19530

### 3. 工具环境部署

```bash
# 启动开发环境 + 管理工具
./docker-quick-start.sh tools
```

**额外服务：**
- Redis 管理界面：http://localhost:8081

### 4. Streamlit 界面部署

```bash
# 启动 Streamlit 界面
./docker-quick-start.sh streamlit
```

**服务：**
- Streamlit 界面：http://localhost:8501

## 📝 常用命令

### 服务管理

```bash
# 查看服务状态
./docker-quick-start.sh --status

# 停止所有服务
./docker-quick-start.sh --stop

# 重启服务
docker-compose restart ai-agent

# 查看日志
docker-compose logs -f ai-agent
```

### 镜像管理

```bash
# 查看镜像
docker images | grep peerportal

# 删除镜像
docker rmi peerportal-ai-agent:latest

# 清理未使用的镜像
docker image prune -f
```

### 容器管理

```bash
# 查看运行中的容器
docker ps

# 进入容器
docker exec -it peerportal-ai-agent-dev bash

# 查看容器资源使用
docker stats
```

### 数据管理

```bash
# 查看数据卷
docker volume ls

# 备份数据卷
docker run --rm -v peerportal_vector_store:/data -v $(pwd):/backup alpine tar czf /backup/vector_store_backup.tar.gz -C /data .

# 恢复数据卷
docker run --rm -v peerportal_vector_store:/data -v $(pwd):/backup alpine tar xzf /backup/vector_store_backup.tar.gz -C /data
```

## 🔍 故障排除

### 常见问题

#### 1. 端口占用

```bash
# 检查端口占用
lsof -i :8000
netstat -tlnp | grep 8000

# 解决方案：修改端口或停止占用进程
export PORT=8001
./docker-quick-start.sh dev
```

#### 2. 内存不足

```bash
# 检查容器内存使用
docker stats --no-stream

# 解决方案：增加 Docker 内存限制或优化代码
```

#### 3. 依赖包安装失败

```bash
# 清理构建缓存
./docker-build.sh clean

# 重新构建
./docker-build.sh prod --no-cache
```

#### 4. 数据库连接失败

```bash
# 检查环境变量
docker exec peerportal-ai-agent env | grep SUPABASE

# 检查网络连接
docker exec peerportal-ai-agent curl -I $SUPABASE_URL
```

### 调试技巧

#### 1. 进入容器调试

```bash
# 进入运行中的容器
docker exec -it peerportal-ai-agent-dev bash

# 运行临时容器进行调试
docker run -it --rm peerportal-ai-agent:dev bash
```

#### 2. 查看详细日志

```bash
# 查看容器启动日志
docker logs peerportal-ai-agent-dev

# 查看应用日志
docker exec peerportal-ai-agent-dev tail -f /app/logs/app.log
```

#### 3. 健康检查调试

```bash
# 手动执行健康检查
docker exec peerportal-ai-agent curl -f http://localhost:8000/health

# 查看健康检查历史
docker inspect peerportal-ai-agent | grep -A 10 Health
```

### 常见错误及解决方案

| 错误信息 | 可能原因 | 解决方案 |
|----------|----------|----------|
| `port already in use` | 端口被占用 | 修改 `.env` 中的端口配置 |
| `no space left on device` | 磁盘空间不足 | 清理 Docker 镜像和容器 |
| `connection refused` | 服务未启动 | 检查容器状态和日志 |
| `permission denied` | 权限不足 | 检查文件权限和用户配置 |

## ⚡ 性能优化

### 1. 镜像优化

```bash
# 使用生产镜像（更小的体积）
./docker-build.sh prod

# 清理不必要的镜像层
docker image prune -f
```

### 2. 资源限制

```yaml
# docker-compose.yml 中添加资源限制
services:
  ai-agent:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### 3. 缓存优化

```bash
# 预热缓存
docker exec peerportal-ai-agent python -c "from app.agents.v2 import create_study_planner; create_study_planner()"

# 监控缓存使用
docker exec peerportal-redis redis-cli info memory
```

## 🔒 安全建议

### 1. 环境变量安全

```bash
# 使用 Docker secrets（生产环境）
echo "your_api_key" | docker secret create openai_api_key -

# 避免在 Dockerfile 中硬编码密钥
# ❌ 错误
ENV OPENAI_API_KEY=sk-xxx

# ✅ 正确
ENV OPENAI_API_KEY=""
```

### 2. 网络安全

```bash
# 仅暴露必要端口
ports:
  - "127.0.0.1:8000:8000"  # 仅本地访问

# 使用自定义网络
networks:
  - app-network
```

### 3. 镜像安全

```bash
# 使用非特权用户
USER appuser

# 定期更新基础镜像
docker pull python:3.11-slim
./docker-build.sh prod
```

### 4. 数据安全

```bash
# 加密数据卷
docker volume create --driver encrypted vector_store

# 定期备份
./scripts/backup-data.sh
```

## 📊 监控和日志

### 1. 健康检查

```bash
# 手动健康检查
curl http://localhost:8000/health
curl http://localhost:8000/api/v2/agents/status

# 自动健康监控
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

### 2. 日志管理

```bash
# 查看应用日志
./docker-quick-start.sh dev --logs

# 日志轮转配置
docker run --log-driver=json-file --log-opt max-size=10m --log-opt max-file=3 peerportal-ai-agent
```

### 3. 性能监控

```bash
# 容器资源监控
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# 应用性能监控（如果启用）
curl http://localhost:8000/metrics
```

## 🆘 获取帮助

### 官方文档
- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)

### 项目相关
- [项目 README](./README.md)
- [API 文档](http://localhost:8000/docs)
- [部署指南](./DOCKER_部署指南.md)

### 社区支持
- [GitHub Issues](https://github.com/your-org/peerportal/issues)
- [Discord 社区](https://discord.gg/peerportal)

---

**最后更新：** 2024-12-19
**版本：** v2.0 