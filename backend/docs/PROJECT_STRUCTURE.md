# 项目结构说明

## 目录结构

```
backend/
├── app/                     # 主应用代码
│   ├── api/                # API路由
│   ├── core/               # 核心配置
│   ├── crud/               # 数据库操作
│   └── schemas/            # 数据模型
├── docs/                   # 项目文档
│   ├── api/               # API文档
│   ├── guides/            # 使用指南
│   └── reports/           # 测试报告
├── scripts/               # 脚本工具
│   ├── database/          # 数据库脚本
│   ├── testing/           # 测试脚本
│   └── deployment/        # 部署脚本
├── configs/               # 配置文件
├── test/                  # 单元测试
├── legacy_backup/         # 旧版本备份
├── logs/                  # 日志文件
└── backups/               # 备份文件
```

## 目录说明

### `/app` - 主应用代码
- **api/**: FastAPI路由定义
- **core/**: 应用核心配置（数据库、设置等）
- **crud/**: 数据库CRUD操作
- **schemas/**: Pydantic数据模型

### `/docs` - 项目文档
- **api/**: API接口文档
- **guides/**: 配置和使用指南
- **reports/**: 测试和项目报告

### `/scripts` - 脚本工具
- **database/**: 数据库相关脚本（Schema分析、连接测试等）
- **testing/**: 测试脚本（API测试、集成测试等）
- **deployment/**: 部署相关脚本

### `/configs` - 配置文件
- 环境变量示例
- 部署配置模板

## 文件命名规范

- **脚本文件**: 使用下划线分隔，描述性命名
- **文档文件**: 使用大写和下划线，便于识别
- **配置文件**: 小写，使用点分隔

## 使用建议

1. **开发时**: 主要关注 `/app` 目录
2. **测试时**: 使用 `/scripts/testing` 中的脚本
3. **部署时**: 参考 `/scripts/deployment` 和 `/configs`
4. **文档**: 查看 `/docs` 获取详细信息

## 维护说明

- 定期清理 `/logs` 和 `/backups` 目录
- 更新文档时同步更新此README
- 新增功能时遵循目录结构规范
