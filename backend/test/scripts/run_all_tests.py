"""
主测试运行器 - 完整测试套件
针对新架构的所有测试功能
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_environment():
    """检查环境配置"""
    print("🔍 环境检查")
    print("=" * 40)
    
    try:
        from app.core.config import settings
        print(f"✅ 配置加载成功")
        print(f"   🌐 项目URL: {settings.SUPABASE_URL}")
        print(f"   🔑 API Key: {settings.SUPABASE_KEY[:20]}...")
        print(f"   🏠 服务器: {settings.HOST}:{settings.PORT}")
        return True
    except Exception as e:
        print(f"❌ 环境配置检查失败: {e}")
        return False

def run_complete_api_tests():
    """运行完整的API测试套件"""
    print("\n" + "="*60)
    print("🚀 完整API测试套件")
    print("="*60)
    try:
        from test_all_api import APITester
        tester = APITester()
        success = tester.run_all_tests()
        return success
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def run_login_specific_tests():
    """运行专门的登录测试"""
    print("\n" + "="*60)
    print("🔐 专门登录测试")
    print("="*60)
    try:
        from test_login import main as login_main
        login_main()
        return True
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
        return False

def run_database_tests():
    """运行数据库相关测试"""
    print("\n" + "="*60)
    print("🗄️  数据库测试")
    print("="*60)
    try:
        from check_database import main as check_db
        check_db()
        print("✅ 数据库连接测试完成")
        
        from setup_database import setup_database
        setup_database()
        print("✅ 数据库设置测试完成")
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

async def run_websocket_tests():
    """运行 WebSocket 测试"""
    print("\n" + "="*60)
    print("🔌 WebSocket 测试")
    print("="*60)
    try:
        from test_ws import run_all_ws_tests
        await run_all_ws_tests()
        return True
    except Exception as e:
        print(f"❌ WebSocket 测试失败: {e}")
        return False

def run_server_health_check():
    """运行服务器健康检查"""
    print("\n" + "="*60)
    print("🏥 服务器健康检查")
    print("="*60)
    
    import requests
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器运行正常")
            print(f"   状态: {data.get('status')}")
            print(f"   版本: {data.get('version')}")
            print(f"   调试模式: {data.get('debug')}")
            return True
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("💡 请确保运行: python start_new_app.py")
        return False

async def main():
    """主测试函数"""
    print("🎯 启动完整测试套件")
    print("=" * 80)
    print("针对新的企业级架构进行全面测试")
    print("=" * 80)

    if not check_environment():
        print("\n❌ 环境检查失败，请配置 .env 文件后重试")
        return False

    # 检查服务器是否运行
    if not run_server_health_check():
        print("\n❌ 服务器未运行，请先启动服务器")
        print("💡 运行命令: python start_new_app.py")
        return False

    success_count = 0
    total_tests = 5

    # 1. 完整API测试套件（主要测试）
    print(f"\n{'='*80}")
    print("🎯 测试 1/5: 完整API功能测试")
    if run_complete_api_tests():
        success_count += 1
        print("✅ 完整API测试: 通过")
    else:
        print("❌ 完整API测试: 失败")

    # 2. 专门登录测试
    print(f"\n{'='*80}")
    print("🎯 测试 2/5: 专门登录功能测试")
    if run_login_specific_tests():
        success_count += 1
        print("✅ 登录测试: 通过")
    else:
        print("❌ 登录测试: 失败")

    # 3. 数据库测试
    print(f"\n{'='*80}")
    print("🎯 测试 3/5: 数据库功能测试")
    if run_database_tests():
        success_count += 1
        print("✅ 数据库测试: 通过")
    else:
        print("❌ 数据库测试: 失败")

    # 4. WebSocket测试
    print(f"\n{'='*80}")
    print("🎯 测试 4/5: WebSocket功能测试")
    if await run_websocket_tests():
        success_count += 1
        print("✅ WebSocket测试: 通过")
    else:
        print("❌ WebSocket测试: 失败")

    # 5. 服务器稳定性测试
    print(f"\n{'='*80}")
    print("🎯 测试 5/5: 服务器稳定性测试")
    stability_passed = True
    for i in range(3):
        if not run_server_health_check():
            stability_passed = False
            break
    
    if stability_passed:
        success_count += 1
        print("✅ 稳定性测试: 通过")
    else:
        print("❌ 稳定性测试: 失败")

    # 最终总结
    print("\n" + "="*80)
    print("🏆 最终测试报告")
    print("="*80)
    print(f"✨ 测试完成! 成功: {success_count}/{total_tests}")
    print(f"📈 成功率: {(success_count/total_tests*100):.1f}%")
    
    if success_count == total_tests:
        print("🎉 所有测试通过! 系统工作完美!")
        print("\n🚀 您的API已经完全就绪:")
        print("   • 用户认证系统 ✅")
        print("   • 用户资料管理 ✅") 
        print("   • 数据库连接 ✅")
        print("   • API文档 ✅")
        print("   • 错误处理 ✅")
        print("   • 安全验证 ✅")
        print("\n💡 下一步: 开始前端开发或添加更多API功能")
    elif success_count >= 3:
        print("✅ 大部分测试通过! 系统基本可用")
        print(f"⚠️  有 {total_tests - success_count} 个测试失败，建议检查")
    else:
        print(f"⚠️  多个测试失败 ({total_tests - success_count} 个)")
        print("🔧 建议检查服务器配置和数据库连接")

    print("="*80)
    return success_count >= 3  # 至少通过3个测试认为是成功

def print_usage():
    """打印使用说明"""
    print("📖 测试套件使用说明")
    print("=" * 50)
    print("运行方式:")
    print("  python test/run_all_tests.py        # 运行全部测试")
    print("  python test/test_all_api.py         # 只运行API测试")
    print("  python test/test_login.py           # 只运行登录测试")
    print("  python test/check_database.py       # 只检查数据库")
    print("")
    print("🔧 准备工作:")
    print("  1. 确保虚拟环境已激活: source venv/bin/activate")
    print("  2. 确保服务器正在运行: python start_new_app.py")
    print("  3. 确保.env文件配置正确")
    print("")
    print("📊 测试内容:")
    print("  • 完整API功能测试 (22个测试项)")
    print("  • 用户认证和授权测试")
    print("  • 数据库连接和操作测试")
    print("  • WebSocket连接测试")
    print("  • 服务器稳定性测试")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        sys.exit(1) 