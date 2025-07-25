#!/usr/bin/env python3
"""
完全完整的数据库检查脚本
检查所有21个表，包括从截图发现的所有表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings

def main():
    print("🔍 完全完整的数据库连接检查 (更新版)")
    print("=" * 60)

    try:
        print(f"📊 数据库配置信息:")
        print(f"  🌐 项目URL: {settings.SUPABASE_URL}")
        print(f"  🔑 API Key: {settings.SUPABASE_KEY[:20]}...")
        if 'supabase.co' in settings.SUPABASE_URL:
            project_id = settings.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
            print(f"  🆔 项目ID: {project_id}")

        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print(f"  ✅ Supabase 客户端创建成功")

        # 所有21个表的完整列表（根据用户最新反馈更新）
        all_tables = [
            # 基础用户系统
            'users', 'profiles', 'friends', 'messages',
            
            # 服务和交易系统  
            'services', 'orders', 'reviews',
            
            # 导师系统（表名已更正）
            'mentor_matches',              # 导师学员匹配记录表
            'mentorship_relationships',    # 指导关系表 (30列!) - 正确表名
            'mentorship_reviews',          # 指导关系评价表
            'mentorship_sessions',         # 指导会话记录表
            'mentorship_transactions',     # 交易记录表 - 用户特别提到
            
            # 技能系统
            'skill_categories',            # 技能分类表
            'skills',                      # 具体技能表
            
            # 用户扩展系统（从截图新发现的）
            'user_availability',           # 用户可用时间表
            'user_credit_logs',            # 积分记录表
            'user_learning_needs',         # 用户学习需求表
            'user_reputation_stats',       # 用户信誉统计表
            'user_skills',                 # 用户技能表（导师能力）
            'user_unavailable_periods',    # 用户不可用时间段表 - 用户特别提到
            'user_wallets'                 # 用户钱包表
        ]

        print(f"\n📋 检查完整的21个表结构 (表名已更正):")
        existing_tables = []
        missing_tables = []
        permission_issues = []
        table_stats = {}
        table_columns = {}

        # 特别标记用户提到的表
        user_mentioned_tables = ['mentorship_transactions', 'user_unavailable_periods', 'mentorship_relationships']

        for table in all_tables:
            marker = "🔥" if table in user_mentioned_tables else "  "
            try:
                result = supabase.table(table).select("*", count="exact").limit(1).execute()
                count = result.count
                existing_tables.append(table)
                table_stats[table] = count
                
                # 获取字段数量
                columns_count = 0
                if result.data:
                    columns_count = len(result.data[0].keys())
                table_columns[table] = columns_count
                
                status_icon = "🟢" if table in user_mentioned_tables else "✅"
                print(f"{marker}{status_icon} {table:<25} | {count:>4} 行 | {columns_count:>2} 字段")
                
            except Exception as e:
                error_msg = str(e)
                if 'relation' in error_msg and 'does not exist' in error_msg:
                    missing_tables.append(table)
                    status_icon = "🔴" if table in user_mentioned_tables else "❌"
                    print(f"{marker}{status_icon} {table:<25} | 表不存在")
                elif 'permission' in error_msg.lower():
                    permission_issues.append(table)
                    status_icon = "🔒" if table in user_mentioned_tables else "🔒"
                    print(f"{marker}{status_icon} {table:<25} | 权限不足")
                else:
                    permission_issues.append(table)
                    status_icon = "⚠️" if table in user_mentioned_tables else "⚠️"
                    print(f"{marker}{status_icon} {table:<25} | 访问问题: {error_msg[:30]}...")

        # 特别检查用户提到的表
        print(f"\n🔥 用户特别关注的表状态:")
        for table in user_mentioned_tables:
            if table in existing_tables:
                count = table_stats.get(table, 0)
                columns = table_columns.get(table, 0)
                print(f"  ✅ {table:<25} | {count:>4} 行 | {columns:>2} 字段")
            elif table in missing_tables:
                print(f"  ❌ {table:<25} | 表不存在")
            elif table in permission_issues:
                print(f"  🔒 {table:<25} | 访问问题")

        # 按功能系统分类统计
        print(f"\n📊 按功能系统分类统计:")
        
        # 基础用户系统
        basic_tables = ['users', 'profiles', 'friends', 'messages']
        basic_existing = [t for t in basic_tables if t in existing_tables]
        basic_count = sum(table_stats.get(t, 0) for t in basic_existing)
        print(f"  👥 基础用户系统: {len(basic_existing)}/{len(basic_tables)} 表, {basic_count} 条记录")
        
        # 服务交易系统
        service_tables = ['services', 'orders', 'reviews']
        service_existing = [t for t in service_tables if t in existing_tables]
        service_count = sum(table_stats.get(t, 0) for t in service_existing)
        print(f"  🛍️  服务交易系统: {len(service_existing)}/{len(service_tables)} 表, {service_count} 条记录")
        
        # 导师指导系统 (已更正表名)
        mentor_tables = ['mentor_matches', 'mentorship_relationships', 'mentorship_reviews', 
                        'mentorship_sessions', 'mentorship_transactions']
        mentor_existing = [t for t in mentor_tables if t in existing_tables]
        mentor_count = sum(table_stats.get(t, 0) for t in mentor_existing)
        print(f"  🎓 导师指导系统: {len(mentor_existing)}/{len(mentor_tables)} 表, {mentor_count} 条记录")
        
        # 技能管理系统
        skill_tables = ['skill_categories', 'skills', 'user_skills']
        skill_existing = [t for t in skill_tables if t in existing_tables]
        skill_count = sum(table_stats.get(t, 0) for t in skill_existing)
        print(f"  🛠️  技能管理系统: {len(skill_existing)}/{len(skill_tables)} 表, {skill_count} 条记录")
        
        # 用户扩展系统（积分、钱包、信誉等）
        extended_tables = ['user_availability', 'user_credit_logs', 'user_learning_needs',
                          'user_reputation_stats', 'user_unavailable_periods', 'user_wallets']
        extended_existing = [t for t in extended_tables if t in existing_tables]
        extended_count = sum(table_stats.get(t, 0) for t in extended_existing)
        print(f"  💎 用户扩展系统: {len(extended_existing)}/{len(extended_tables)} 表, {extended_count} 条记录")

        # 显示表字段详情（重点表）
        important_tables = ['users', 'mentorship_relationships', 'user_skills', 'skill_categories', 'mentorship_transactions']
        print(f"\n🔍 重点表详情:")
        for table in important_tables:
            if table in existing_tables:
                columns = table_columns.get(table, 0)
                rows = table_stats.get(table, 0)
                marker = "🔥" if table in user_mentioned_tables else "  "
                print(f"{marker}📊 {table:<25} | {rows:>3} 行 | {columns:>2} 字段")
                
                # 如果有数据，显示一些示例
                if rows > 0:
                    try:
                        sample = supabase.table(table).select('*').limit(2).execute()
                        if sample.data:
                            print(f"     示例字段: {list(sample.data[0].keys())[:5]}...")
                    except:
                        pass

        # 数据总结
        total_tables = len(all_tables)
        accessible_tables = len(existing_tables)
        total_records = sum(table_stats.values())
        
        print(f"\n📈 完整数据库状态总结:")
        print(f"  🟢 可访问的表: {accessible_tables}/{total_tables}")
        print(f"  🔴 缺失的表: {len(missing_tables)}")
        print(f"  🔒 权限问题: {len(permission_issues)}")
        print(f"  📊 总记录数: {total_records}")
        print(f"  🔢 总字段数: {sum(table_columns.values())}")

        # 显示问题表
        if missing_tables:
            print(f"\n❌ 缺失的表:")
            for table in missing_tables:
                marker = "🔥" if table in user_mentioned_tables else "  "
                print(f"  {marker}• {table}")
                
        if permission_issues:
            print(f"\n🔒 权限或访问问题的表:")
            for table in permission_issues:
                marker = "🔥" if table in user_mentioned_tables else "  "
                print(f"  {marker}• {table}")

        # 系统功能状态
        print(f"\n🚀 系统功能完整度:")
        basic_status = "✅" if len(basic_existing) == len(basic_tables) else f"⚠️ {len(basic_existing)}/{len(basic_tables)}"
        service_status = "✅" if len(service_existing) == len(service_tables) else f"⚠️ {len(service_existing)}/{len(service_tables)}"
        mentor_status = "✅" if len(mentor_existing) == len(mentor_tables) else f"⚠️ {len(mentor_existing)}/{len(mentor_tables)}"
        skill_status = "✅" if len(skill_existing) == len(skill_tables) else f"⚠️ {len(skill_existing)}/{len(skill_tables)}"
        extended_status = "✅" if len(extended_existing) == len(extended_tables) else f"⚠️ {len(extended_existing)}/{len(extended_tables)}"
        
        print(f"  {basic_status} 基础用户功能")
        print(f"  {service_status} 服务交易功能")
        print(f"  {mentor_status} 导师指导功能")
        print(f"  {skill_status} 技能管理功能")
        print(f"  {extended_status} 用户扩展功能（积分/钱包/信誉）")

        # 数据活跃度分析
        active_tables = [t for t in existing_tables if table_stats.get(t, 0) > 0]
        print(f"\n📊 数据活跃度:")
        print(f"  🟢 有数据的表: {len(active_tables)}/{len(existing_tables)}")
        print(f"  🔥 最活跃的表:")
        sorted_tables = sorted(table_stats.items(), key=lambda x: x[1], reverse=True)
        for table, count in sorted_tables[:5]:
            if count > 0:
                marker = "🔥" if table in user_mentioned_tables else "  "
                print(f"   {marker}• {table}: {count} 条记录")

        if accessible_tables >= 18:  # 至少85%的表可访问
            print(f"\n🎉 数据库结构基本完整！您拥有功能完备的导师匹配平台！")
        else:
            print(f"\n⚠️  数据库结构不完整，建议检查缺失的表。")

        # 特别提醒用户关注的表
        user_table_status = [t for t in user_mentioned_tables if t in existing_tables]
        print(f"\n🔥 用户关注表状态: {len(user_table_status)}/{len(user_mentioned_tables)} 可访问")

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 