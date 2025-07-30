#!/usr/bin/env python3
"""
启航引路人平台 - 数据库连接和功能测试
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.core.config import settings
    from app.core.supabase_client import get_supabase_client
    from app.core.db import check_db_health, is_db_pool_available
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)

class DatabaseTester:
    def __init__(self):
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }
    
    def log_test(self, name: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.results['total'] += 1
        status = "✅ PASS" if success else "❌ FAIL"
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
        
        result = f"{status} | {name}"
        if details:
            result += f" | {details}"
        
        self.results['details'].append(result)
        print(result)
    
    async def test_environment_config(self):
        """测试环境配置"""
        print("🔧 测试环境配置")
        print("-" * 50)
        
        # 检查必要的环境变量
        required_vars = [
            ('SUPABASE_URL', settings.SUPABASE_URL),
            ('SUPABASE_KEY', settings.SUPABASE_KEY),
            ('SUPABASE_DB_PASSWORD', getattr(settings, 'SUPABASE_DB_PASSWORD', None))
        ]
        
        for var_name, var_value in required_vars:
            if var_value:
                # 敏感信息只显示前几个字符
                if 'PASSWORD' in var_name or 'KEY' in var_name:
                    display_value = f"{var_value[:10]}..." if len(var_value) > 10 else "***"
                else:
                    display_value = var_value
                self.log_test(f"环境变量 {var_name}", True, display_value)
            else:
                self.log_test(f"环境变量 {var_name}", False, "未设置")
    
    async def test_database_connection_pool(self):
        """测试数据库连接池"""
        print("\n🏊 测试数据库连接池")
        print("-" * 50)
        
        # 检查连接池状态
        pool_available = is_db_pool_available()
        self.log_test("数据库连接池可用性", pool_available, 
                     "连接池已初始化" if pool_available else "使用降级模式")
        
        # 如果连接池可用，测试健康检查
        if pool_available:
            try:
                health_status = await check_db_health()
                self.log_test("数据库健康检查", health_status, 
                             "连接正常" if health_status else "连接异常")
            except Exception as e:
                self.log_test("数据库健康检查", False, f"错误: {str(e)}")
    
    async def test_supabase_rest_api(self):
        """测试 Supabase REST API"""
        print("\n🌐 测试 Supabase REST API")
        print("-" * 50)
        
        try:
            client = await get_supabase_client()
            self.log_test("Supabase 客户端初始化", True, "客户端创建成功")
            
            # 测试查询用户表
            try:
                users = await client.select("users", "*", limit=1)
                self.log_test("用户表查询", True, f"查询成功，返回 {len(users)} 条记录")
            except Exception as e:
                self.log_test("用户表查询", False, f"查询失败: {str(e)}")
            
            # 测试查询其他重要表
            important_tables = [
                "services", "profiles", "skill_categories", 
                "mentorship_relationships", "reviews"
            ]
            
            for table in important_tables:
                try:
                    data = await client.select(table, "*", limit=1)
                    self.log_test(f"{table}表查询", True, f"返回 {len(data)} 条记录")
                except Exception as e:
                    # 表不存在或查询失败都记录，但不算严重错误
                    self.log_test(f"{table}表查询", False, f"查询失败: {str(e)}")
            
        except Exception as e:
            self.log_test("Supabase 客户端初始化", False, f"初始化失败: {str(e)}")
    
    async def test_database_operations(self):
        """测试数据库基本操作"""
        print("\n💾 测试数据库基本操作")
        print("-" * 50)
        
        try:
            client = await get_supabase_client()
            
            # 测试插入操作（使用临时数据）
            test_data = {
                "username": f"test_user_{int(asyncio.get_event_loop().time())}",
                "email": f"test_{int(asyncio.get_event_loop().time())}@test.com",
                "password_hash": "test_hash",
                "role": "student",
                "is_active": True
            }
            
            try:
                # 插入测试数据
                inserted_user = await client.insert("users", test_data)
                if inserted_user:
                    user_id = inserted_user.get('id')
                    self.log_test("数据插入操作", True, f"插入用户ID: {user_id}")
                    
                    # 测试查询刚插入的数据
                    if user_id:
                        try:
                            queried_user = await client.select(
                                "users", "*", {"id": user_id}, limit=1
                            )
                            if queried_user:
                                self.log_test("数据查询操作", True, f"查询到用户: {queried_user[0].get('username')}")
                            else:
                                self.log_test("数据查询操作", False, "未查询到刚插入的数据")
                        except Exception as e:
                            self.log_test("数据查询操作", False, f"查询失败: {str(e)}")
                        
                        # 测试更新操作
                        try:
                            updated_data = {"is_active": False}
                            updated_user = await client.update(
                                "users", {"id": user_id}, updated_data
                            )
                            if updated_user:
                                self.log_test("数据更新操作", True, "更新成功")
                            else:
                                self.log_test("数据更新操作", False, "更新失败")
                        except Exception as e:
                            self.log_test("数据更新操作", False, f"更新失败: {str(e)}")
                        
                        # 清理测试数据
                        try:
                            await client.delete("users", {"id": user_id})
                            self.log_test("测试数据清理", True, "清理成功")
                        except Exception as e:
                            self.log_test("测试数据清理", False, f"清理失败: {str(e)}")
                    
                else:
                    self.log_test("数据插入操作", False, "插入返回空结果")
                    
            except Exception as e:
                self.log_test("数据插入操作", False, f"插入失败: {str(e)}")
                
        except Exception as e:
            self.log_test("数据库基本操作", False, f"客户端获取失败: {str(e)}")
    
    async def test_database_schema(self):
        """测试数据库表结构"""
        print("\n🗄️ 测试数据库表结构")
        print("-" * 50)
        
        try:
            client = await get_supabase_client()
            
            # 预期的数据库表
            expected_tables = [
                "users", "profiles", "friends", "messages",
                "mentor_matches", "mentorship_relationships", 
                "mentorship_reviews", "mentorship_sessions", 
                "mentorship_transactions", "services", "orders", 
                "reviews", "skill_categories", "skills", "user_skills",
                "user_availability", "user_credit_logs", 
                "user_learning_needs", "user_reputation_stats", 
                "user_unavailable_periods", "user_wallets"
            ]
            
            existing_tables = []
            missing_tables = []
            
            for table in expected_tables:
                try:
                    # 尝试查询表（限制1条记录以减少开销）
                    await client.select(table, "*", limit=1)
                    existing_tables.append(table)
                except Exception:
                    missing_tables.append(table)
            
            self.log_test("数据库表结构检查", True, 
                         f"存在 {len(existing_tables)}/{len(expected_tables)} 个表")
            
            if missing_tables:
                self.log_test("缺失的表", False, f"缺失: {', '.join(missing_tables[:5])}" + 
                             (f" 等{len(missing_tables)}个表" if len(missing_tables) > 5 else ""))
            else:
                self.log_test("所有表都存在", True, "数据库结构完整")
                
        except Exception as e:
            self.log_test("数据库表结构检查", False, f"检查失败: {str(e)}")
    
    async def run_all_tests(self):
        """运行所有数据库测试"""
        print("🗄️ 启航引路人 - 数据库测试套件")
        print("=" * 60)
        
        try:
            await self.test_environment_config()
            await self.test_database_connection_pool()
            await self.test_supabase_rest_api()
            await self.test_database_operations()
            await self.test_database_schema()
            
            # 输出测试结果
            self.print_summary()
            
        except Exception as e:
            print(f"❌ 测试执行失败: {str(e)}")
            return False
        
        return self.results['failed'] == 0
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 60)
        print("📊 数据库测试结果总结")
        print("=" * 60)
        print(f"总测试数: {self.results['total']}")
        print(f"通过: {self.results['passed']} ✅")
        print(f"失败: {self.results['failed']} ❌")
        print(f"成功率: {(self.results['passed'] / self.results['total'] * 100):.1f}%")
        print("=" * 60)
        
        if self.results['failed'] > 0:
            print("❌ 失败的测试:")
            for detail in self.results['details']:
                if "❌ FAIL" in detail:
                    print(f"  {detail}")

async def main():
    """主函数"""
    tester = DatabaseTester()
    success = await tester.run_all_tests()
    
    if success:
        print("🎉 所有数据库测试通过！")
        sys.exit(0)
    else:
        print("💥 部分测试失败，请检查数据库配置")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
