# 🚀 PeerPortal AI智能体系统 - 后端API接口文档

## 📖 文档概述

**PeerPortal** 是一个专业的留学双边信息平台，连接留学申请者与目标学校学长学姐，提供个性化的留学指导服务。本文档详细介绍了后端API的所有接口。

### 🎯 系统特色
- 🤖 **AI智能体系统 v2.0** - 留学规划师 + 留学咨询师
- 🎓 **智能匹配算法** - 精准匹配申请者与引路人
- 💬 **实时沟通平台** - 论坛、消息、评价系统
- 📁 **文件管理系统** - 文档上传与管理
- 🔐 **完整认证体系** - JWT令牌 + 角色权限

---

## 🔧 **基础信息**

- **API版本**: v3.0.0
- **基础URL**: `http://localhost:8000`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **文档地址**: `http://localhost:8000/docs`

---

## 📊 **系统核心接口**

### 平台基础
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `GET` | `/` | 平台首页 | 显示平台基本信息和功能介绍 |
| `GET` | `/health` | 健康检查 | 检查服务状态和数据库连接 |
| `GET` | `/docs` | API文档 | Swagger/OpenAPI 交互式文档 |
| `GET` | `/static/{path}` | 静态文件 | 访问上传的文件资源 |

#### 平台首页响应示例
```json
{
    "message": "欢迎使用启航引路人 - 留学双边信息平台",
    "description": "连接留学申请者与目标学校学长学姐的专业指导平台",
    "version": "3.0.0",
    "features": [
        "🎓 学长学姐指导服务",
        "🎯 智能匹配算法", 
        "📚 专业留学指导",
        "💬 实时沟通交流",
        "⭐ 评价反馈体系",
        "🤖 AI智能体系统 v2.0"
    ],
    "ai_agents": {
        "version": "2.0.0",
        "types": ["study_planner", "study_consultant"],
        "api_v2": "/api/v2/agents",
        "status": "/api/v2/agents/status"
    },
    "api_docs": "/docs",
    "health_check": "/health"
}
```

---

## 🤖 **AI智能体系统 v2.0** - `/api/v2/agents`

### 概述
专业的留学AI顾问系统，包含两个核心智能体：
- **留学规划师** (`study_planner`): 个性化申请策略、选校建议、时间规划
- **留学咨询师** (`study_consultant`): 政策解答、院校信息、签证咨询

### 接口列表

#### 系统管理
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `GET` | `/status` | 系统状态 | 获取AI智能体系统运行状态 |
| `GET` | `/info` | 架构信息 | 获取系统版本和功能模块信息 |
| `GET` | `/health` | 健康检查 | AI智能体系统专用健康检查 |

#### AI对话接口
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/planner/chat` | 留学规划师对话 | 与留学规划AI智能体对话 |
| `POST` | `/consultant/chat` | 留学咨询师对话 | 与留学咨询AI智能体对话 |
| `POST` | `/chat` | 智能体自动选择 | 根据类型自动路由到相应智能体 |
| `POST` | `/planner/invoke` | 规划师调用（兼容） | 兼容旧版API的接口 |

### 请求/响应模型

#### 对话请求 (`ChatRequest`)
```json
{
    "message": "你好，我想申请美国计算机科学硕士，请给我一些建议",
    "user_id": "user_12345",
    "session_id": "session_67890"  // 可选
}
```

#### 对话响应 (`ChatResponse`)
```json
{
    "response": "您好！申请美国CS硕士是个很好的选择。我建议您从以下几个方面开始准备...",
    "agent_type": "study_planner",
    "version": "2.0",
    "user_id": "user_12345",
    "session_id": "session_67890"
}
```

#### 系统状态响应 (`SystemStatusResponse`)
```json
{
    "is_initialized": true,
    "version": "2.0.0",
    "available_agents": ["study_planner", "study_consultant"],
    "external_services": {
        "openai": true,
        "redis": true,
        "milvus": false,
        "mongodb": true
    }
}
```

### 使用示例

#### cURL 示例
```bash
# 与留学规划师对话
curl -X POST "http://localhost:8000/api/v2/agents/planner/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "message": "我想申请美国大学的计算机科学专业，请给我一些建议",
    "user_id": "test_user"
  }'

# 检查系统状态
curl -X GET "http://localhost:8000/api/v2/agents/status"
```

#### Python SDK 示例
```python
import httpx

# 创建客户端
client = httpx.Client(base_url="http://localhost:8000")

# 与AI智能体对话
response = client.post("/api/v2/agents/planner/chat", json={
    "message": "我想了解英国留学的申请流程",
    "user_id": "user_123"
}, headers={"Authorization": f"Bearer {token}"})

print(response.json())
```

---

## 🔐 **认证系统** - `/api/v1/auth`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/register` | 用户注册 | 创建新用户账户 |
| `POST` | `/login` | 用户登录 | 用户身份验证和令牌获取 |
| `POST` | `/refresh` | 令牌刷新 | 刷新访问令牌 |
| `POST` | `/logout` | 用户登出 | 注销当前会话 |

### 请求/响应示例

#### 用户注册
**请求**:
```json
POST /api/v1/auth/register
{
    "username": "student_zhang",
    "email": "zhang@example.com",
    "password": "SecurePass123!",
    "role": "student"  // 可选: student, mentor, user
}
```

**响应**:
```json
{
    "id": 123,
    "username": "student_zhang",
    "email": "zhang@example.com",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z"
}
```

#### 用户登录
**请求**:
```json
POST /api/v1/auth/login
{
    "username": "student_zhang",
    "password": "SecurePass123!"
}
```

**响应**:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": 123,
        "username": "student_zhang",
        "email": "zhang@example.com",
        "role": "student"
    }
}
```

---

## 👥 **用户管理** - `/api/v1/users`

### 接口列表
| 方法 | 路径 | 功能 | 权限要求 |
|------|------|------|----------|
| `GET` | `/me` | 获取当前用户资料 | 已登录用户 |
| `PUT` | `/me` | 更新当前用户资料 | 已登录用户 |
| `GET` | `/me/basic` | 获取基本信息 | 已登录用户 |
| `DELETE` | `/me` | 删除当前用户 | 已登录用户 |

### 响应示例

#### 用户资料 (`ProfileRead`)
```json
{
    "id": 123,
    "username": "student_zhang",
    "email": "zhang@example.com",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z",
    "full_name": "张三",
    "avatar_url": "http://localhost:8000/static/avatars/123.jpg",
    "bio": "计算机科学专业，希望申请美国研究生",
    "phone": "+86-138-0000-0000",
    "location": "北京",
    "website": "https://zhangsan.dev",
    "birth_date": "2000-01-01"
}
```

---

## 🎓 **学长学姐（引路人）管理** - `/api/v1/mentors`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/register` | 引路人注册 | 注册成为引路人 |
| `GET` | `/{mentor_id}` | 获取引路人详情 | 查看引路人详细信息 |
| `PUT` | `/{mentor_id}` | 更新引路人资料 | 更新引路人信息 |
| `GET` | `/search` | 搜索引路人 | 根据条件搜索引路人 |
| `GET` | `/` | 获取引路人列表 | 分页获取引路人信息 |
| `GET` | `/{mentor_id}/profile` | 引路人公开资料 | 获取引路人公开信息 |

### 引路人注册示例
```json
POST /api/v1/mentors/register
{
    "education": {
        "university": "斯坦福大学",
        "degree": "计算机科学硕士",
        "graduation_year": 2023
    },
    "expertise": ["机器学习", "软件工程", "创业"],
    "experience": "在Google工作2年，专注AI产品开发",
    "hourly_rate": 200,
    "availability": "周末可用",
    "languages": ["中文", "英文"],
    "certifications": ["AWS认证", "Google Cloud认证"]
}
```

---

## 🎯 **智能匹配系统** - `/api/v1/matching`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/recommend` | 推荐引路人 | 基于需求智能推荐匹配的引路人 |
| `GET` | `/filters` | 获取筛选条件 | 获取可用的筛选选项 |
| `POST` | `/filter` | 高级筛选 | 根据条件筛选引路人 |
| `GET` | `/history` | 匹配历史 | 获取用户的匹配历史记录 |
| `POST` | `/save` | 保存匹配结果 | 保存感兴趣的匹配结果 |
| `GET` | `/saved` | 获取收藏的匹配 | 获取用户收藏的引路人 |
| `GET` | `/stats` | 匹配统计 | 获取匹配系统统计信息 |
| `GET` | `/compatibility` | 兼容性检查 | 检查申请者与引路人的匹配度 |

### 匹配请求示例
```json
POST /api/v1/matching/recommend
{
    "target_universities": ["斯坦福大学", "麻省理工学院"],
    "target_majors": ["计算机科学", "人工智能"],
    "preferred_degree": "硕士",
    "budget_range": [100, 300],
    "preferred_languages": ["中文", "英文"],
    "session_type": "1对1",
    "timeline": "紧急",
    "special_requirements": "需要有AI研究经验"
}
```

### 匹配结果示例
```json
{
    "request_id": "match_12345",
    "student_id": 123,
    "total_matches": 15,
    "matches": [
        {
            "mentor_id": 456,
            "mentor_name": "李导师",
            "university": "斯坦福大学",
            "major": "计算机科学",
            "match_score": 0.95,
            "match_reasons": ["专业完全匹配", "有AI研究经验", "支持中文沟通"],
            "hourly_rate": 250,
            "rating": 4.9,
            "total_sessions": 120
        }
    ],
    "filters_applied": { /* 应用的筛选条件 */ },
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

## 💼 **指导服务管理** - `/api/v1/services`

### 接口列表
| 方法 | 路径 | 功能 | 权限要求 |
|------|------|------|----------|
| `POST` | `/` | 创建服务 | 引路人权限 |
| `GET` | `/` | 获取服务列表 | 所有用户 |
| `GET` | `/{service_id}` | 获取服务详情 | 所有用户 |
| `PUT` | `/{service_id}` | 更新服务 | 服务创建者 |
| `DELETE` | `/{service_id}` | 删除服务 | 服务创建者 |

### 服务创建示例
```json
POST /api/v1/services/
{
    "title": "斯坦福CS申请一对一指导",
    "description": "提供从选校到面试的全流程指导",
    "category": "申请指导",
    "price": 300,
    "duration": 60,
    "session_type": "视频通话",
    "included_services": [
        "申请策略制定",
        "文书修改指导", 
        "面试模拟练习"
    ],
    "target_audience": "申请美国CS硕士的学生"
}
```

---

## 📝 **论坛系统** - `/api/v1/forum`

### 接口列表

#### 论坛分类和帖子
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `GET` | `/categories` | 获取论坛分类 | 获取所有论坛分类 |
| `GET` | `/posts` | 获取帖子列表 | 获取论坛帖子（支持搜索筛选） |
| `POST` | `/posts` | 创建帖子 | 发布新帖子 |
| `GET` | `/posts/{post_id}` | 获取帖子详情 | 查看帖子详细内容 |
| `PUT` | `/posts/{post_id}` | 更新帖子 | 编辑帖子内容 |
| `DELETE` | `/posts/{post_id}` | 删除帖子 | 删除帖子 |
| `POST` | `/posts/{post_id}/like` | 点赞帖子 | 给帖子点赞 |

#### 回复系统
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `GET` | `/posts/{post_id}/replies` | 获取回复列表 | 获取帖子的回复 |
| `POST` | `/posts/{post_id}/replies` | 创建回复 | 回复帖子 |
| `PUT` | `/replies/{reply_id}` | 更新回复 | 编辑回复内容 |
| `DELETE` | `/replies/{reply_id}` | 删除回复 | 删除回复 |

#### 标签系统
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `GET` | `/tags/popular` | 获取热门标签 | 获取论坛热门标签 |

### 帖子创建示例
```json
POST /api/v1/forum/posts
{
    "title": "求助：斯坦福CS申请经验分享",
    "content": "大家好，我是今年刚被Stanford CS录取的学生...",
    "category": "申请经验",
    "tags": ["斯坦福", "CS", "申请经验", "GRE"],
    "is_anonymous": false
}
```

### 帖子查询参数
```
GET /api/v1/forum/posts?category=申请经验&search=斯坦福&sort_by=latest&limit=20&offset=0
```

---

## 📁 **文件上传系统** - `/api/v1/files`

### 接口列表
| 方法 | 路径 | 功能 | 文件类型 |
|------|------|------|----------|
| `POST` | `/upload/avatar` | 上传头像 | 图片文件 (jpg, png, gif) |
| `POST` | `/upload/document` | 上传文档 | 文档文件 (pdf, doc, docx) |
| `POST` | `/upload/general` | 通用文件上传 | 多种格式支持 |
| `DELETE` | `/{file_id}` | 删除文件 | - |

### 文件上传示例
```bash
# 上传头像
curl -X POST "http://localhost:8000/api/v1/files/upload/avatar" \
  -H "Authorization: Bearer your_jwt_token" \
  -F "file=@avatar.jpg"

# 上传申请文档
curl -X POST "http://localhost:8000/api/v1/files/upload/document" \
  -H "Authorization: Bearer your_jwt_token" \
  -F "file=@personal_statement.pdf" \
  -F "description=个人陈述"
```

### 文件上传响应
```json
{
    "file_id": "file_12345",
    "filename": "avatar.jpg",
    "original_filename": "my_photo.jpg",
    "file_url": "http://localhost:8000/static/avatars/file_12345.jpg",
    "file_size": 204800,
    "content_type": "image/jpeg",
    "uploaded_at": "2024-01-01T10:00:00Z"
}
```

---

## 💬 **消息系统** - `/api/v1/messages`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/` | 发送消息 | 发送私信给其他用户 |
| `GET` | `/` | 获取消息列表 | 查看收到/发送的消息 |
| `GET` | `/{message_id}` | 获取消息详情 | 查看消息详细内容 |
| `PUT` | `/{message_id}` | 标记已读 | 标记消息为已读状态 |
| `DELETE` | `/{message_id}` | 删除消息 | 删除消息 |

### 发送消息示例
```json
POST /api/v1/messages/
{
    "recipient_id": 456,
    "subject": "关于斯坦福申请咨询",
    "content": "您好，我看到您是斯坦福CS的学长，想请教一些申请问题...",
    "message_type": "consultation_inquiry"
}
```

---

## ⭐ **评价反馈系统** - `/api/v1/reviews`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/` | 创建评价 | 对指导服务进行评价 |
| `GET` | `/` | 获取评价列表 | 查看评价列表 |
| `GET` | `/{review_id}` | 获取评价详情 | 查看评价详细信息 |
| `PUT` | `/{review_id}` | 更新评价 | 更新评价内容 |
| `DELETE` | `/{review_id}` | 删除评价 | 删除评价 |

### 评价创建示例
```json
POST /api/v1/reviews/
{
    "mentor_id": 456,
    "session_id": 789,
    "rating": 5,
    "title": "非常专业的指导服务",
    "content": "李导师非常专业，帮我制定了详细的申请计划...",
    "tags": ["专业", "耐心", "经验丰富"],
    "would_recommend": true
}
```

---

## 📅 **指导会话管理** - `/api/v1/sessions`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/` | 创建会话 | 预约指导会话 |
| `GET` | `/` | 获取会话列表 | 查看用户的指导会话 |
| `GET` | `/{session_id}` | 获取会话详情 | 查看会话详细信息 |
| `PUT` | `/{session_id}` | 更新会话 | 更新会话状态或信息 |
| `DELETE` | `/{session_id}` | 取消会话 | 取消指导会话 |

### 会话预约示例
```json
POST /api/v1/sessions/
{
    "mentor_id": 456,
    "service_id": 789,
    "preferred_time": "2024-01-15T14:00:00Z",
    "duration": 60,
    "session_type": "video_call",
    "notes": "希望重点讨论个人陈述的写作",
    "contact_preference": "zoom"
}
```

---

## 🎯 **学弟学妹（申请者）管理** - `/api/v1/students`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/register` | 申请者注册 | 注册成为申请者 |
| `GET` | `/{student_id}` | 获取申请者详情 | 查看申请者信息 |
| `PUT` | `/{student_id}` | 更新申请者资料 | 更新申请者信息 |
| `GET` | `/{student_id}/profile` | 申请者公开资料 | 获取申请者公开信息 |
| `DELETE` | `/{student_id}` | 删除申请者 | 删除申请者信息 |

### 申请者注册示例
```json
POST /api/v1/students/register
{
    "academic_background": {
        "current_school": "北京大学",
        "major": "计算机科学",
        "gpa": 3.8,
        "graduation_year": 2024
    },
    "target_applications": {
        "universities": ["斯坦福大学", "MIT", "CMU"],
        "majors": ["计算机科学", "人工智能"],
        "degree_level": "硕士",
        "application_year": 2024
    },
    "test_scores": {
        "gre": {"verbal": 160, "quantitative": 170, "writing": 4.5},
        "toefl": 110,
        "ielts": null
    },
    "experience": {
        "internships": ["腾讯AI实习生", "字节跳动算法实习"],
        "research": ["深度学习项目", "NLP研究"],
        "competitions": ["ACM竞赛银牌"]
    }
}
```

---

## 🔧 **兼容性API** - `/api/v1`

### 接口列表
| 方法 | 路径 | 功能 | 描述 |
|------|------|------|------|
| `POST` | `/planner/invoke` | AI规划师调用 | 兼容旧版的AI规划师接口 |

---

## 🔐 **认证和权限**

### JWT Token 使用
所有需要认证的API都需要在请求头中包含JWT令牌：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 用户角色
- **student**: 申请者，可以搜索引路人、预约会话
- **mentor**: 引路人，可以提供指导服务、接受预约
- **admin**: 管理员，拥有所有权限
- **user**: 普通用户，基础功能

### 权限控制示例
```python
# 只有引路人可以创建服务
@router.post("/services/", dependencies=[Depends(require_mentor_role())])

# 只有申请者可以预约会话
@router.post("/sessions/", dependencies=[Depends(require_student_role())])

# 管理员权限
@router.delete("/admin/users/{user_id}", dependencies=[Depends(require_admin_role())])
```

---

## 📊 **错误处理**

### 标准错误响应格式
```json
{
    "detail": "错误描述信息",
    "error_code": "ERROR_CODE",
    "timestamp": "2024-01-01T10:00:00Z",
    "path": "/api/v1/users/me"
}
```

### 常见HTTP状态码
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或令牌无效
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### AI智能体特殊错误
```json
{
    "detail": "智能体错误: 用户输入过长",
    "error_code": "AGENT_INPUT_TOO_LONG",
    "agent_type": "study_planner",
    "max_length": 2000
}
```

---

## 🚀 **快速开始**

### 1. 获取API文档
访问 `http://localhost:8000/docs` 查看交互式API文档

### 2. 健康检查
```bash
curl http://localhost:8000/health
```

### 3. 注册用户
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### 4. 登录获取令牌
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "TestPass123!"
  }'
```

### 5. 使用AI智能体
```bash
curl -X POST "http://localhost:8000/api/v2/agents/planner/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "我想申请美国计算机科学硕士，请给我一些建议",
    "user_id": "test_user"
  }'
```

---

## 📱 **SDK 和工具**

### Python SDK 示例
```python
import httpx
from typing import Optional

class PeerPortalClient:
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.client = httpx.Client(base_url=base_url)
        if token:
            self.client.headers["Authorization"] = f"Bearer {token}"
    
    def chat_with_planner(self, message: str, user_id: str):
        """与留学规划师对话"""
        response = self.client.post("/api/v2/agents/planner/chat", json={
            "message": message,
            "user_id": user_id
        })
        return response.json()
    
    def search_mentors(self, **filters):
        """搜索引路人"""
        response = self.client.post("/api/v1/matching/recommend", json=filters)
        return response.json()

# 使用示例
client = PeerPortalClient(token="your_jwt_token")
result = client.chat_with_planner("我想申请斯坦福CS", "user_123")
print(result["response"])
```

### JavaScript SDK 示例
```javascript
class PeerPortalAPI {
    constructor(baseURL = 'http://localhost:8000', token = null) {
        this.baseURL = baseURL;
        this.token = token;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
            ...options.headers
        };
        
        const response = await fetch(url, { ...options, headers });
        return response.json();
    }
    
    async chatWithPlanner(message, userId) {
        return this.request('/api/v2/agents/planner/chat', {
            method: 'POST',
            body: JSON.stringify({ message, user_id: userId })
        });
    }
}

// 使用示例
const api = new PeerPortalAPI('http://localhost:8000', 'your_jwt_token');
const result = await api.chatWithPlanner('我想申请MIT', 'user_123');
console.log(result.response);
```

---

## 🔄 **版本历史**

### v3.0.0 (当前版本)
- ✅ AI智能体系统 v2.0 完整实现
- ✅ 智能匹配算法优化
- ✅ 论坛系统完整功能
- ✅ 文件上传系统
- ✅ 完整的认证和权限体系

### v2.x.x
- 🏗️ 基础平台功能
- 🏗️ 用户管理系统
- 🏗️ 初版AI功能

### v1.x.x
- 🏗️ 项目初始版本
- 🏗️ 核心架构搭建

---

## 📞 **技术支持**

### 开发团队联系
- **项目仓库**: [GitHub Repository]
- **API文档**: `http://localhost:8000/docs`
- **技术文档**: `/docs` 目录

### 常见问题
1. **Q: 如何获取JWT令牌？**
   A: 通过 `/api/v1/auth/login` 接口登录获取

2. **Q: AI智能体不响应怎么办？**
   A: 检查 `/api/v2/agents/status` 确认系统状态

3. **Q: 文件上传失败？**
   A: 检查文件大小限制和格式要求

4. **Q: 权限不足错误？**
   A: 确认用户角色和令牌有效性

---

**📍 最后更新**: 2024年12月  
**📍 API版本**: v3.0.0  
**📍 文档版本**: v1.0.0

---

🎉 **感谢使用 PeerPortal AI智能体系统！** 🎉 