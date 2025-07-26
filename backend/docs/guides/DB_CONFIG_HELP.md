# 🔧 数据库配置解决方案

## ❌ 当前问题
```
❌ 启动失败: invalid literal for int() with base 10: 'port'
```

这个错误是因为 `.env` 文件中有无效的数据库连接字符串模板。

## ✅ 解决方案

### 方案 1: 注释掉无效的 DATABASE_URL （推荐）

我已经为您修复了这个问题。现在您有两个选择：

#### 选择 A: 使用 Supabase REST API（简单）
```bash
# 您的 .env 文件现在已经正确配置
# 应用将使用 Supabase 客户端而不是直接数据库连接
# 这对大多数功能来说是足够的
```

#### 选择 B: 配置直接数据库连接（高级）
如果您需要数据库连接池功能，请添加 Supabase 数据库密码：

```bash
# 1. 登录 Supabase Dashboard
# 2. 进入您的项目
# 3. Settings → Database
# 4. 复制 "Database password"
# 5. 在 .env 文件中添加：
SUPABASE_DB_PASSWORD=您的实际数据库密码
```

## 🚀 立即启动应用

现在您可以启动应用了：

```bash
# 方式1: 使用简化启动脚本
python -m app.main

# 方式2: 使用完整启动脚本
python start_new_app.py

# 方式3: 直接运行 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📊 配置状态检查

```bash
# 检查配置是否正确
python -c "from app.core.config import settings; print('✅ 配置正常:', settings.SUPABASE_URL[:30])"

# 检查数据库状态（使用 Supabase 客户端）
python test/check_database.py
```

## 🎯 推荐配置

对于开发环境，推荐使用方案 A（Supabase REST API）：

**优点：**
- ✅ 配置简单
- ✅ 无需数据库密码
- ✅ 自动处理连接
- ✅ 适合大多数开发需求

**缺点：**
- ⚠️ 无法使用连接池
- ⚠️ 某些高级查询功能受限

## 🔮 后续升级

当您需要生产级性能时，可以随时切换到直接数据库连接：

1. 获取 Supabase 数据库密码
2. 在 `.env` 中添加 `SUPABASE_DB_PASSWORD`
3. 重启应用即可自动使用连接池

---

✨ **现在应该可以正常启动应用了！** 