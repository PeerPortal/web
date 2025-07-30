# 🤖 AI智能体系统 v2.0 - 快速入门指南

## 🎯 什么是 PeerPortal AI智能体系统？

这是一个专业的**留学规划AI顾问**，包含两个核心智能体：

### 🎓 留学规划师 (StudyPlannerAgent)
- **功能**: 制定个性化留学申请策略
- **特长**: 院校推荐、时间规划、背景分析
- **适用场景**: "我想申请美国CS硕士，请帮我制定申请计划"

### 💬 留学咨询师 (StudyConsultantAgent)  
- **功能**: 提供留学政策和生活咨询
- **特长**: 费用分析、签证指导、生活建议
- **适用场景**: "英国留学一年费用是多少？"

---

## ⚡ 30秒快速体验

```bash
# 1. 激活环境并测试
cd backend
source venv/bin/activate
python test_v2_config.py

# 2. 启动服务
python -m uvicorn app.main:app --reload

# 3. 访问 API 文档
open http://localhost:8000/docs
```

---

## 🔧 核心技术特性

### 🧠 智能记忆系统
- **短期记忆**: 维持当前会话连续性 (24小时)
- **长期记忆**: 学习用户偏好和历史申请信息
- **智能检索**: 基于上下文自动调用相关记忆

### 🔍 知识增强 (RAG)
- **文档支持**: PDF、Word、Markdown等
- **实时检索**: 从知识库获取最新申请信息
- **智能匹配**: 根据用户问题精准检索相关内容

### 🛠️ 工具集成
```python
内置工具:
- find_mentors_tool     # 查找学长学姐
- find_services_tool    # 查找留学服务
- web_search_tool       # 实时网络搜索
- get_platform_stats    # 平台数据统计
```

### 🎭 状态机架构 (LangGraph)
```
用户输入 → 思考分析 → 记忆检索 → 知识检索 → 工具调用 → 生成回答
```

---

## 📱 API 使用示例

### 与留学规划师对话
```bash
curl -X POST "http://localhost:8000/api/v2/agents/planner/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想申请美国大学CS专业",
    "user_id": "user_123"
  }'
```

### 与留学咨询师对话
```bash
curl -X POST "http://localhost:8000/api/v2/agents/consultant/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "美国留学费用大概是多少？",
    "user_id": "user_123"
  }'
```

### Python SDK 使用
```python
from app.agents.v2 import create_study_planner, create_study_consultant

# 创建智能体
planner = create_study_planner("user_123")
consultant = create_study_consultant("user_123")

# 获取建议
plan_response = await planner.execute("我想申请MIT的CS硕士")
cost_info = await consultant.execute("MIT一年学费是多少？")

print(f"申请建议: {plan_response}")
print(f"费用信息: {cost_info}")
```

---

## 🎬 实际对话示例

### 场景一：制定申请策略
```
🧑 用户: "我是国内985本科CS专业，GPA 3.7，想申请美国top30的CS硕士"

🤖 规划师: "根据你的背景，我为你分析一下申请策略：

【背景评估】
- 985院校背景：优势明显 ✅
- CS专业对口：专业匹配度高 ✅  
- GPA 3.7：中上水平，需要其他方面补强 ⚠️

【推荐院校层次】
- 冲刺档：Stanford, MIT, CMU (需要突出亮点)
- 主申档：UIUC, Georgia Tech, UT Austin
- 保底档：UCSD, Northeastern, NYU

【提升建议】
1. 科研经历：寻找AI/ML相关研究项目
2. 实习经验：FAANG或知名tech公司实习
3. GRE分数：目标320+
4. 个人项目：GitHub上展示技术能力

需要我详细制定时间规划吗？"
```

### 场景二：费用咨询
```
🧑 用户: "加州大学的学费和生活费大概是多少？"

🤖 咨询师: "加州大学系统的费用分析如下：

【学费 (2024-2025学年)】
- UC Berkeley/UCLA: ~$48,000/年
- UC San Diego/Irvine: ~$46,000/年
- UC Davis/Santa Barbara: ~$44,000/年

【生活费 (按地区)】
- 湾区 (Berkeley): $25,000-30,000/年
- 洛杉矶 (UCLA): $20,000-25,000/年
- 圣地亚哥 (UCSD): $18,000-22,000/年

【总费用预估】
- 湾区UC: $73,000-78,000/年
- 其他UC: $62,000-70,000/年

【省钱建议】
1. 申请TA/RA职位 (可减免学费)
2. 校外合租 (比宿舍便宜30%)
3. 申请奖学金和助学金

需要我帮你分析具体的资金规划吗？"
```

---

## 🔨 环境配置

### 最小化配置 (仅需OpenAI)
```bash
# .env 文件
OPENAI_API_KEY=sk-proj-xxx
DEBUG=True
```

### 完整配置 (包含记忆和知识库)
```bash
# .env 文件
OPENAI_API_KEY=sk-proj-xxx
REDIS_URL=redis://localhost:6379
MILVUS_HOST=localhost:19530
MONGODB_URL=mongodb://localhost:27017
DEBUG=True
```

### Docker 快速部署
```bash
# 使用 Docker Compose
docker-compose up -d

# 或者单独运行
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-proj-xxx \
  peerpotal-ai-agent:latest
```

---

## 📊 系统监控

### 健康检查
```bash
# 检查系统状态
curl http://localhost:8000/api/v2/agents/status

# 检查各组件状态
curl http://localhost:8000/health
```

### 性能指标
```python
# 当前系统配置
{
    "🤖 LLM模型": 3,           # gpt-4o-mini, gpt-4, gpt-3.5-turbo
    "📊 嵌入模型": 3,          # ada-002, 3-small, 3-large  
    "💾 Redis缓存": "✅",      # 短期记忆
    "🔍 向量数据库": "⚪",     # 长期记忆 (可选)
    "📄 文档数据库": "⚪",     # 知识存储 (可选)
    "🛠️ 工具数量": 4          # 内置工具
}
```

---

## 🚨 常见问题

### Q: 如何提高响应速度？
```python
# 使用更快的模型
DEFAULT_MODEL = "gpt-4o-mini"  # 代替 gpt-4

# 启用缓存
REDIS_URL = "redis://localhost:6379"

# 并发处理
AGENT_MAX_CONCURRENT = 5
```

### Q: 如何添加自定义知识？
```python
# 1. 上传文档到 knowledge_base/ 目录
# 2. 重启系统自动索引
# 3. 或手动触发索引
from app.agents.v2.data_communication.rag.rag_manager import rag_manager
await rag_manager.index_document("path/to/document.pdf")
```

### Q: 如何监控token使用？
```python
# 查看使用统计
curl http://localhost:8000/api/v2/agents/usage-stats

# 设置使用限制
DAILY_TOKEN_LIMIT = 100000
USER_TOKEN_LIMIT = 1000
```

---

## 🎯 应用场景

### 🏫 教育机构
- **留学中介**: 提供24/7智能咨询服务
- **国际学校**: 为学生提供申请指导
- **培训机构**: 增强服务价值

### 🎓 个人用户  
- **留学申请者**: 获得专业的申请建议
- **在读学生**: 了解转学和升学机会
- **家长**: 了解留学政策和费用

### 🏢 企业应用
- **人力资源**: 员工海外培训规划
- **教育科技**: 集成AI咨询功能
- **在线平台**: 提升用户体验

---

## 🔄 版本演进

### v2.0.0 当前版本 ✅
- 双智能体系统 (规划师 + 咨询师)
- LangGraph 状态机架构
- 双层记忆系统
- RAG 知识检索
- 工具集成框架

### v2.1.0 即将发布 🚧
- 流式响应支持
- 更多智能体类型 (文书润色师、面试教练)
- 多语言支持 (英文、中文)
- 移动端API优化

### v2.2.0 规划中 📋
- 语音对话支持
- 图表和数据可视化
- 个性化推荐引擎
- 多租户架构

---

## 🎉 立即开始

1. **克隆项目**: `git clone https://github.com/yourrepo/peerpotal.git`
2. **安装依赖**: `pip install -r requirements.txt`  
3. **配置OpenAI**: 设置 `OPENAI_API_KEY`
4. **运行测试**: `python test_v2_config.py`
5. **启动服务**: `uvicorn app.main:app --reload`
6. **开始对话**: 访问 `http://localhost:8000/docs`

---

**🌟 让AI成为你的专属留学顾问！**

📞 技术支持: 查看 `docs/AI_AGENT_SYSTEM_V2_文档.md` 获取完整文档

*更新时间: 2024年12月* 