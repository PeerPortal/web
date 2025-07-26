"""
数据库连接和状态检查脚本 - 新架构版本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings

def main():
    print("🔍 数据库连接检查")
    print("=" * 50)
    
    try:
        # 显示配置信息
        print(f"📊 数据库配置信息:")
        print(f"  🌐 项目URL: {settings.SUPABASE_URL}")
        print(f"  🔑 API Key: {settings.SUPABASE_KEY[:20]}...")
        
        if 'supabase.co' in settings.SUPABASE_URL:
            project_id = settings.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
            print(f"  🆔 项目ID: {project_id}")
        
        # 创建客户端
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print(f"  ✅ Supabase 客户端创建成功")
        
        print(f"\n📋 检查表结构:")
        tables_to_check = ['users', 'profiles', 'friends', 'messages', 'services', 'orders', 'reviews']
        
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table:10} 表存在")
                existing_tables.append(table)
            except Exception as e:
                if 'does not exist' in str(e).lower():
                    print(f"  ❌ {table:10} 表不存在")
                    missing_tables.append(table)
                else:
                    print(f"  ⚠️  {table:10} 检查出错: {str(e)[:50]}...")
        
        # 检查用户数据
        if 'users' in existing_tables:
            print(f"\n👥 用户数据统计:")
            try:
                # 获取用户总数
                users_result = supabase.table('users').select('id').execute()
                user_count = len(users_result.data)
                print(f"  📊 总用户数: {user_count}")
                
                # 显示最近的几个用户
                if user_count > 0:
                    recent_users = supabase.table('users').select('id, username, email, created_at').order('created_at', desc=True).limit(5).execute()
                    print(f"  📝 最近注册的用户:")
                    for user in recent_users.data:
                        print(f"    • {user['username']} ({user.get('email', '无邮箱')}) - {user.get('created_at', '')[:10]}")
                
            except Exception as e:
                print(f"  ❌ 获取用户数据失败: {e}")
        
        # 检查消息数据
        if 'messages' in existing_tables:
            print(f"\n💬 消息数据统计:")
            try:
                messages_result = supabase.table('messages').select('id').execute()
                message_count = len(messages_result.data)
                print(f"  📊 总消息数: {message_count}")
            except Exception as e:
                print(f"  ❌ 获取消息数据失败: {e}")
        
        # 总结
        print(f"\n📈 数据库状态总结:")
        print(f"  🟢 存在的表: {len(existing_tables)}/{len(tables_to_check)}")
        print(f"  🔴 缺失的表: {len(missing_tables)}")
        
        if missing_tables:
            print(f"\n💡 建议:")
            print(f"  1. 在 Supabase Dashboard 中执行 db_schema.sql")
            print(f"  2. 缺失的表: {', '.join(missing_tables)}")
            print(f"  3. SQL Editor 路径: https://supabase.com/dashboard/project/{project_id}/sql")
        else:
            print(f"\n🎉 所有必要的表都已存在！数据库准备就绪。")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    main() 