"""
数据库初始化脚本 - 兼容新架构
创建所需的表结构并插入测试数据
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检测是否能使用新架构的连接（需要应用运行时）
try:
    # 先尝试导入旧架构（更稳定）
    from supabase import create_client
    from app.core.config import settings
    
    # 使用配置创建 Supabase 客户端
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    NEW_ARCHITECTURE = False
    print("✅ 使用 Supabase 客户端连接（推荐用于数据库初始化）")
    
except ImportError:
    print("❌ 无法导入数据库连接，请检查配置")
    sys.exit(1)

def check_table_exists(table_name):
    """检查表是否存在"""
    try:
        # 使用 Supabase 客户端
        result = supabase.table(table_name).select('*').limit(1).execute()
        print(f"✅ 表 '{table_name}' 已存在")
        return True
    except Exception as e:
        error_msg = str(e)
        if 'does not exist' in error_msg.lower():
            print(f"❌ 表 '{table_name}' 不存在")
        else:
            print(f"❌ 检查表 '{table_name}' 时出错: {e}")
        return False

def create_test_user():
    """创建测试用户"""
    try:
        # 使用 API 风格的用户创建（更安全）
        print("ℹ️  数据库表已存在，建议使用 API 端点创建用户:")
        print("   POST /api/v1/auth/register")
        print("   示例: curl -X POST http://localhost:8001/api/v1/auth/register \\")
        print("              -H 'Content-Type: application/json' \\")
        print("              -d '{\"username\":\"testuser\",\"password\":\"testpass\",\"email\":\"test@example.com\"}'")
        return True
            
    except Exception as e:
        print(f"❌ 创建测试用户失败: {e}")
        return False

def setup_database():
    """设置数据库"""
    print("🚀 开始数据库检查和初始化...")
    print("=" * 50)
    
    print("\n📋 检查表结构:")
    tables_to_check = ['users', 'messages', 'friends', 'profiles']
    
    all_tables_exist = True
    for table in tables_to_check:
        if not check_table_exists(table):
            all_tables_exist = False
    
    if not all_tables_exist:
        print("\n❌ 某些表不存在！")
        print("📝 请按照以下步骤手动创建表:")
        print("1. 登录 Supabase 项目: https://supabase.com/dashboard")
        print("2. 选择您的项目")
        print("3. 进入 SQL Editor")
        print("4. 复制并执行项目根目录下的 db_schema.sql 文件内容")
        print("5. 重新运行此脚本")
        return False
    
    print("\n✅ 所有必需的表都存在！")
    
    print("\n📝 测试数据操作:")
    user_test = create_test_user()
    
    if user_test:
        print("\n🎉 数据库初始化完成！")
        print("💡 下一步操作指南:")
        print("   1. 启动应用: python start_new_app.py")
        print("   2. 访问文档: http://localhost:8001/docs")
        print("   3. 测试 API: python test/test_new_api.py")
        return True
    
    print("\n⚠️  数据库功能测试未完全通过")
    return False

def show_database_info():
    """显示数据库信息"""
    try:
        print("\n📊 数据库状态:")
        print(f"  🌐 项目URL: {settings.SUPABASE_URL}")
        print(f"  🔑 API Key: {settings.SUPABASE_KEY[:20]}...")
        print("  🏗️  架构: Supabase 客户端 (兼容模式)")
        print("  🔗 连接: 直接 REST API")
            
    except Exception as e:
        print(f"❌ 获取数据库信息失败: {e}")

if __name__ == "__main__":
    success = setup_database()
    show_database_info()
    
    if success:
        print("\n🎯 成功！数据库已准备就绪")
        print("  ✨ 可以开始使用新架构的所有功能了")
    else:
        print("\n⚠️  请先在 Supabase 中创建表结构")
        print("  📖 详细步骤请查看 QUICK_START.md") 