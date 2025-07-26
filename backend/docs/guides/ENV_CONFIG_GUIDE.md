# 🔧 环境变量配置指南

## 快速开始

1. **复制配置文件**：
   ```bash
   # 项目已为您创建了基础的 .env 文件
   # 您只需要修改其中的 Supabase 配置即可
   ```

2. **获取 Supabase 配置**：
   - 登录 [Supabase](https://supabase.com)
   - 进入您的项目
   - 在 Settings → API 中找到配置信息

## 📋 必需配置项

### 🔑 Supabase 配置

```bash
# 在 Supabase 项目的 Settings → API 页面找到：

# 项目 URL
SUPABASE_URL=https://your-project-id.supabase.co

# Anon Key（匿名密钥）
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 🌍 获取 Supabase 配置的详细步骤

1. **登录 Supabase**：
   - 访问 https://supabase.com
   - 登录您的账户

2. **选择项目**：
   - 如果没有项目，点击 "New Project" 创建
   - 选择您的项目

3. **获取配置信息**：
   ```
   左侧菜单 → Settings → API
   ```
   
4. **复制以下信息**：
   - **Project URL** → 对应 `SUPABASE_URL`
   - **anon public** → 对应 `SUPABASE_KEY`

## 📝 完整配置模板

创建 `.env` 文件并填入以下内容：

```bash
# ===========================================
# 🚀 应用配置
# ===========================================
DEBUG=true
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=8001

# ===========================================
# 🗃️ Supabase 数据库配置
# ===========================================
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# ===========================================
# 🔐 安全配置
# ===========================================
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ===========================================
# 🌐 CORS 配置
# ===========================================
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# ===========================================
# ⚡ 性能配置
# ===========================================
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=10
```

## 🔍 配置验证

配置完成后，运行以下命令验证：

```bash
# 1. 测试配置加载
python -c "from app.core.config import settings; print('✅ 配置加载成功:', settings.APP_NAME)"

# 2. 检查数据库连接
python test/check_database.py

# 3. 启动应用
python start_new_app.py
```

## 🚨 常见问题解决

### 问题 1: ValidationError: SUPABASE_URL field required
**解决方案**：
```bash
# 确保 .env 文件中有以下配置
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
```

### 问题 2: Extra inputs are not permitted
**解决方案**：
```bash
# 检查 .env 文件中是否有拼写错误的字段名
# 移除或注释掉不需要的字段
```

### 问题 3: 数据库连接失败
**解决方案**：
```bash
# 1. 确认 Supabase 项目正常运行
# 2. 检查网络连接
# 3. 验证 API Key 是否正确
```

## 🔐 安全提醒

1. **SECRET_KEY**：
   - 开发环境可以使用默认值
   - 生产环境必须使用强密码

2. **API Keys**：
   - 永远不要提交到 Git
   - 定期轮换密钥

3. **CORS 配置**：
   - 生产环境只允许实际的前端域名

## 🎯 不同环境配置

### 开发环境 (.env.development)
```bash
DEBUG=true
PORT=8001
SUPABASE_URL=https://your-dev-project.supabase.co
```

### 生产环境 (.env.production)
```bash
DEBUG=false
PORT=8000
SECRET_KEY=super-strong-production-secret
SUPABASE_URL=https://your-prod-project.supabase.co
```

## 📞 获取帮助

如果配置过程中遇到问题：

1. **检查 Supabase 状态**：
   ```bash
   python test/check_database.py
   ```

2. **查看应用日志**：
   ```bash
   python start_new_app.py
   # 查看启动时的日志信息
   ```

3. **验证环境变量**：
   ```bash
   python -c "import os; print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))"
   ```

---

✅ **配置完成后，您就可以正常使用新架构的所有功能了！** 