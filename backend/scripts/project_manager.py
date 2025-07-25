#!/usr/bin/env python3
"""
项目管理工具
提供项目维护、清理、检查等功能
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class ProjectManager:
    def __init__(self, project_root="/Users/frederick/Documents/peerpotal/backend"):
        self.project_root = Path(project_root)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def show_structure(self):
        """显示项目结构"""
        print("📁 当前项目结构:")
        print("=" * 50)
        
        def print_tree(path, prefix="", is_last=True):
            if path.name.startswith('.'):
                return
            
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{path.name}/")
            
            if path.is_dir():
                children = [p for p in path.iterdir() if not p.name.startswith('.')]
                children.sort(key=lambda x: (x.is_file(), x.name.lower()))
                
                for i, child in enumerate(children):
                    is_last_child = i == len(children) - 1
                    extension = "    " if is_last else "│   "
                    if child.is_dir():
                        print_tree(child, prefix + extension, is_last_child)
                    else:
                        child_connector = "└── " if is_last_child else "├── "
                        print(f"{prefix}{extension}{child_connector}{child.name}")
        
        print_tree(self.project_root)
    
    def create_backup(self):
        """创建项目备份"""
        backup_dir = self.project_root / "backups" / f"backup_{self.timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份重要文件和目录
        important_items = ["app", "docs", "scripts", "requirements.txt", ".env.test", "README.md"]
        
        print(f"🔄 创建备份到: {backup_dir}")
        
        for item in important_items:
            source_path = self.project_root / item
            if source_path.exists():
                target_path = backup_dir / item
                if source_path.is_dir():
                    shutil.copytree(source_path, target_path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                else:
                    shutil.copy2(source_path, target_path)
                print(f"  ✅ 备份: {item}")
        
        print(f"📦 备份完成: {backup_dir}")
        return backup_dir
    
    def clean_project(self):
        """清理项目文件"""
        print("🧹 开始清理项目...")
        
        # 清理Python缓存
        cache_patterns = ["__pycache__", "*.pyc", "*.pyo", ".pytest_cache"]
        cleaned_items = 0
        
        for pattern in cache_patterns:
            if pattern.startswith("__"):
                # 目录
                for cache_dir in self.project_root.rglob(pattern):
                    if cache_dir.is_dir():
                        shutil.rmtree(cache_dir)
                        print(f"  🗑️ 删除缓存目录: {cache_dir.relative_to(self.project_root)}")
                        cleaned_items += 1
            else:
                # 文件
                for cache_file in self.project_root.rglob(pattern):
                    if cache_file.is_file():
                        cache_file.unlink()
                        print(f"  🗑️ 删除缓存文件: {cache_file.relative_to(self.project_root)}")
                        cleaned_items += 1
        
        # 清理空的日志目录
        logs_dir = self.project_root / "logs"
        if logs_dir.exists() and not any(logs_dir.iterdir()):
            print("  📂 logs目录为空，保持清洁状态")
        
        print(f"✅ 清理完成，删除了 {cleaned_items} 个缓存文件/目录")
    
    def check_dependencies(self):
        """检查依赖项状态"""
        print("🔍 检查项目依赖...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt 文件不存在")
            return
        
        try:
            # 检查虚拟环境
            venv_path = self.project_root / "venv"
            if venv_path.exists():
                print("✅ 虚拟环境存在")
                
                # 检查已安装的包
                result = subprocess.run(
                    [str(venv_path / "bin" / "pip"), "list", "--format=freeze"],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    installed_packages = result.stdout.strip().split('\n')
                    print(f"📦 已安装 {len(installed_packages)} 个包")
                else:
                    print("⚠️ 无法获取已安装包列表")
            else:
                print("❌ 虚拟环境不存在，建议运行: python -m venv venv")
                
        except Exception as e:
            print(f"❌ 检查依赖时出错: {e}")
    
    def validate_structure(self):
        """验证项目结构完整性"""
        print("🔍 验证项目结构...")
        
        required_structure = {
            "app": "目录",
            "app/main.py": "文件",
            "app/api": "目录", 
            "app/core": "目录",
            "app/crud": "目录",
            "app/schemas": "目录",
            "docs": "目录",
            "scripts": "目录",
            "requirements.txt": "文件",
            "README.md": "文件"
        }
        
        missing_items = []
        
        for item, item_type in required_structure.items():
            item_path = self.project_root / item
            
            if item_type == "目录" and not item_path.is_dir():
                missing_items.append(f"目录: {item}")
            elif item_type == "文件" and not item_path.is_file():
                missing_items.append(f"文件: {item}")
            else:
                print(f"  ✅ {item}")
        
        if missing_items:
            print("\n❌ 缺少以下项目:")
            for item in missing_items:
                print(f"  - {item}")
        else:
            print("\n🎉 项目结构完整！")
    
    def generate_summary(self):
        """生成项目摘要"""
        print("\n📊 项目摘要:")
        print("=" * 50)
        
        # 统计文件数量
        file_counts = {}
        for item in self.project_root.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                suffix = item.suffix.lower() or "无扩展名"
                file_counts[suffix] = file_counts.get(suffix, 0) + 1
        
        print("文件类型统计:")
        for suffix, count in sorted(file_counts.items()):
            print(f"  {suffix}: {count} 个文件")
        
        # 代码行数统计（仅Python文件）
        total_lines = 0
        python_files = 0
        for py_file in self.project_root.rglob("*.py"):
            if "venv" not in str(py_file) and "__pycache__" not in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        python_files += 1
                except:
                    pass
        
        print(f"\nPython代码统计:")
        print(f"  文件数: {python_files}")
        print(f"  总行数: {total_lines}")
        print(f"  平均行数: {total_lines // python_files if python_files > 0 else 0}")

def main():
    """主函数"""
    manager = ProjectManager()
    
    print("🚀 项目管理工具")
    print("=" * 50)
    
    actions = {
        "1": ("显示项目结构", manager.show_structure),
        "2": ("创建备份", manager.create_backup),
        "3": ("清理项目", manager.clean_project),
        "4": ("检查依赖", manager.check_dependencies),
        "5": ("验证结构", manager.validate_structure),
        "6": ("生成摘要", manager.generate_summary),
        "7": ("执行所有检查", lambda: [
            manager.validate_structure(),
            manager.check_dependencies(),
            manager.generate_summary()
        ])
    }
    
    print("可用操作:")
    for key, (description, _) in actions.items():
        print(f"  {key}. {description}")
    
    choice = input("\n请选择操作 (1-7, 默认7): ").strip() or "7"
    
    if choice in actions:
        print(f"\n执行: {actions[choice][0]}")
        print("-" * 30)
        actions[choice][1]()
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
