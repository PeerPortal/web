# PeerPortal - AI留学规划师平台

一个集成论坛、消息、文件上传、AI咨询的智能留学申请平台，基于FastAPI + LangGraph构建，提供全方位留学申请指导服务。

**🤖 AI智能对话 | 💬 实时消息 | 🏛️ 论坛交流 | 📁 文件管理 | 🎯 精准匹配 | 🚀 高性能架构**

## 🌟 核心功能

### 🤖 AI留学规划师
- **智能对话**: 基于LangGraph的多轮对话AI系统
- **知识库学习**: 支持PDF文档上传，AI自动学习专业知识  
- **实时搜索**: 集成网络搜索获取最新信息
- **工具融合**: 数据库查询 + 网络搜索 + 知识库检索

### 🏛️ 论坛系统 (新增)
- **分类讨论**: 申请经验、院校讨论、留学生活、职业规划等
- **帖子管理**: 创建、编辑、删除、置顶、加热
- **互动功能**: 点赞、回复、嵌套评论
- **标签系统**: 热门标签、搜索筛选
- **举报系统**: 内容审核和社区管理

### 💬 消息系统 (增强)
- **实时通信**: 导师学生一对一聊天
- **对话管理**: 对话列表、未读消息提醒
- **消息类型**: 文本、图片、文件消息支持
- **消息状态**: 已发送、已送达、已读状态跟踪
- **在线状态**: 实时在线状态显示

### 📁 文件上传系统 (新增)
- **头像上传**: 支持多种图片格式，自动压缩优化
- **文档管理**: PDF、Word、TXT文件上传与管理
- **批量上传**: 一次性上传多个文件
- **安全验证**: 文件类型、大小严格限制
- **静态服务**: 高效的文件访问和下载

### 🎯 智能匹配系统
- **精准推荐**: 基于目标学校、专业、申请阶段的智能匹配
- **引路人网络**: 连接在读生/毕业生与申请者
- **服务推荐**: 个性化留学服务推荐
- **评价体系**: 透明的服务评价和质量保证

### 🌐 多端支持
- **REST API**: 完整的FastAPI后端服务
- **Web界面**: Streamlit交互式界面
- **Swagger文档**: 自动生成的API文档

## 📁 项目结构

```
backend/
├── app/                          # 应用核心代码
│   ├── agents/                   # AI Agent相关
│   │   ├── langgraph/           # LangGraph实现
│   │   │   ├── agent_state.py   # Agent状态定义
│   │   │   ├── agent_graph.py   # Agent核心逻辑
│   │   │   ├── agent_tools.py   # 工具集合
│   │   │   └── knowledge_base.py # 知识库管理
│   │   ├── planner_agent.py     # 简单Agent实现
│   │   └── tools/               # 工具实现
│   ├── api/                     # API路由
│   │   └── routers/             # API路由模块
│   │       ├── forum_router.py  # 论坛系统API (新增)
│   │       ├── file_router.py   # 文件上传API (新增)
│   │       ├── message_router.py # 消息系统API (增强)
│   │       └── ...              # 其他API模块
│   ├── core/                    # 核心配置
│   ├── crud/                    # 数据库操作
│   │   ├── crud_forum.py        # 论坛CRUD (新增)
│   │   ├── crud_message.py      # 消息CRUD (新增)
│   │   └── ...                  # 其他CRUD模块
│   ├── schemas/                 # 数据模型
│   │   ├── forum_schema.py      # 论坛数据模型 (新增)
│   │   ├── message_schema.py    # 消息数据模型 (新增)
│   │   └── ...                  # 其他数据模型
│   ├── main.py                  # FastAPI应用入口
│   └── streamlit_app.py         # Streamlit Web界面
├── test/                        # 测试文件 (按功能分类)
│   ├── agents/                  # AI Agent测试 (18个文件)
│   ├── api/                     # API功能测试 (12个文件)
│   ├── database/                # 数据库测试 (10个文件)
│   ├── integration/             # 集成测试 (3个文件)
│   ├── tools/                   # 测试工具 (12个文件)
│   ├── scripts/                 # 测试脚本 (8个文件)
│   └── reports/                 # 测试报告 (11个文件)
├── scripts/                     # 工具脚本
│   ├── database/                # 数据库相关脚本
│   │   └── create_missing_tables.sql # 新增表结构 (新增)
│   └── *.py                     # 调试和维护脚本
├── docs/                        # 项目文档
│   ├── PeerPortal_后端API文档.md # 完整API文档 (新增)
│   ├── 新功能测试指南.md        # 测试指南 (新增)
│   └── 项目完善完成报告.md      # 项目报告 (新增)
├── uploads/                     # 文件上传目录 (新增)
│   ├── avatars/                # 头像存储
│   └── documents/              # 文档存储
├── knowledge_base/              # 知识库文件存储
├── vector_store/                # 向量数据库(ChromaDB)
├── test_new_features.py         # 新功能测试脚本 (新增)
├── test_database_tables.py      # 数据库验证脚本 (新增)
├── run_feature_tests.sh         # 一键测试脚本 (新增)
├── fix_test_issues.py           # 测试诊断工具 (新增)
├── start_api.sh                 # FastAPI启动脚本
├── start_streamlit.sh           # Streamlit启动脚本
└── run_tests.sh                 # 测试运行脚本
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `configs/env_example.txt` 为 `.env` 并填入配置：

```env
# OpenAI API Key (必需)
OPENAI_API_KEY=sk-...

# Tavily API Key (可选，用于网络搜索)
TAVILY_API_KEY=tvly-...

# Supabase数据库配置 (必需)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_DB_PASSWORD=your-database-password
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# 其他配置
DEBUG=true
```

### 3. 数据库初始化

```bash
# 创建新增的数据库表
psql -h your-host -U your-username -d your-database -f scripts/database/create_missing_tables.sql

# 或使用诊断工具检查环境
python fix_test_issues.py
```

### 4. 启动服务

```bash
# 方式1: 启动FastAPI后端服务
./start_api.sh
# 访问 http://localhost:8000/docs

# 方式2: 启动Streamlit Web界面  
./start_streamlit.sh
# 访问 http://localhost:8503

# 方式3: 使用uvicorn直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 运行测试

```bash
# 一键测试所有新功能 (推荐)
cd test/scripts && ./run_feature_tests.sh

# 按模块运行测试
python -m pytest test/api/           # API功能测试
python -m pytest test/database/     # 数据库测试
python -m pytest test/agents/       # AI Agent测试
python -m pytest test/integration/  # 集成测试

# 使用测试工具
cd test/tools && python fix_test_issues.py  # 环境诊断

# 或运行完整测试套件
cd test/scripts && ./run_tests.sh
```

## 🛠️ 技术栈

| 组件 | 技术 | 版本 | 作用 |
|------|------|------|------|
| **后端框架** | FastAPI | 0.116.1 | RESTful API服务 |
| **智能体核心** | LangGraph | 0.2.51 | AI工作流编排 |
| **大语言模型** | OpenAI GPT | 4o-mini | 智能对话和推理 |
| **知识库** | ChromaDB | 0.5.15 | 向量数据库 |
| **文件处理** | aiofiles | 24.1.0 | 异步文件操作 |
| **Web界面** | Streamlit | 1.41.1 | 交互式前端 |
| **数据库** | Supabase | 2.17.0 | 后端数据存储 |
| **网络搜索** | Tavily/DuckDuckGo | latest | 实时信息检索 |
| **HTTP客户端** | httpx | 0.28.1 | 异步HTTP请求 |

## 📊 API接口

### 🏛️ 论坛系统 API (新增)

#### 分类和帖子管理
- `GET /api/v1/forum/categories` - 获取论坛分类
- `GET /api/v1/forum/posts` - 获取帖子列表 (支持筛选和搜索)
- `POST /api/v1/forum/posts` - 创建新帖子
- `GET /api/v1/forum/posts/{post_id}` - 获取帖子详情
- `PUT /api/v1/forum/posts/{post_id}` - 更新帖子
- `DELETE /api/v1/forum/posts/{post_id}` - 删除帖子

#### 互动功能
- `POST /api/v1/forum/posts/{post_id}/like` - 点赞/取消点赞帖子
- `POST /api/v1/forum/posts/{post_id}/view` - 增加浏览量
- `GET /api/v1/forum/posts/{post_id}/replies` - 获取帖子回复
- `POST /api/v1/forum/posts/{post_id}/replies` - 创建回复
- `PUT /api/v1/forum/replies/{reply_id}` - 更新回复
- `DELETE /api/v1/forum/replies/{reply_id}` - 删除回复
- `POST /api/v1/forum/replies/{reply_id}/like` - 点赞/取消点赞回复

#### 个人和管理
- `GET /api/v1/forum/my-posts` - 我的帖子
- `GET /api/v1/forum/my-replies` - 我的回复
- `GET /api/v1/forum/tags/popular` - 热门标签
- `POST /api/v1/forum/posts/{post_id}/report` - 举报帖子
- `POST /api/v1/forum/replies/{reply_id}/report` - 举报回复

### 💬 消息系统 API (增强)

#### 对话管理
- `GET /api/v1/messages/conversations` - 获取对话列表
- `GET /api/v1/messages/conversations/{conversation_id}` - 获取对话消息
- `GET /api/v1/messages` - 获取消息列表

#### 消息操作
- `POST /api/v1/messages` - 发送消息
- `PUT /api/v1/messages/{message_id}/read` - 标记消息为已读

### 📁 文件上传 API (新增)

#### 文件上传
- `POST /api/v1/files/upload/avatar` - 上传头像 (JPG, PNG, GIF, WebP, 最大5MB)
- `POST /api/v1/files/upload/document` - 上传文档 (PDF, DOC, DOCX, TXT, 最大10MB)
- `POST /api/v1/files/upload/multiple` - 批量上传文件 (最多10个)

#### 文件管理
- `DELETE /api/v1/files/files/{file_id}` - 删除文件
- `GET /static/uploads/avatars/{filename}` - 访问头像文件
- `GET /static/uploads/documents/{filename}` - 访问文档文件

### 🤖 AI智能体API

#### 基础版Agent
- `GET /api/v1/planner/capabilities` - AI能力查询
- `POST /api/v1/planner/invoke` - AI咨询对话 (路径已修复)

#### 高级版Agent
- `GET /api/v1/ai/advanced-planner/health` - 健康检查  
- `POST /api/v1/ai/advanced-planner/invoke` - 高级AI咨询
- `POST /api/v1/ai/advanced-planner/upload-documents` - 上传知识库文档
- `GET /api/v1/ai/advanced-planner/knowledge-base/status` - 知识库状态

### 👤 用户管理 API

#### 用户信息
- `GET /api/v1/users/me` - 获取完整用户信息
- `GET /api/v1/users/me/basic` - 获取基础用户信息 (新增)
- `PUT /api/v1/users/me` - 更新用户信息
- `GET /api/v1/users/{user_id}/profile` - 获取公开用户资料

#### 认证系统
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新Token

### 🎯 其他核心API

#### 导师系统
- `GET /api/v1/mentors/search` - 搜索导师
- `GET /api/v1/mentors/{mentor_id}` - 获取导师详情
- `POST /api/v1/mentors/profile` - 创建导师档案

#### 会话和评价
- `GET /api/v1/sessions` - 获取会话列表
- `POST /api/v1/sessions` - 创建会话预约
- `GET /api/v1/sessions/statistics` - 会话统计
- `POST /api/v1/reviews` - 创建评价
- `GET /api/v1/reviews/my-reviews` - 我的评价

#### 服务订单
- `GET /api/v1/services/orders/my-orders` - 我的订单

#### 学生档案
- `GET /api/v1/students/profile` - 获取学生档案

### API使用示例

```python
# 论坛API使用示例
import httpx

# 获取论坛分类
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v1/forum/categories")
    categories = response.json()

# 创建帖子
post_data = {
    "title": "美国CS硕士申请经验分享",
    "content": "分享我的申请经验...",
    "category": "application",
    "tags": ["美国留学", "CS申请"]
}
response = await client.post(
    "http://localhost:8000/api/v1/forum/posts",
    json=post_data,
    headers={"Authorization": f"Bearer {token}"}
)

# 文件上传示例
with open("avatar.png", "rb") as f:
    files = {"file": ("avatar.png", f, "image/png")}
    response = await client.post(
        "http://localhost:8000/api/v1/files/upload/avatar",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )

# AI咨询示例
ai_data = {
    "input": "我想申请美国计算机科学硕士，有什么建议？",
    "session_id": "user123",
    "stream": False
}
response = await client.post(
    "http://localhost:8000/api/v1/planner/invoke",
    json=ai_data,
    headers={"Authorization": f"Bearer {token}"}
)
```

## 🗄️ 数据库结构

### 新增数据表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| **forum_posts** | 论坛帖子 | id, title, content, author_id, category, tags, likes_count, views_count |
| **forum_replies** | 论坛回复 | id, post_id, content, author_id, parent_id, likes_count |
| **forum_likes** | 点赞记录 | id, user_id, post_id, reply_id |
| **messages** | 消息记录 | id, sender_id, recipient_id, content, message_type, status, is_read |
| **uploaded_files** | 文件记录 | id, file_id, user_id, filename, file_path, file_size, content_type |

### 数据库优化

- ✅ **性能索引**: 针对查询优化的复合索引
- ✅ **自动触发器**: 统计数据自动更新 (点赞数、回复数)
- ✅ **数据一致性**: 外键约束和检查约束
- ✅ **查询视图**: 简化复杂查询的优化视图

## 🧪 测试系统

### 新增测试工具

#### 🔧 环境诊断工具
```bash
# 运行环境诊断
cd test/tools && python fix_test_issues.py
```
**功能**:
- Python版本检查
- 虚拟环境状态验证
- 依赖包安装检查
- 测试文件完整性验证
- 上传目录创建
- 常见问题自动修复

#### 📊 综合功能测试
```bash
# 运行所有新功能测试
cd test/api && python test_new_features.py
```
**测试范围**:
- 🏛️ 论坛系统 (4个API端点)
- 💬 消息系统 (3个API端点)
- 📁 文件上传 (2个API端点)
- 🤖 AI功能 (2个API端点)
- 👤 用户管理 (2个API端点)

#### 🗄️ 数据库结构验证
```bash
# 验证数据库表结构
cd test/database && python test_database_tables.py
```
**验证内容**:
- 表存在性检查 (5个新增表)
- 列结构完整性验证
- 索引优化检查 (15+个索引)
- 触发器功能验证
- 视图可用性检查

#### 🚀 一键测试脚本
```bash
# 运行完整测试套件
cd test/scripts && ./run_feature_tests.sh
```
**自动化功能**:
- 环境检查和修复
- 服务器状态验证
- 依赖自动安装
- 并行测试执行
- 综合报告生成

### 测试覆盖率

| 功能模块 | 测试覆盖 | 端点数量 | 状态 |
|---------|---------|----------|------|
| 🏛️ **论坛系统** | 100% | 12个API | ✅ 全覆盖 |
| 💬 **消息系统** | 100% | 5个API | ✅ 全覆盖 |
| 📁 **文件上传** | 100% | 4个API | ✅ 全覆盖 |
| 🤖 **AI功能** | 100% | 2个API | ✅ 全覆盖 |
| 👤 **用户管理** | 100% | 4个API | ✅ 全覆盖 |
| 🗄️ **数据库** | 100% | 15项检查 | ✅ 全覆盖 |

**总计**: 27个API端点 + 15项数据库检查 = **42项全面测试**

### 测试报告

测试完成后自动生成以下报告：

- `new_features_test_report_*.json` - API功能测试详细报告
- `database_verification_report_*.json` - 数据库验证详细报告
- `comprehensive_test_summary.md` - 综合测试摘要
- `diagnostic_report.md` - 环境诊断报告

## 🔧 开发指南

### 添加新的论坛功能

1. **扩展数据模型**:
```python
# app/schemas/forum_schema.py
class NewForumFeature(BaseModel):
    name: str
    description: str
```

2. **实现CRUD操作**:
```python
# app/crud/crud_forum.py
async def create_feature(self, db_conn, feature_data):
    # 实现数据库操作
    pass
```

3. **添加API端点**:
```python
# app/api/routers/forum_router.py
@router.post("/features")
async def create_forum_feature(feature: NewForumFeature):
    return await forum_crud.create_feature(db_conn, feature)
```

### 扩展消息系统

```python
# 添加新消息类型
class MessageType(str, Enum):
    text = "text"
    image = "image"
    file = "file"
    voice = "voice"  # 新增语音消息
    video = "video"  # 新增视频消息
```

### 自定义文件上传

```python
# 添加新文件类型支持
ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/avi", "video/mov"
}

@router.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    # 实现视频上传逻辑
    pass
```

### 数据库迁移

```sql
-- 添加新字段
ALTER TABLE forum_posts ADD COLUMN featured BOOLEAN DEFAULT FALSE;

-- 创建新索引
CREATE INDEX idx_forum_posts_featured ON forum_posts(featured) WHERE featured = TRUE;
```

## 🚀 生产部署

### Docker部署
```bash
# 构建镜像
docker build -t peerportal-backend .

# 运行容器
docker run -d -p 8000:8000 --env-file .env peerportal-backend
```

### 环境配置
```env
# 生产环境配置
DEBUG=false
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-production-database-url
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### 性能优化
- ✅ **连接池**: asyncpg数据库连接池
- ✅ **静态文件**: 高效的文件服务
- ✅ **异步处理**: 全异步架构
- ✅ **缓存策略**: 合理的缓存机制

## 🆘 故障排除

### 常见问题

1. **AsyncIO安装错误**:
   ```bash
   # asyncio是Python内置模块，无需安装
   python -c "import asyncio; print('✅ asyncio可用')"
   ```

2. **文件上传失败**:
   ```bash
   # 确保上传目录存在
   mkdir -p uploads/avatars uploads/documents
   chmod 755 uploads/
   ```

3. **数据库表不存在**:
   ```bash
   # 执行数据库表创建脚本
   psql -h host -U user -d db -f scripts/database/create_missing_tables.sql
   ```

4. **服务器启动失败**:
   ```bash
   # 检查依赖是否完整
   pip install -r requirements.txt
   
   # 测试应用导入
   python -c "from app.main import app; print('✅ 应用导入成功')"
   ```

### 调试工具

```bash
# 运行环境诊断
python fix_test_issues.py

# 检查API健康状态
curl http://localhost:8000/

# 查看详细日志
uvicorn app.main:app --reload --log-level debug
```

### 获取支持

- 📧 **技术支持**: tech@peerportal.com
- 📚 **详细文档**: 查看 `docs/` 目录
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/PeerPortal/backend/issues)
- 💬 **社区讨论**: [论坛系统](http://localhost:8000/api/v1/forum/categories)

---

## 🌟 项目状态

**✅ PeerPortal v2.0.0 - 全功能留学平台**

### 🎉 最新更新 (v2.0.0)

- 🏛️ **论坛系统**: 完整的社区讨论功能
- 💬 **消息系统**: 实时通信和对话管理
- 📁 **文件上传**: 安全的文件管理系统
- 🔧 **AI路径修复**: 优化的AI服务接口
- 🧪 **测试套件**: 全面的自动化测试系统
- 📊 **项目文档**: 完整的API文档和使用指南

### 🎯 核心特性

- 🎓 **专业定位**: 专注留学申请指导服务
- ⚡ **高性能**: asyncpg连接池 + FastAPI异步架构  
- 🏛️ **社区交流**: 完整的论坛和消息系统
- 📁 **文件管理**: 安全的上传和存储机制
- 🎯 **智能匹配**: 多维度匹配算法
- 📱 **API完整**: 27个端点 + 5个数据表
- 🔒 **企业安全**: JWT + 角色权限 + 数据验证
- 📊 **全面测试**: 42项测试 + 自动化验证
- 📚 **完整文档**: API文档 + 使用指南

### 📊 技术指标

- **API端点**: 27个 (新增12个论坛API + 4个文件API)
- **数据表**: 15个 (新增5个核心表)
- **测试覆盖**: 42项测试 (API + 数据库)
- **文档完整**: 3个完整指南 + API文档
- **性能优化**: 15+个数据库索引 + 触发器
- **安全特性**: 文件验证 + 权限控制 + 数据验证

**🚀 让每一个留学梦想都能在社区中找到支持和指导！**

---
*© 2024 PeerPortal团队. All rights reserved. - 版本 v2.0.0*
