# 启航引路人 - AI留学规划师

一个基于FastAPI + LangGraph的智能留学咨询平台，融合AI对话、知识库学习、数据匹配等功能，提供个性化留学申请指导。

**🤖 AI智能对话 | 📚 知识库学习 | 🎯 精准匹配 | 🚀 高性能架构**

## 🌟 核心功能

### 🤖 AI留学规划师
- **智能对话**: 基于LangGraph的多轮对话AI系统
- **知识库学习**: 支持PDF文档上传，AI自动学习专业知识  
- **实时搜索**: 集成网络搜索获取最新信息
- **工具融合**: 数据库查询 + 网络搜索 + 知识库检索

### 🎯 智能匹配系统
- **精准推荐**: 基于目标学校、专业、申请阶段的智能匹配
- **引路人网络**: 连接在读生/毕业生与申请者
- **服务推荐**: 个性化留学服务推荐
- **评价体系**: 透明的服务评价和质量保证

### 🌐 多端支持
- **REST API**: 完整的FastAPI后端服务
- **Web界面**: Streamlit交互式界面
- **文件上传**: 支持PDF知识库文档管理

## � 项目结构

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
│   ├── core/                    # 核心配置
│   ├── crud/                    # 数据库操作
│   ├── schemas/                 # 数据模型
│   ├── main.py                  # FastAPI应用入口
│   └── streamlit_app.py         # Streamlit Web界面
├── test/                        # 测试文件
│   ├── agents/                  # Agent测试
│   └── *.py                     # 其他功能测试
├── scripts/                     # 工具脚本
│   ├── database/                # 数据库相关脚本
│   └── *.py                     # 调试和维护脚本
├── docs/                        # 项目文档
├── knowledge_base/              # 知识库文件存储
├── vector_store/                # 向量数据库(ChromaDB)
├── start_api.sh                 # FastAPI启动脚本
├── start_streamlit.sh           # Streamlit启动脚本
└── run_tests.sh                 # 测试运行脚本
```
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
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

# 其他配置
DEBUG=true
```

### 3. 启动服务

```bash
# 方式1: 启动FastAPI后端服务
./start_api.sh
# 访问 http://localhost:8001/docs

# 方式2: 启动Streamlit Web界面  
./start_streamlit.sh
# 访问 http://localhost:8503

# 方式3: 同时启动两个服务
./start_api.sh &
./start_streamlit.sh
```

### 4. 运行测试

```bash
# 运行完整测试套件
./run_tests.sh

# 或单独运行测试
python test/agents/test_simple_agent.py
python test/check_database_complete.py
```

## 🛠️ 技术栈

| 组件 | 技术 | 版本 | 作用 |
|------|------|------|------|
| **后端框架** | FastAPI | 0.116.1 | RESTful API服务 |
| **智能体核心** | LangGraph | 0.2.51 | AI工作流编排 |
| **大语言模型** | OpenAI GPT | 4o-mini | 智能对话和推理 |
| **知识库** | ChromaDB | 0.6.2 | 向量数据库 |
| **文件处理** | unstructured | 0.17.5 | PDF/DOC解析 |
| **Web界面** | Streamlit | 1.41.1 | 交互式前端 |
| **数据库** | Supabase | 2.17.0 | 后端数据存储 |
| **网络搜索** | Tavily/DuckDuckGo | latest | 实时信息检索 |
## 📊 API接口

### AI智能体API

#### 基础版Agent
- `GET /api/v1/ai/planner/health` - 健康检查
- `POST /api/v1/ai/planner/invoke` - 基础AI咨询

#### 高级版Agent (推荐)
- `GET /api/v1/ai/advanced-planner/health` - 健康检查  
- `POST /api/v1/ai/advanced-planner/invoke` - 高级AI咨询
- `POST /api/v1/ai/advanced-planner/upload-documents` - 上传知识库文档
- `GET /api/v1/ai/advanced-planner/knowledge-base/status` - 知识库状态

### 平台核心API

#### 用户认证 (/auth)
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新Token

#### 学长学姐管理 (/mentors)  
- `GET /mentors` - 获取指导者列表
- `POST /mentors` - 创建指导者档案
- `GET /mentors/{id}` - 获取指导者详情

#### 智能匹配 (/matching)
- `POST /matching/recommend` - 获取智能推荐
- `POST /matching/create` - 创建匹配关系

#### 服务管理 (/services)
- `GET /services` - 获取服务列表  
- `POST /services` - 创建新服务

### API示例

```python
# AI咨询示例
import requests

response = requests.post(
    "http://localhost:8001/api/v1/ai/advanced-planner/invoke",
    json={
        "message": "我想申请美国计算机科学硕士，有什么建议？",
        "user_id": "user123"
    }
)
```
│
├── 🛍️ 服务交易系统 (3表)
│   ├── services           # 指导服务发布
## 🔧 开发指南

### 添加新的AI工具

1. 在 `app/agents/tools/` 下创建工具文件：
```python
# app/agents/tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """My custom tool description."""
    # 工具逻辑实现
    return "result"
```

2. 在 `app/agents/langgraph/agent_tools.py` 中注册工具：
```python
from app.agents.tools.my_tool import my_custom_tool

tools = [
    # 现有工具...
    my_custom_tool,
]
```

3. 重启服务测试新工具

### 扩展知识库

1. **上传文档方式**：
   - 通过Streamlit界面上传PDF文档
   - 直接将文档放入 `knowledge_base/` 目录
   - 使用API接口上传文档

2. **知识库重建**：
```python
# 通过API重建知识库
POST /api/v1/ai/advanced-planner/upload-documents
```

3. **查看知识库状态**：
```python
# 检查知识库状态
GET /api/v1/ai/advanced-planner/knowledge-base/status
```

### 自定义Agent行为

修改 `app/agents/langgraph/agent_graph.py` 中的系统提示词：

```python
system_prompt = """
你是启航引路人的AI留学规划师。

核心能力：
1. 留学申请规划和建议
2. 学校和专业推荐
3. 申请材料指导
4. 面试准备建议

# 在这里添加你的自定义指导原则
"""
```

### 数据库操作

1. **添加新的CRUD操作**：
```python
# app/crud/crud_new_model.py
from app.crud.base import CRUDBase
from app.schemas.new_model_schema import NewModelCreate, NewModelUpdate

crud_new_model = CRUDBase[NewModel, NewModelCreate, NewModelUpdate](NewModel)
```

2. **创建新的API路由**：
```python
# app/api/routers/new_router.py
from fastapi import APIRouter, Depends
from app.crud.crud_new_model import crud_new_model

router = APIRouter()

@router.post("/")
async def create_item(item: NewModelCreate, db: AsyncSession = Depends(get_db)):
    return await crud_new_model.create(db, obj_in=item)
## 🧪 测试系统

### 运行完整测试套件

```bash
# 运行所有测试
./run_tests.sh

# 或分别运行测试
python test/run_all_tests.py           # 所有功能测试
python test/agents/test_simple_agent.py # 简单Agent测试
python test/agents/test_advanced_agent.py # 高级Agent测试
python test/check_database_complete.py  # 数据库测试
```

### 测试覆盖

- ✅ **Agent功能测试**: 简单Agent (6/6通过)
- ✅ **数据库连接测试**: Supabase连接和表结构验证
- ✅ **API接口测试**: 所有路由和认证测试
- ✅ **知识库测试**: 文档上传和检索功能
- ✅ **匹配算法测试**: 智能推荐算法验证

## 🤝 贡献指南

### 参与开发

1. **Fork项目并创建分支**：
```bash
git clone https://github.com/PeerPortal/backend.git
cd backend
git checkout -b feature/AmazingFeature
```

2. **设置开发环境**：
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **进行开发并测试**：
```bash
# 运行测试确保功能正常
./run_tests.sh

# 检查代码格式
black app/ test/
flake8 app/ test/
```

4. **提交更改**：
```bash
git add .
git commit -m 'Add some AmazingFeature'
git push origin feature/AmazingFeature
```

5. **创建Pull Request**

### 开发规范

- 🐍 **Python代码**: 遵循PEP 8规范，使用type hints
- 📝 **API文档**: 所有接口必须有完整的docstring和示例
- 🧪 **测试驱动**: 新功能必须包含相应的测试用例
- 📊 **数据库**: 使用Alembic管理数据库迁移
- 🔐 **安全**: 所有敏感操作必须有适当的权限验证

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 🆘 支持与联系

### 获取帮助

- 📧 **邮箱支持**: support@peerpotal.com
- 📱 **微信群**: 扫描二维码加入开发者群
- 🐛 **Bug报告**: [GitHub Issues](https://github.com/PeerPortal/backend/issues)
- 📖 **技术文档**: 查看 `docs/` 目录获取详细文档

### 社区

- 💬 **开发者讨论**: [GitHub Discussions](https://github.com/PeerPortal/backend/discussions)
- 🎯 **功能请求**: [Feature Requests](https://github.com/PeerPortal/backend/issues/new?template=feature_request.md)
- 📚 **知识分享**: [Wiki页面](https://github.com/PeerPortal/backend/wiki)

---

## 🌟 项目愿景

**启航引路人**致力于通过AI技术和社区力量，让每一个留学梦想都能得到专业、个性化的指导。我们相信：

- 🎓 **知识共享**: 每个成功的留学经历都应该成为后来者的明灯
- 🤖 **AI赋能**: 人工智能能够让个性化指导更加精准和高效  
- 🌍 **连接世界**: 留学不仅是学术提升，更是文化交流的桥梁
- 💡 **持续创新**: 不断优化技术和服务，提供最佳用户体验

**让留学申请更智能，让梦想触手可及！** 🚀✨

---
*© 2024 启航引路人团队. All rights reserved.*

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
