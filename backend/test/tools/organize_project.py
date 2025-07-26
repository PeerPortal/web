#!/usr/bin/env python3
"""
项目结构整理脚本
将散乱的文件按功能分类归档到合适的目录
"""

import os
import shutil
from pathlib import Path

def organize_project():
    """整理项目结构"""
    base_dir = Path("/Users/frederick/Documents/peerpotal/backend")
    
    print("🗂️ 开始整理项目结构...")
    
    # 1. 创建目录结构
    directories = {
        "docs": "项目文档",
        "docs/api": "API文档",
        "docs/guides": "使用指南",
        "docs/reports": "测试报告",
        "scripts": "脚本工具",
        "scripts/database": "数据库相关脚本",
        "scripts/testing": "测试脚本",
        "scripts/deployment": "部署脚本",
        "configs": "配置文件",
        "logs": "日志文件",
        "backups": "备份文件"
    }
    
    for dir_path, description in directories.items():
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {dir_path} - {description}")
    
    # 2. 文件归类映射
    file_mappings = {
        # 文档类
        "API_TEST_COMPLETE_GUIDE.md": "docs/api/",
        "DB_CONFIG_HELP.md": "docs/guides/",
        "ENV_CONFIG_GUIDE.md": "docs/guides/",
        "TEAM_COLLABORATION_GUIDE.md": "docs/guides/",
        "MODULE_TEST_REPORT.md": "docs/reports/",
        "PROJECT_UPDATE_COMPLETE_SUMMARY.md": "docs/reports/",
        "TEST_SUMMARY_REPORT.md": "docs/reports/",
        "前端.md": "docs/",
        "后端.md": "docs/",
        "应用启动成功.md": "docs/reports/",
        "数据库连接问题解决报告.md": "docs/reports/",
        
        # 数据库脚本
        "analyze_table_schema.py": "scripts/database/",
        "check_table_structure.py": "scripts/database/",
        "discover_structure.py": "scripts/database/",
        "get_table_fields.py": "scripts/database/",
        "fix_db_connection.py": "scripts/database/",
        "fix_supabase_calls.py": "scripts/database/",
        "db_schema.sql": "scripts/database/",
        
        # 测试脚本
        "test_api_comprehensive.py": "scripts/testing/",
        "test_comprehensive_api.py": "scripts/testing/",
        "test_database_comprehensive.py": "scripts/testing/",
        "test_db_connection.py": "scripts/testing/",
        "test_fix_verification.py": "scripts/testing/",
        "test_fixed_apis.py": "scripts/testing/",
        "test_simple_fix.py": "scripts/testing/",
        "test_supabase_api.py": "scripts/testing/",
        "run_comprehensive_tests.py": "scripts/testing/",
        "quick_health_check.py": "scripts/testing/",
        "test_report_1753365747.json": "scripts/testing/",
        
        # 部署和工具脚本
        "start_new_app.py": "scripts/deployment/",
        "start_server.sh": "scripts/deployment/",
        "update_routes.py": "scripts/",
        "fix_schemas.py": "scripts/",
        
        # 配置文件
        "env_example.txt": "configs/",
    }
    
    # 3. 移动文件
    moved_files = 0
    for filename, target_dir in file_mappings.items():
        source_path = base_dir / filename
        target_path = base_dir / target_dir / filename
        
        if source_path.exists():
            try:
                # 确保目标目录存在
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 移动文件
                shutil.move(str(source_path), str(target_path))
                print(f"📄 移动: {filename} → {target_dir}")
                moved_files += 1
            except Exception as e:
                print(f"❌ 移动失败 {filename}: {e}")
        else:
            print(f"⚠️ 文件不存在: {filename}")
    
    # 4. 创建README文件说明新结构
    create_structure_readme(base_dir)
    
    # 5. 更新.gitignore
    update_gitignore(base_dir)
    
    print(f"\n✅ 项目整理完成！")
    print(f"📊 共移动 {moved_files} 个文件")
    print(f"📁 创建 {len(directories)} 个目录")
    
    return True

def create_structure_readme(base_dir):
    """创建项目结构说明文档"""
    readme_content = """# 项目结构说明

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
"""
    
    readme_path = base_dir / "PROJECT_STRUCTURE.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📝 创建项目结构文档: PROJECT_STRUCTURE.md")

def update_gitignore(base_dir):
    """更新.gitignore文件"""
    gitignore_additions = """
# 新增的目录结构忽略规则
logs/*.log
logs/**/*.log
backups/**
*.tmp
*.temp
.DS_Store
Thumbs.db

# IDE和编辑器
.vscode/
.idea/
*.swp
*.swo
*~

# 临时文件
tmp/
temp/
cache/
"""
    
    gitignore_path = base_dir / ".gitignore"
    
    # 读取现有内容
    existing_content = ""
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # 如果新内容不存在，则添加
    if "# 新增的目录结构忽略规则" not in existing_content:
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write(gitignore_additions)
        print("📝 更新 .gitignore 文件")

if __name__ == "__main__":
    organize_project()
