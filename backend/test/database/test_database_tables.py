"""
PeerPortal 数据库表结构验证脚本
验证新增的数据库表是否正确创建
"""
import asyncio
import asyncpg
from typing import Dict, List, Optional
import os
from datetime import datetime

from app.core.config import settings

class DatabaseTableVerifier:
    """数据库表结构验证器"""
    
    def __init__(self):
        self.connection = None
        self.test_results = {}
        
    async def connect(self):
        """连接数据库"""
        print("🔗 连接数据库...")
        
        try:
            # 尝试获取数据库连接字符串
            postgres_url = settings.postgres_url
            print(f"📍 连接到: {postgres_url.split('@')[1] if '@' in postgres_url else 'localhost'}")
            
            self.connection = await asyncpg.connect(postgres_url)
            print("✅ 数据库连接成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            print("请检查数据库配置和网络连接")
            return False
    
    async def verify_table_exists(self, table_name: str) -> bool:
        """验证表是否存在"""
        try:
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
            """
            result = await self.connection.fetchval(query, table_name)
            return result
        except Exception as e:
            print(f"❌ 检查表 {table_name} 时出错: {e}")
            return False
    
    async def get_table_columns(self, table_name: str) -> List[Dict]:
        """获取表的列信息"""
        try:
            query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = $1
                ORDER BY ordinal_position
            """
            rows = await self.connection.fetch(query, table_name)
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ 获取表 {table_name} 列信息时出错: {e}")
            return []
    
    async def get_table_indexes(self, table_name: str) -> List[str]:
        """获取表的索引信息"""
        try:
            query = """
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = $1
                AND schemaname = 'public'
            """
            rows = await self.connection.fetch(query, table_name)
            return [row['indexname'] for row in rows]
        except Exception as e:
            print(f"❌ 获取表 {table_name} 索引信息时出错: {e}")
            return []
    
    async def verify_forum_tables(self):
        """验证论坛相关表"""
        print("\n🏛️ 验证论坛系统表...")
        results = {}
        
        # 1. 验证 forum_posts 表
        print("  📋 验证 forum_posts 表...")
        if await self.verify_table_exists("forum_posts"):
            print("  ✅ forum_posts 表存在")
            results["forum_posts_exists"] = "✅ 存在"
            
            # 检查列结构
            columns = await self.get_table_columns("forum_posts")
            expected_columns = [
                'id', 'title', 'content', 'author_id', 'category',
                'tags', 'replies_count', 'likes_count', 'views_count',
                'is_pinned', 'is_hot', 'created_at', 'updated_at', 'last_activity'
            ]
            
            column_names = [col['column_name'] for col in columns]
            missing_columns = set(expected_columns) - set(column_names)
            
            if not missing_columns:
                print("  ✅ forum_posts 表结构正确")
                results["forum_posts_structure"] = "✅ 正确"
            else:
                print(f"  ❌ forum_posts 表缺少列: {missing_columns}")
                results["forum_posts_structure"] = f"❌ 缺少: {missing_columns}"
            
            # 检查索引
            indexes = await self.get_table_indexes("forum_posts")
            print(f"  📇 索引数量: {len(indexes)}")
            results["forum_posts_indexes"] = f"✅ {len(indexes)} 个索引"
            
        else:
            print("  ❌ forum_posts 表不存在")
            results["forum_posts_exists"] = "❌ 不存在"
        
        # 2. 验证 forum_replies 表
        print("  💬 验证 forum_replies 表...")
        if await self.verify_table_exists("forum_replies"):
            print("  ✅ forum_replies 表存在")
            results["forum_replies_exists"] = "✅ 存在"
            
            columns = await self.get_table_columns("forum_replies")
            expected_columns = [
                'id', 'post_id', 'content', 'author_id', 'parent_id',
                'likes_count', 'created_at', 'updated_at'
            ]
            
            column_names = [col['column_name'] for col in columns]
            missing_columns = set(expected_columns) - set(column_names)
            
            if not missing_columns:
                print("  ✅ forum_replies 表结构正确")
                results["forum_replies_structure"] = "✅ 正确"
            else:
                print(f"  ❌ forum_replies 表缺少列: {missing_columns}")
                results["forum_replies_structure"] = f"❌ 缺少: {missing_columns}"
                
        else:
            print("  ❌ forum_replies 表不存在")
            results["forum_replies_exists"] = "❌ 不存在"
        
        # 3. 验证 forum_likes 表
        print("  👍 验证 forum_likes 表...")
        if await self.verify_table_exists("forum_likes"):
            print("  ✅ forum_likes 表存在")
            results["forum_likes_exists"] = "✅ 存在"
        else:
            print("  ❌ forum_likes 表不存在")
            results["forum_likes_exists"] = "❌ 不存在"
        
        self.test_results["forum_tables"] = results
        return results
    
    async def verify_message_tables(self):
        """验证消息相关表"""
        print("\n💬 验证消息系统表...")
        results = {}
        
        # 验证 messages 表
        print("  📨 验证 messages 表...")
        if await self.verify_table_exists("messages"):
            print("  ✅ messages 表存在")
            results["messages_exists"] = "✅ 存在"
            
            # 检查列结构
            columns = await self.get_table_columns("messages")
            expected_columns = [
                'id', 'conversation_id', 'sender_id', 'recipient_id',
                'content', 'message_type', 'status', 'is_read',
                'created_at', 'updated_at', 'read_at'
            ]
            
            column_names = [col['column_name'] for col in columns]
            missing_columns = set(expected_columns) - set(column_names)
            
            if not missing_columns:
                print("  ✅ messages 表结构正确")
                results["messages_structure"] = "✅ 正确"
            else:
                print(f"  ❌ messages 表缺少列: {missing_columns}")
                results["messages_structure"] = f"❌ 缺少: {missing_columns}"
            
            # 检查索引
            indexes = await self.get_table_indexes("messages")
            print(f"  📇 索引数量: {len(indexes)}")
            results["messages_indexes"] = f"✅ {len(indexes)} 个索引"
            
        else:
            print("  ❌ messages 表不存在")
            results["messages_exists"] = "❌ 不存在"
        
        self.test_results["message_tables"] = results
        return results
    
    async def verify_file_tables(self):
        """验证文件相关表"""
        print("\n📁 验证文件系统表...")
        results = {}
        
        # 验证 uploaded_files 表
        print("  📄 验证 uploaded_files 表...")
        if await self.verify_table_exists("uploaded_files"):
            print("  ✅ uploaded_files 表存在")
            results["uploaded_files_exists"] = "✅ 存在"
            
            # 检查列结构
            columns = await self.get_table_columns("uploaded_files")
            expected_columns = [
                'id', 'file_id', 'user_id', 'filename', 'original_filename',
                'file_path', 'file_url', 'file_size', 'content_type',
                'file_type', 'description', 'created_at', 'updated_at'
            ]
            
            column_names = [col['column_name'] for col in columns]
            missing_columns = set(expected_columns) - set(column_names)
            
            if not missing_columns:
                print("  ✅ uploaded_files 表结构正确")
                results["uploaded_files_structure"] = "✅ 正确"
            else:
                print(f"  ❌ uploaded_files 表缺少列: {missing_columns}")
                results["uploaded_files_structure"] = f"❌ 缺少: {missing_columns}"
            
        else:
            print("  ❌ uploaded_files 表不存在")
            results["uploaded_files_exists"] = "❌ 不存在"
        
        self.test_results["file_tables"] = results
        return results
    
    async def verify_triggers(self):
        """验证触发器"""
        print("\n⚡ 验证数据库触发器...")
        results = {}
        
        try:
            # 检查触发器
            query = """
                SELECT trigger_name, event_object_table
                FROM information_schema.triggers
                WHERE trigger_schema = 'public'
                AND trigger_name IN (
                    'trigger_update_post_replies_count',
                    'trigger_update_likes_count'
                )
            """
            triggers = await self.connection.fetch(query)
            
            trigger_names = [trigger['trigger_name'] for trigger in triggers]
            
            if 'trigger_update_post_replies_count' in trigger_names:
                print("  ✅ 回复数量更新触发器存在")
                results["replies_count_trigger"] = "✅ 存在"
            else:
                print("  ❌ 回复数量更新触发器不存在")
                results["replies_count_trigger"] = "❌ 不存在"
            
            if 'trigger_update_likes_count' in trigger_names:
                print("  ✅ 点赞数量更新触发器存在")
                results["likes_count_trigger"] = "✅ 存在"
            else:
                print("  ❌ 点赞数量更新触发器不存在")
                results["likes_count_trigger"] = "❌ 不存在"
                
        except Exception as e:
            print(f"  ❌ 检查触发器时出错: {e}")
            results["trigger_check"] = f"❌ 错误: {e}"
        
        self.test_results["triggers"] = results
        return results
    
    async def verify_views(self):
        """验证视图"""
        print("\n👁️ 验证数据库视图...")
        results = {}
        
        try:
            # 检查视图
            query = """
                SELECT table_name
                FROM information_schema.views
                WHERE table_schema = 'public'
                AND table_name IN (
                    'forum_posts_with_author',
                    'forum_replies_with_author',
                    'message_conversations'
                )
            """
            views = await self.connection.fetch(query)
            view_names = [view['table_name'] for view in views]
            
            expected_views = [
                'forum_posts_with_author',
                'forum_replies_with_author', 
                'message_conversations'
            ]
            
            for view_name in expected_views:
                if view_name in view_names:
                    print(f"  ✅ 视图 {view_name} 存在")
                    results[f"{view_name}_exists"] = "✅ 存在"
                else:
                    print(f"  ❌ 视图 {view_name} 不存在")
                    results[f"{view_name}_exists"] = "❌ 不存在"
                    
        except Exception as e:
            print(f"  ❌ 检查视图时出错: {e}")
            results["view_check"] = f"❌ 错误: {e}"
        
        self.test_results["views"] = results
        return results
    
    async def test_basic_operations(self):
        """测试基本数据库操作"""
        print("\n🧪 测试基本数据库操作...")
        results = {}
        
        # 测试插入和查询操作
        try:
            # 如果tables存在，测试基本插入操作
            if await self.verify_table_exists("forum_posts"):
                print("  📝 测试论坛帖子插入...")
                
                # 注意：这里只是测试表结构，不会实际插入数据
                # 因为需要有效的外键引用（author_id -> users表）
                
                # 检查是否可以查询
                count_query = "SELECT COUNT(*) FROM forum_posts"
                count = await self.connection.fetchval(count_query)
                print(f"  📊 当前帖子数量: {count}")
                results["forum_posts_query"] = "✅ 可查询"
            
            if await self.verify_table_exists("messages"):
                print("  💬 测试消息表查询...")
                count_query = "SELECT COUNT(*) FROM messages"
                count = await self.connection.fetchval(count_query)
                print(f"  📊 当前消息数量: {count}")
                results["messages_query"] = "✅ 可查询"
                
        except Exception as e:
            print(f"  ❌ 数据库操作测试出错: {e}")
            results["basic_operations"] = f"❌ 错误: {e}"
        
        self.test_results["basic_operations"] = results
        return results
    
    async def generate_report(self):
        """生成验证报告"""
        print("\n📊 生成数据库验证报告...")
        
        report_data = {
            "verification_time": datetime.now().isoformat(),
            "test_results": self.test_results,
            "summary": {}
        }
        
        # 统计结果
        total_checks = 0
        passed_checks = 0
        
        for category, checks in self.test_results.items():
            for check_name, result in checks.items():
                total_checks += 1
                if result.startswith("✅"):
                    passed_checks += 1
        
        report_data["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "success_rate": f"{(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "0%"
        }
        
        # 保存报告
        report_filename = f"database_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 验证报告已保存: {report_filename}")
        
        # 打印摘要
        print("\n📈 验证摘要:")
        print(f"  总检查项: {total_checks}")
        print(f"  通过检查: {passed_checks}")
        print(f"  失败检查: {total_checks - passed_checks}")
        print(f"  成功率: {report_data['summary']['success_rate']}")
        
        # 打印详细结果
        print("\n📋 详细验证结果:")
        for category, checks in self.test_results.items():
            print(f"  📂 {category}:")
            for check_name, result in checks.items():
                print(f"    {check_name}: {result}")
        
        return report_data
    
    async def cleanup(self):
        """清理连接"""
        if self.connection:
            await self.connection.close()
    
    async def run_verification(self):
        """运行完整验证"""
        print("🔍 开始数据库表结构验证")
        print("=" * 50)
        
        # 连接数据库
        if not await self.connect():
            print("❌ 数据库连接失败，终止验证")
            return
        
        try:
            # 运行各项验证
            await self.verify_forum_tables()
            await self.verify_message_tables()
            await self.verify_file_tables()
            await self.verify_triggers()
            await self.verify_views()
            await self.test_basic_operations()
            
            # 生成报告
            await self.generate_report()
            
        finally:
            await self.cleanup()
        
        print("\n🎉 数据库验证完成！")

async def main():
    """主函数"""
    verifier = DatabaseTableVerifier()
    await verifier.run_verification()

if __name__ == "__main__":
    asyncio.run(main()) 