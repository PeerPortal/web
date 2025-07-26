# PeerPortal 留学平台后端 API 文档

## 概述

PeerPortal 是一个留学申请一站式服务平台，连接学生与已录取的学长学姐导师。平台提供 AI 智能咨询、导师匹配、论坛交流、申请指导等功能。

**API 基础URL**: `http://localhost:8000`  
**API 版本**: v1  
**认证方式**: Bearer Token (JWT)

## 目录

1. [认证系统 API](#1-认证系统-api)
2. [用户管理 API](#2-用户管理-api)
3. [导师系统 API](#3-导师系统-api)
4. [AI 智能顾问 API](#4-ai-智能顾问-api)
5. [论坛系统 API](#5-论坛系统-api)
6. [消息系统 API](#6-消息系统-api)
7. [会话预约 API](#7-会话预约-api)
8. [评价系统 API](#8-评价系统-api)
9. [服务订单 API](#9-服务订单-api)
10. [学生档案 API](#10-学生档案-api)

---

## 1. 认证系统 API

### 1.1 用户登录

**POST** `/api/v1/auth/login`

登录获取访问令牌。

**请求参数** (Form Data):
```
username: string  // 用户名
password: string  // 密码
```

**响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 1.2 用户注册

**POST** `/api/v1/auth/register`

创建新用户账户。

**请求体**:
```json
{
  "username": "student123",
  "email": "student@example.com",
  "password": "securePassword123",
  "role": "student"
}
```

**响应示例**:
```json
{
  "id": 1,
  "username": "student123",
  "email": "student@example.com",
  "role": "student",
  "is_active": true,
  "created_at": "2024-01-20T10:30:00Z"
}
```

### 1.3 刷新令牌

**POST** `/api/v1/auth/refresh`

刷新访问令牌。

**请求头**:
```
Authorization: Bearer <token>
```

---

## 2. 用户管理 API

### 2.1 获取当前用户信息

**GET** `/api/v1/users/me`

**响应示例**:
```json
{
  "id": 1,
  "username": "student123",
  "email": "student@example.com",
  "full_name": "张三",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "立志申请美国TOP10大学的计算机科学专业",
  "phone": "+86-138-0000-0000",
  "location": "北京市",
  "role": "student",
  "created_at": "2024-01-20T10:30:00Z"
}
```

### 2.2 更新用户信息

**PUT** `/api/v1/users/me`

**请求体**:
```json
{
  "full_name": "张三",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "立志申请美国TOP10大学的计算机科学专业",
  "phone": "+86-138-0000-0000",
  "location": "北京市"
}
```

---

## 3. 导师系统 API

### 3.1 搜索导师

**GET** `/api/v1/mentors/search`

**查询参数**:
```
search_query: string (可选)     // 搜索关键词
university: string (可选)       // 大学名称
major: string (可选)           // 专业
limit: number (可选, 默认20)   // 每页数量
offset: number (可选, 默认0)   // 偏移量
```

**响应示例**:
```json
[
  {
    "id": 1,
    "mentor_id": 1,
    "title": "斯坦福大学 计算机科学 导师",
    "description": "Stanford CS MS毕业，现任Google软件工程师",
    "hourly_rate": 200,
    "rating": 4.9,
    "sessions_completed": 127
  }
]
```

### 3.2 获取导师详细资料

**GET** `/api/v1/mentors/{mentor_id}`

### 3.3 创建导师档案

**POST** `/api/v1/mentors/profile`

**请求体**:
```json
{
  "title": "斯坦福大学 计算机科学 导师",
  "description": "Stanford CS MS毕业，现任Google软件工程师",
  "hourly_rate": 200,
  "session_duration_minutes": 60
}
```

---

## 4. AI 智能顾问 API

### 4.1 AI 对话接口

**POST** `/api/v1/planner/invoke`

**请求体**:
```json
{
  "input": "我想申请美国的计算机科学硕士，需要什么条件？",
  "session_id": "session_123",
  "stream": true
}
```

**流式响应格式**:
```
data: {"type": "start", "content": "开始分析您的问题..."}
data: {"type": "thinking", "content": "正在分析美国CS硕士申请要求..."}
data: {"type": "final_answer", "content": "美国计算机科学硕士申请通常需要..."}
data: {"type": "end"}
```

### 4.2 获取AI能力

**GET** `/api/v1/planner/capabilities`

**响应示例**:
```json
{
  "capabilities": [
    "学校专业推荐",
    "申请要求查询",
    "时间规划制定",
    "文书建议",
    "导师匹配"
  ],
  "status": "active",
  "version": "1.0.0"
}
```

---

## 5. 论坛系统 API

### 5.1 获取论坛分类

**GET** `/api/v1/forum/categories`

**响应示例**:
```json
[
  {
    "id": "application",
    "name": "申请经验",
    "description": "分享申请经验、文书写作、面试技巧",
    "post_count": 156,
    "icon": "📝"
  }
]
```

### 5.2 获取帖子列表

**GET** `/api/v1/forum/posts`

**查询参数**:
```
category: string (可选)        // 分类ID
search: string (可选)          // 搜索关键词
sort_by: string (可选)         // 排序方式
limit: number (可选, 默认20)   // 每页数量
offset: number (可选, 默认0)   // 偏移量
```

**响应示例**:
```json
{
  "posts": [
    {
      "id": 1,
      "title": "如何准备MIT计算机科学申请？",
      "content": "大家好，我是大三学生...",
      "author": {
        "id": 1,
        "username": "小明同学",
        "role": "student",
        "university": "清华大学"
      },
      "category": "application",
      "tags": ["MIT", "计算机科学"],
      "replies_count": 15,
      "likes_count": 23,
      "views_count": 156,
      "created_at": "2024-01-20T10:30:00Z"
    }
  ],
  "total": 50
}
```

### 5.3 创建帖子

**POST** `/api/v1/forum/posts`

**请求体**:
```json
{
  "title": "如何准备MIT计算机科学申请？",
  "content": "大家好，我是大三学生...",
  "category": "application",
  "tags": ["MIT", "计算机科学"]
}
```

### 5.4 点赞帖子

**POST** `/api/v1/forum/posts/{post_id}/like`

### 5.5 获取帖子回复

**GET** `/api/v1/forum/posts/{post_id}/replies`

### 5.6 创建回复

**POST** `/api/v1/forum/posts/{post_id}/replies`

---

## 6. 消息系统 API

### 6.1 获取对话列表

**GET** `/api/v1/messages/conversations`

**响应示例**:
```json
[
  {
    "conversation_id": "conv_123",
    "mentor_id": 1,
    "mentor_name": "张导师",
    "last_message": "好的，我们明天下午2点开始吧",
    "last_message_time": "2024-01-20T15:45:00Z",
    "unread_count": 2,
    "is_online": true
  }
]
```

### 6.2 获取对话详情

**GET** `/api/v1/messages/conversations/{conversation_id}`

### 6.3 发送消息

**POST** `/api/v1/messages`

**请求体**:
```json
{
  "recipient_id": 2,
  "content": "您好，我想咨询一下美国CS申请的问题",
  "conversation_id": "conv_123"
}
```

---

## 7. 会话预约 API

### 7.1 获取用户会话列表

**GET** `/api/v1/sessions`

**响应示例**:
```json
[
  {
    "id": "session_789",
    "mentor_id": 1,
    "mentor_name": "张导师",
    "title": "美国CS硕士申请咨询",
    "scheduled_time": "2024-01-25T14:00:00Z",
    "duration_minutes": 60,
    "status": "scheduled",
    "amount": 200
  }
]
```

### 7.2 创建会话预约

**POST** `/api/v1/sessions`

### 7.3 获取会话统计

**GET** `/api/v1/sessions/statistics`

**响应示例**:
```json
{
  "total_sessions": 5,
  "total_hours": 8.5,
  "average_rating": 4.8,
  "completed_applications": 3
}
```

---

## 8. 评价系统 API

### 8.1 创建评价

**POST** `/api/v1/reviews`

### 8.2 我的评价

**GET** `/api/v1/reviews/my-reviews`

---

## 9. 服务订单 API

### 9.1 获取我的订单

**GET** `/api/v1/services/orders/my-orders`

---

## 10. 学生档案 API

### 10.1 获取学生档案

**GET** `/api/v1/students/profile`

**响应示例**:
```json
{
  "id": 1,
  "target_degree": "Master",
  "target_major": "Computer Science",
  "target_countries": ["美国", "加拿大"],
  "academic_background": {
    "current_university": "清华大学",
    "current_major": "计算机科学与技术",
    "current_gpa": 3.8
  },
  "test_scores": {
    "toefl": {
      "total": 108,
      "test_date": "2023-10-15"
    }
  }
}
```

---

## 错误码说明

### HTTP状态码
- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权/token无效
- `403` - 权限不足
- `404` - 资源不存在
- `500` - 服务器内部错误

### 业务错误码
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "用户名或密码错误"
  }
}
```

---

## 认证和授权

### JWT Token格式
```json
{
  "sub": "user_123",
  "username": "student123",
  "role": "student",
  "exp": 1640995200
}
```

### 请求头格式
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

---

## 前端集成说明

基于前端代码分析，本API设计考虑了以下前端需求：

1. **认证流程**: 支持登录、注册、token刷新和自动重新认证
2. **导师搜索**: 提供灵活的搜索和筛选功能，支持分页
3. **AI对话**: 流式响应，实时显示思考过程和工具调用
4. **论坛交互**: 完整的帖子管理、回复、点赞功能
5. **消息通信**: 实时聊天，支持导师学生沟通
6. **个人资料**: 用户信息管理和学习统计
7. **会话管理**: 预约系统和进度跟踪

### 前端状态管理集成

API设计与前端Zustand状态管理兼容：

- 认证状态自动同步localStorage
- 用户信息实时更新
- 错误处理和重试机制
- 流式数据处理支持

### 实时功能

- AI对话流式响应
- 消息实时推送
- 在线状态同步
- 通知系统

**最后更新**: 2024年1月20日  
**API版本**: v1.0.0 