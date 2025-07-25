# 启航引路人 - 留学双边信息平台

一个专业的留学申请指导平台，连接留学申请者（学弟学妹）与目标学校的在读生或毕业生（学长学姐），提供个性化的留学申请指导服务。

**🎓 专业留学指导平台 | ⚡ 高性能后端架构 | 🎯 智能匹配算法**

## 🌟 平台特色

**为学弟学妹提供:**
- 🔍 **精准匹配**: 基于目标学校、专业、申请阶段的智能推荐
- 📝 **专业指导**: 文书修改、推荐信建议、面试辅导等服务
- 💬 **实时沟通**: 与学长学姐直接交流经验分享
- ⭐ **评价体系**: 透明的服务评价和质量保证

**为学长学姐提供:**
- 💰 **收入机会**: 通过分享经验获得合理回报
- 📈 **信誉积累**: 建立专业指导者形象
- 🎯 **灵活安排**: 自主设置服务时间和价格
- 🏆 **价值实现**: 帮助学弟学妹实现留学梦想

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
复制 `env_example.txt` 并创建 `.env` 文件：
```bash
cp env_example.txt .env
```

编辑 `.env` 文件：
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
DEBUG=true
```

### 3. 数据库初始化
```bash
# 在 Supabase SQL Editor 中执行 db_schema.sql
# 运行数据库检查
python test/check_database_complete.py
```

### 4. 启动平台
```bash
# 方式1: 使用启动脚本（推荐）
./start_server.sh

# 方式2: 手动启动
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 服务运行在 http://localhost:8001
```

## 🏗️ 技术架构

### 核心技术栈
- **FastAPI 0.116.1**: 高性能Web框架，自动生成API文档
- **PostgreSQL + Supabase**: 关系型数据库，支持实时功能
- **asyncpg 0.30.0**: 高性能异步数据库驱动
- **Pydantic V2**: 严格的数据验证和序列化
- **JWT认证**: 无状态身份验证和授权

### 项目结构
```
app/                          # 留学平台核心应用
├── api/                      # API层
│   ├── deps.py              # 认证依赖和数据库连接
│   └── routers/             # 路由模块
│       ├── auth_router.py      # 用户认证API
│       ├── user_router.py      # 用户管理API
│       ├── mentor_router.py    # 学长学姐API
│       ├── student_router.py   # 学弟学妹API
│       ├── matching_router.py  # 智能匹配API
│       ├── service_router.py   # 指导服务API
│       ├── session_router.py   # 指导会话API
│       ├── review_router.py    # 评价反馈API
│       └── message_router.py   # 消息系统API
├── core/                    # 核心配置
│   ├── config.py           # 环境配置管理
│   └── db.py               # 数据库连接池
├── crud/                   # 数据库操作层
│   ├── crud_user.py        # 用户数据操作
│   ├── crud_mentor.py      # 指导者数据操作
│   ├── crud_student.py     # 申请者数据操作
│   ├── crud_service.py     # 服务数据操作
│   ├── crud_matching.py    # 匹配算法数据操作
│   ├── crud_session.py     # 会话数据操作
│   └── crud_review.py      # 评价数据操作
├── schemas/                # Pydantic数据模型
│   ├── user_schema.py      # 用户模型
│   ├── mentor_schema.py    # 指导者模型
│   ├── student_schema.py   # 申请者模型
│   ├── service_schema.py   # 服务模型
│   ├── matching_schema.py  # 匹配模型
│   ├── session_schema.py   # 会话模型
│   ├── review_schema.py    # 评价模型
│   └── token_schema.py     # JWT认证模型
└── main.py                 # FastAPI应用主入口
```

## 📊 数据库架构

### 21表完整数据模型
```
📊 留学平台数据架构 (21表)
├── 👥 用户身份系统 (4表)
│   ├── users              # 用户基础信息
│   ├── profiles           # 详细个人资料
│   ├── friends            # 用户关系网络
│   └── messages           # 实时消息系统
│
├── 🎓 留学指导系统 (5表)
│   ├── mentor_matches            # 学长学姐匹配记录
│   ├── mentorship_relationships  # 指导关系管理
│   ├── mentorship_reviews        # 指导服务评价
│   ├── mentorship_sessions       # 指导会话记录
│   └── mentorship_transactions   # 指导服务交易
│
├── 🛍️ 服务交易系统 (3表)
│   ├── services           # 指导服务发布
│   ├── orders             # 服务订单管理
│   └── reviews            # 服务评价系统
│
├── 🛠️ 专业技能系统 (3表)
│   ├── skill_categories   # 申请方向分类
│   ├── skills             # 具体专业技能
│   └── user_skills        # 用户专业能力映射
│
└── 💎 用户扩展系统 (6表)
    ├── user_availability        # 指导时间安排
    ├── user_credit_logs         # 平台积分记录
    ├── user_learning_needs      # 申请者学习需求
    ├── user_reputation_stats    # 指导者信誉统计
    ├── user_unavailable_periods # 不可用时间管理
    └── user_wallets             # 用户钱包系统
```

## 🔗 API 端点总览

### 认证系统 `/api/v1/auth`
- `POST /register` - 用户注册（支持学生邮箱验证）
- `POST /login` - 用户登录
- `POST /refresh` - 刷新访问令牌

### 用户管理 `/api/v1/users`
- `GET /me` - 获取当前用户信息
- `PUT /me` - 更新用户资料
- `GET /{user_id}` - 获取用户基本信息

### 学长学姐端 `/api/v1/mentors`
- `POST /profile` - 创建指导者资料
- `GET /profile` - 获取自己的指导者资料
- `PUT /profile` - 更新指导者资料
- `GET /{mentor_id}` - 查看指导者详情
- `GET /` - 搜索指导者
- `PUT /availability` - 设置可用时间

### 学弟学妹端 `/api/v1/students`
- `POST /profile` - 创建申请者资料
- `PUT /learning-needs` - 设置学习需求
- `GET /matches` - 获取推荐指导者
- `GET /orders` - 查看服务订单
- `POST /reviews` - 提交服务评价

### 智能匹配 `/api/v1/matching`
- `POST /recommend` - 获取推荐指导者
- `GET /filters` - 获取筛选条件
- `POST /filter` - 高级筛选
- `GET /history` - 查看匹配历史

### 指导服务 `/api/v1/services`
- `GET /` - 浏览所有服务
- `POST /` - 发布新服务
- `GET /{service_id}` - 查看服务详情
- `POST /{service_id}/purchase` - 购买服务

### 指导会话 `/api/v1/sessions`
- `POST /` - 创建指导会话
- `GET /{session_id}` - 查看会话详情
- `POST /{session_id}/start` - 开始会话
- `POST /{session_id}/feedback` - 提交反馈

### 评价反馈 `/api/v1/reviews`
- `POST /service` - 服务评价
- `POST /mentor` - 指导者评价
- `GET /service/{service_id}` - 查看服务评价
- `GET /mentor/{mentor_id}` - 查看指导者评价

## 🧪 测试系统

### 运行完整测试
```bash
# 运行所有测试
python test/run_all_tests.py

# 测试数据库连接
python test/check_database_complete.py

# 测试API功能
python test/test_all_api.py
```

## 📱 API 使用示例

### 1. 学弟学妹注册并寻找指导者
```bash
# 注册申请者账户
curl -X POST "http://localhost:8001/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "student2024",
       "email": "student@university.edu",
       "password": "securepass",
       "role": "student"
     }'

# 登录获取token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=student2024&password=securepass"

# 创建申请者资料
curl -X POST "http://localhost:8001/api/v1/students/profile" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "current_education": "本科大四",
       "target_degree": "master",
       "target_universities": ["Stanford University", "MIT"],
       "target_majors": ["Computer Science", "AI"],
       "application_timeline": "2024秋季申请"
     }'

# 获取推荐指导者
curl -X POST "http://localhost:8001/api/v1/matching/recommend" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "target_universities": ["Stanford University"],
       "target_majors": ["Computer Science"],
       "degree_level": "master"
     }'
```

### 2. 学长学姐注册并提供服务
```bash
# 注册指导者账户
curl -X POST "http://localhost:8001/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "mentor2024",
       "email": "mentor@stanford.edu",
       "password": "securepass",
       "role": "mentor"
     }'

# 创建指导者资料
curl -X POST "http://localhost:8001/api/v1/mentors/profile" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "university": "Stanford University",
       "major": "Computer Science",
       "degree_level": "master",
       "graduation_year": 2023,
       "current_status": "graduated",
       "specialties": ["文书指导", "面试辅导"],
       "bio": "斯坦福CS硕士，擅长文书修改和面试指导"
     }'

# 发布指导服务
curl -X POST "http://localhost:8001/api/v1/services" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Stanford CS申请文书指导",
       "description": "一对一文书修改，包括Personal Statement等",
       "category": "essay",
       "price": 200.00,
       "duration": 120,
       "delivery_days": 3
     }'
```

## 🔧 开发指南

### 添加新功能模块
1. **定义数据模型**: 在 `app/schemas/` 中创建 Pydantic 模型
2. **实现数据操作**: 在 `app/crud/` 中添加数据库操作函数
3. **创建API路由**: 在 `app/api/routers/` 中定义API端点
4. **注册路由**: 在 `app/main.py` 中注册新路由
5. **添加测试**: 创建相应的测试用例

### 角色权限控制
```python
from app.api.deps import require_mentor_role, require_student_role

@router.post("/mentor-only-endpoint")
async def mentor_function(current_user = Depends(require_mentor_role())):
    # 仅限学长学姐访问的功能
    pass

@router.post("/student-only-endpoint") 
async def student_function(current_user = Depends(require_student_role())):
    # 仅限学弟学妹访问的功能
    pass
```

## 📖 文档资源

- **API交互文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc
- **健康检查**: http://localhost:8001/health
- **技术架构**: [`后端.md`](后端.md)
- **前端对接**: [`前端.md`](前端.md)

## 🔒 安全特性

- ✅ **JWT认证**: 无状态token认证
- ✅ **角色授权**: 基于角色的访问控制
- ✅ **数据验证**: Pydantic严格验证
- ✅ **CORS配置**: 跨域安全策略
- ✅ **错误处理**: 全局异常处理
- ✅ **SQL注入防护**: 参数化查询

## 🚀 生产部署

### Docker部署
```bash
# 构建镜像
docker build -t study-abroad-platform .

# 运行容器
docker run -d -p 8001:8001 --env-file .env study-abroad-platform
```

### 环境配置
```env
# 生产环境配置
DEBUG=false
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-production-database-url
CORS_ORIGINS=https://yourdomain.com
```

## 🆘 故障排除

**常见问题解决:**

1. **模块导入错误**: 确保虚拟环境已激活并安装所有依赖
2. **数据库连接失败**: 检查 `.env` 文件配置和网络连接
3. **认证错误**: 验证JWT密钥配置
4. **端口冲突**: 更改启动端口或终止占用进程

**获取支持:**
- 查看详细日志输出
- 运行健康检查: `curl http://localhost:8001/health`
- 运行测试套件: `python test/run_all_tests.py`

---

## 🌟 项目状态

**✅ 留学双边信息平台 v3.0.0 - 生产就绪**

- 🎓 **专业定位**: 专注留学申请指导服务
- ⚡ **高性能**: asyncpg连接池 + FastAPI异步架构
- 🎯 **智能匹配**: 多维度匹配算法
- 📱 **API完整**: 21表数据模型 + 8大API模块
- 🔒 **企业安全**: JWT + 角色权限 + 数据验证
- 📊 **可扩展**: 模块化架构支持快速迭代

**🚀 让每一个留学梦想都能找到最合适的指导者！**
