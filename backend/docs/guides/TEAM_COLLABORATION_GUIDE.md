# 🤝 Supabase 团队协作指南

## 📋 快速开始检查清单

### ✅ 方法1：项目邀请（最简单）

#### 队友需要做的：
- [ ] 登录 Supabase Dashboard
- [ ] 选择项目 → Settings → Team
- [ ] 点击 "Invite a teammate"
- [ ] 输入您的邮箱：`您的邮箱地址`
- [ ] 选择权限：`Developer` 或 `Admin`
- [ ] 发送邀请

#### 您需要做的：
- [ ] 检查邮箱接受邀请
- [ ] 登录 Supabase Dashboard
- [ ] 找到共享的项目
- [ ] 复制项目配置信息
- [ ] 更新本地 `.env` 文件

### ✅ 方法2：配置信息共享

#### 队友提供配置信息：
```bash
# 在 Supabase Dashboard → Settings → API 获取
SUPABASE_URL=https://xxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...

# 可选：数据库密码（Settings → Database）
SUPABASE_DB_PASSWORD=数据库密码
```

#### 您的操作步骤：
```bash
# 1. 备份当前配置
cp .env .env.backup

# 2. 更新 .env 文件
SUPABASE_URL=队友提供的URL
SUPABASE_KEY=队友提供的Key

# 3. 测试连接
python test/check_database.py

# 4. 启动应用测试
python start_new_app.py
```

## 🔄 同步数据库结构

### 选项A：使用现有 schema
```bash
# 如果队友的数据库结构和我们的 db_schema.sql 一致
# 直接在队友的 Supabase 项目中执行我们的 schema

# 1. 复制 db_schema.sql 内容
cat db_schema.sql

# 2. 队友在 Supabase SQL Editor 中执行
# 或者您获得权限后自己执行
```

### 选项B：导出队友的结构
```sql
-- 在队友的 Supabase SQL Editor 中执行
-- 导出完整的数据库结构
SELECT 
    schemaname,
    tablename,
    tableowner,
    hasindexes,
    hasrules,
    hastriggers
FROM pg_tables 
WHERE schemaname = 'public';

-- 导出每个表的详细结构
\d+ table_name;
```

## 🧪 测试协作设置

### 1. 连接测试
```bash
# 测试基本连接
python -c "
from app.core.config import settings
print('项目URL:', settings.SUPABASE_URL)
print('API Key:', settings.SUPABASE_KEY[:20] + '...')
"

# 测试数据库连接
python test/check_database.py
```

### 2. 功能测试
```bash
# 启动应用
python start_new_app.py

# 在另一个终端测试 API
curl -s http://localhost:8001/health | python -m json.tool
```

### 3. 数据操作测试
```bash
# 注册测试用户
curl -X POST "http://localhost:8001/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username":"teamtest","email":"test@team.com","password":"teampass123"}'
```

## 🔐 权限级别说明

| 权限级别 | 数据库访问 | 设置修改 | 团队管理 | 适用场景 |
|----------|------------|----------|----------|----------|
| **Owner** | ✅ 完全 | ✅ 完全 | ✅ 完全 | 项目负责人 |
| **Admin** | ✅ 完全 | ✅ 大部分 | ✅ 邀请成员 | 技术负责人 |
| **Developer** | ✅ 读写 | ⚠️ 有限 | ❌ 无 | 开发人员 |
| **Read-only** | 👁️ 只读 | ❌ 无 | ❌ 无 | 观察者 |

## 🚨 注意事项

### 🔒 安全考虑
- **API Keys**: 永远不要在代码中硬编码
- **数据库密码**: 只在需要直连时使用
- **权限原则**: 给予最小必要权限

### 🔄 数据同步
- **生产数据**: 谨慎操作，建议先在开发环境测试
- **Schema 变更**: 团队协调，避免冲突
- **备份**: 重要操作前务必备份

### 📝 团队协作最佳实践
1. **统一环境**: 使用相同的 schema 版本
2. **配置管理**: 使用 `.env.example` 分享配置模板
3. **文档同步**: 及时更新 API 文档
4. **测试覆盖**: 确保所有成员都能运行测试

## 🆘 常见问题解决

### Q: 无法访问队友的项目
**A:** 检查以下几点：
- 是否接受了邀请邮件
- 邮箱地址是否正确
- 是否登录了正确的 Supabase 账户

### Q: 数据库连接失败
**A:** 验证配置：
```bash
# 检查配置格式
echo $SUPABASE_URL
echo $SUPABASE_KEY

# 测试网络连接
curl -I $SUPABASE_URL
```

### Q: 权限不足错误
**A:** 联系项目 Owner 检查权限级别

## 📞 获取帮助

### 快速验证命令
```bash
# 一键验证团队协作设置
python -c "
import os
from app.core.config import settings
print('✅ 配置验证')
print('URL:', settings.SUPABASE_URL)
print('Key:', '已配置' if settings.SUPABASE_KEY else '未配置')
print('项目ID:', settings.SUPABASE_URL.split('//')[1].split('.')[0] if settings.SUPABASE_URL else '无')
"
```

### 团队配置模板
```bash
# 团队成员配置文件模板
# .env.team (队友分享给您的配置)
SUPABASE_URL=https://项目ID.supabase.co
SUPABASE_KEY=anon_public_key
SUPABASE_DB_PASSWORD=数据库密码（可选）

# 其他配置保持不变
DEBUG=true
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=8001
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
DB_POOL_MIN_SIZE=1
DB_POOL_MAX_SIZE=10
```

---

✨ **通过以上任一方式，您都可以访问和同步队友的 Supabase 数据库！** 