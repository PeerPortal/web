#!/usr/bin/env python3
"""
完整数据库检查脚本
检查所有表包括导师系统相关表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings

def main():
    print("🔍 完整数据库连接检查")
    print("=" * 50)

    try:
        print(f"📊 数据库配置信息:")
        print(f"  🌐 项目URL: {settings.SUPABASE_URL}")
        print(f"  🔑 API Key: {settings.SUPABASE_KEY[:20]}...")
        if 'supabase.co' in settings.SUPABASE_URL:
            project_id = settings.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
            print(f"  🆔 项目ID: {project_id}")

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print(f"  ✅ Supabase 客户端创建成功")

        # 完整的表列表（包含导师系统）
        all_tables = [
            # 基础用户系统
            'users', 'profiles', 'friends', 'messages',
            
            # 服务和交易系统
            'services', 'orders', 'reviews',
            
            # 导师系统
            'mentor_matches', 'mentorship_reviews', 
            'mentorship_sessions', 'mentorship_transactions',
            
            # 技能系统
            'skill_categories', 'skills',
            
            # 可用性系统  
            'user_availability'
        ]

        print(f"\n📋 检查完整表结构:")
        existing_tables = []
        missing_tables = []
        table_stats = {}

        for table in all_tables:
            try:
                result = supabase.table(table).select("*", count="exact").limit(1).execute()
                count = result.count
                existing_tables.append(table)
                table_stats[table] = count
                print(f"  ✅ {table:<25} | {count:>4} 行")
            except Exception as e:
                missing_tables.append(table)
                error_msg = str(e)[:50]
                print(f"  ❌ {table:<25} | 不存在: {error_msg}")

        # 按系统分类显示
        print(f"\n📊 按系统分类统计:")
        
        # 基础系统
        basic_tables = ['users', 'profiles', 'friends', 'messages']
        basic_count = sum(table_stats.get(t, 0) for t in basic_tables if t in existing_tables)
        print(f"  👥 基础用户系统: {len([t for t in basic_tables if t in existing_tables])}/{len(basic_tables)} 表, {basic_count} 条记录")
        
        # 服务系统
        service_tables = ['services', 'orders', 'reviews']
        service_count = sum(table_stats.get(t, 0) for t in service_tables if t in existing_tables)
        print(f"  🛍️  服务交易系统: {len([t for t in service_tables if t in existing_tables])}/{len(service_tables)} 表, {service_count} 条记录")
        
        # 导师系统
        mentor_tables = ['mentor_matches', 'mentorship_reviews', 'mentorship_sessions', 'mentorship_transactions']
        mentor_count = sum(table_stats.get(t, 0) for t in mentor_tables if t in existing_tables)
        print(f"  🎓 导师指导系统: {len([t for t in mentor_tables if t in existing_tables])}/{len(mentor_tables)} 表, {mentor_count} 条记录")
        
        # 技能系统
        skill_tables = ['skill_categories', 'skills']
        skill_count = sum(table_stats.get(t, 0) for t in skill_tables if t in existing_tables)
        print(f"  🛠️  技能管理系统: {len([t for t in skill_tables if t in existing_tables])}/{len(skill_tables)} 表, {skill_count} 条记录")
        
        # 可用性系统
        availability_tables = ['user_availability']
        availability_count = sum(table_stats.get(t, 0) for t in availability_tables if t in existing_tables)
        print(f"  📅 可用性系统: {len([t for t in availability_tables if t in existing_tables])}/{len(availability_tables)} 表, {availability_count} 条记录")

        # 用户数据详情
        if 'users' in existing_tables:
            print(f"\n👥 用户数据详情:")
            try:
                users_result = supabase.table('users').select(
                    'username, email, role, created_at'
                ).order('created_at', desc=True).limit(5).execute()
                
                print(f"  📊 总用户数: {table_stats['users']}")
                print(f"  📝 最近注册的用户:")
                for user in users_result.data:
                    created_date = user['created_at'][:10] if user.get('created_at') else 'Unknown'
                    role = user.get('role', 'user')
                    email_part = user.get('email', 'No email')[:30] if user.get('email') else 'No email'
                    print(f"    • {user['username']} ({email_part}) [{role}] - {created_date}")
            except Exception as e:
                print(f"  ❌ 获取用户详情失败: {e}")

        # 技能数据详情
        if 'skills' in existing_tables and table_stats.get('skills', 0) > 0:
            print(f"\n🛠️  技能数据详情:")
            try:
                skills_result = supabase.table('skills').select('*').limit(10).execute()
                print(f"  📊 技能总数: {table_stats['skills']}")
                print(f"  📝 技能示例:")
                for skill in skills_result.data[:5]:
                    skill_name = skill.get('name', 'Unknown')
                    category = skill.get('category_id', 'N/A')
                    print(f"    • {skill_name} (Category: {category})")
            except Exception as e:
                print(f"  ❌ 获取技能详情失败: {e}")

        print(f"\n📈 完整数据库状态总结:")
        print(f"  🟢 存在的表: {len(existing_tables)}/{len(all_tables)}")
        print(f"  🔴 缺失的表: {len(missing_tables)}")
        print(f"  📊 总记录数: {sum(table_stats.values())}")

        if missing_tables:
            print(f"\n⚠️  缺失的表:")
            for table in missing_tables:
                print(f"    • {table}")
            print(f"\n💡 建议:")
            print(f"  1. 这些表可能需要在 Supabase Dashboard 中创建")
            print(f"  2. 检查是否有权限访问这些表")
            print(f"  3. 联系团队成员确认表结构")
        else:
            print(f"\n🎉 所有表都已存在！数据库结构完整。")
            
        # 显示系统功能状态
        print(f"\n🚀 系统功能状态:")
        print(f"  {'✅' if len([t for t in basic_tables if t in existing_tables]) == len(basic_tables) else '⚠️'} 基础用户功能")
        print(f"  {'✅' if len([t for t in service_tables if t in existing_tables]) == len(service_tables) else '⚠️'} 服务交易功能")
        print(f"  {'✅' if len([t for t in mentor_tables if t in existing_tables]) == len(mentor_tables) else '⚠️'} 导师指导功能")
        print(f"  {'✅' if len([t for t in skill_tables if t in existing_tables]) == len(skill_tables) else '⚠️'} 技能管理功能")
        print(f"  {'✅' if len([t for t in availability_tables if t in existing_tables]) == len(availability_tables) else '⚠️'} 可用性功能")

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 