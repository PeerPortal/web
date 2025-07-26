# Docker 运行文档

## 快速开始

### 1. 环境准备
确保已安装 Docker 和 Docker Compose：
```bash
docker --version
docker-compose --version
```

### 2. 配置环境变量
项目已包含 `.env` 文件，包含必要的 Supabase 配置。

### 3. 启动应用
```bash
# 构建并启动
docker-compose up --build -d

# 或者直接启动（如果已构建过）
docker-compose up -d
```

### 4. 访问应用
- **应用首页**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建
docker-compose up --build
```

## 项目结构
- 使用 **Supabase 云数据库**，无需本地数据库
- 应用运行在 **8000 端口**
- 支持自动重启

## 故障排除

### 端口被占用
```bash
# 检查端口占用
lsof -i :8000

# 或修改端口（在 docker-compose.yml 中）
ports:
  - "8001:8000"
```

### 重新构建
```bash
# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

就这么简单！🚀