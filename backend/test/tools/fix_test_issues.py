#!/usr/bin/env python3
"""
PeerPortal 测试问题诊断和修复脚本
解决常见的测试环境问题
"""
import subprocess
import sys
import os
from pathlib import Path

def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print('='*60)

def check_python_version():
    """检查Python版本"""
    print_section("检查Python版本")
    
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低！建议使用Python 3.8+")
        print("   请升级Python版本")
        return False
    else:
        print("✅ Python版本符合要求")
        return True

def check_asyncio():
    """检查asyncio模块"""
    print_section("检查asyncio模块")
    
    try:
        import asyncio
        print("✅ asyncio模块可用（Python内置模块）")
        print(f"   asyncio版本: {asyncio.__doc__.split()[0] if asyncio.__doc__ else '内置'}")
        return True
    except ImportError as e:
        print(f"❌ asyncio模块不可用: {e}")
        print("   这很不寻常，asyncio是Python 3.4+的内置模块")
        return False

def check_virtual_environment():
    """检查虚拟环境"""
    print_section("检查虚拟环境")
    
    venv = os.environ.get('VIRTUAL_ENV')
    if venv:
        print(f"✅ 虚拟环境已激活: {os.path.basename(venv)}")
        print(f"   路径: {venv}")
        return True
    else:
        print("⚠️  虚拟环境未激活")
        print("   建议激活虚拟环境: source venv/bin/activate")
        return False

def install_dependencies():
    """安装必要的依赖"""
    print_section("安装测试依赖")
    
    required_packages = [
        'httpx',
        'asyncpg',
        'fastapi',
        'uvicorn'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"🔄 安装 {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
                return False
    
    return True

def check_test_files():
    """检查测试文件是否存在"""
    print_section("检查测试文件")
    
    test_files = [
        'test_new_features.py',
        'test_database_tables.py',
        'run_feature_tests.sh'
    ]
    
    all_exist = True
    for file in test_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} 存在 ({size:,} bytes)")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False
    
    return all_exist

def check_server_status():
    """检查服务器状态"""
    print_section("检查服务器状态")
    
    try:
        import httpx
        response = httpx.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务器运行正常")
            return True
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("   请启动后端服务器: uvicorn app.main:app --reload")
        return False

def create_uploads_directory():
    """创建上传目录"""
    print_section("检查上传目录")
    
    upload_dirs = [
        'uploads',
        'uploads/avatars',
        'uploads/documents'
    ]
    
    for dir_path in upload_dirs:
        os.makedirs(dir_path, exist_ok=True)
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/ 目录已创建")
        else:
            print(f"❌ 无法创建 {dir_path}/ 目录")
            return False
    
    return True

def run_quick_test():
    """运行快速连接测试"""
    print_section("运行快速连接测试")
    
    try:
        import httpx
        import asyncio
        
        async def test_connection():
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 测试根端点
                response = await client.get("http://localhost:8000/")
                print(f"根端点: {response.status_code}")
                
                # 测试API文档
                response = await client.get("http://localhost:8000/docs")
                print(f"API文档: {response.status_code}")
                
                return True
        
        result = asyncio.run(test_connection())
        if result:
            print("✅ 连接测试通过")
            return True
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def fix_common_issues():
    """修复常见问题"""
    print_section("修复常见问题")
    
    fixes_applied = []
    
    # 1. 确保requirements.txt中没有asyncio
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        if 'asyncio' in content:
            print("🔄 从requirements.txt中移除asyncio...")
            new_content = '\n'.join(line for line in content.split('\n') 
                                   if not line.startswith('asyncio'))
            with open('requirements.txt', 'w') as f:
                f.write(new_content)
            fixes_applied.append("移除了requirements.txt中的asyncio")
    
    # 2. 确保脚本有执行权限
    script_file = 'run_feature_tests.sh'
    if os.path.exists(script_file):
        try:
            os.chmod(script_file, 0o755)
            fixes_applied.append(f"设置了{script_file}的执行权限")
        except Exception as e:
            print(f"⚠️  无法设置执行权限: {e}")
    
    if fixes_applied:
        print("✅ 应用的修复:")
        for fix in fixes_applied:
            print(f"   - {fix}")
    else:
        print("✅ 没有发现需要修复的问题")
    
    return True

def generate_diagnostic_report():
    """生成诊断报告"""
    print_section("生成诊断报告")
    
    report = []
    report.append("# PeerPortal 测试环境诊断报告")
    report.append(f"生成时间: {__import__('datetime').datetime.now()}")
    report.append("")
    
    # Python信息
    version = sys.version_info
    report.append(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    report.append(f"Python路径: {sys.executable}")
    
    # 虚拟环境信息
    venv = os.environ.get('VIRTUAL_ENV')
    report.append(f"虚拟环境: {venv if venv else '未激活'}")
    
    # 工作目录
    report.append(f"工作目录: {os.getcwd()}")
    
    # 测试文件状态
    report.append("\n## 测试文件状态")
    test_files = ['test_new_features.py', 'test_database_tables.py', 'run_feature_tests.sh']
    for file in test_files:
        exists = "✅" if os.path.exists(file) else "❌"
        size = f"({os.path.getsize(file):,} bytes)" if os.path.exists(file) else ""
        report.append(f"- {exists} {file} {size}")
    
    # 保存报告
    report_file = 'diagnostic_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"📄 诊断报告已保存: {report_file}")
    return True

def main():
    """主函数"""
    print("🚀 PeerPortal 测试环境诊断工具")
    print("本工具将检查并修复常见的测试环境问题")
    
    checks = [
        ("Python版本", check_python_version),
        ("asyncio模块", check_asyncio),
        ("虚拟环境", check_virtual_environment),
        ("测试文件", check_test_files),
        ("上传目录", create_uploads_directory),
        ("修复问题", fix_common_issues),
        ("安装依赖", install_dependencies),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name}检查失败: {e}")
            results[name] = False
    
    # 可选检查（需要服务器运行）
    print("\n" + "="*60)
    print("🌐 可选检查（需要服务器运行）")
    print("="*60)
    
    server_running = check_server_status()
    if server_running:
        run_quick_test()
    else:
        print("跳过连接测试，请先启动服务器")
    
    # 生成报告
    generate_diagnostic_report()
    
    # 总结
    print_section("诊断总结")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"检查通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有检查都通过了！")
        print("您现在可以运行测试:")
        print("   ./run_feature_tests.sh")
    else:
        print("⚠️  部分检查未通过，请解决以下问题:")
        for name, result in results.items():
            if not result:
                print(f"   ❌ {name}")
    
    if not server_running:
        print("\n💡 提示: 启动服务器后再次运行测试")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main() 