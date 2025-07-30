#!/usr/bin/env python3
"""
数据库连接测试脚本
用于验证数据库配置是否正确
"""
import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings

async def test_database_connection():
    """测试数据库连接"""
    print("🔍 开始测试数据库连接...")
    print(f"📊 Supabase URL: {settings.SUPABASE_URL}")
    
    try:
        # 尝试获取 PostgreSQL 连接字符串
        postgres_url = settings.postgres_url
        print(f"🔗 PostgreSQL URL: {postgres_url[:50]}...")  # 只显示前50个字符保护敏感信息
        
        # 解析连接 URL 来检查各个组件
        from urllib.parse import urlparse
        parsed = urlparse(postgres_url)
        print(f"🏠 主机: {parsed.hostname}")
        print(f"🚪 端口: {parsed.port}")
        print(f"👤 用户: {parsed.username}")
        print(f"🗄️  数据库: {parsed.path.lstrip('/')}")
        
        # 先测试网络连接
        print("\n🌐 测试网络连接...")
        import socket
        try:
            sock = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
            sock.close()
            print("✅ 网络连接正常")
        except Exception as e:
            print(f"❌ 网络连接失败: {e}")
            print("💡 这可能是防火墙或网络问题")
            return False
        
        # 测试单个连接
        print("🔌 尝试建立单个数据库连接...")
        
        # 使用更详细的连接配置
        connection = await asyncpg.connect(
            postgres_url,
            timeout=30,  # 增加超时时间
            server_settings={
                'application_name': '启航引路人测试',
                'jit': 'off'
            }
        )
        
        # 执行简单查询
        result = await connection.fetchval("SELECT version()")
        print(f"✅ 连接成功！数据库版本: {result[:100]}...")
        
        # 测试表是否存在
        tables_result = await connection.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        if tables_result:
            print(f"📋 找到 {len(tables_result)} 个表:")
            for row in tables_result:
                print(f"   - {row['table_name']}")
        else:
            print("⚠️  数据库中没有找到表")
        
        await connection.close()
        
        # 测试连接池
        print("\n🏊 测试连接池...")
        pool = await asyncpg.create_pool(
            dsn=postgres_url,
            min_size=1,
            max_size=3,
            command_timeout=30,
            server_settings={'jit': 'off'},
            timeout=30,  # 增加连接池超时
        )
        
        # 测试连接池获取连接
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT 'Pool connection successful'")
            print(f"✅ 连接池测试成功: {result}")
        
        await pool.close()
        print("🎉 所有数据库连接测试通过！")
        return True
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return False
    except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
        print(f"❌ 认证失败: {e}")
        print("💡 请检查 SUPABASE_DB_PASSWORD 是否正确")
        return False
    except asyncpg.exceptions.CannotConnectNowError as e:
        print(f"❌ 服务器拒绝连接: {e}")
        print("💡 可能是网络问题或数据库服务器繁忙")
        return False
    except ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        print("💡 这通常表示网络连接问题或防火墙阻止")
        print("💡 建议检查:")
        print("   1. 网络连接是否正常")
        print("   2. Supabase 项目是否暂停")
        print("   3. 防火墙设置")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        
        # 如果是 SSL 相关错误，提供建议
        if 'ssl' in str(e).lower():
            print("💡 可能是 SSL 连接问题，尝试添加 SSL 参数")
        
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 启航引路人数据库连接测试")
    print("=" * 60)
    
    # 检查环境变量
    print("\n📝 检查环境变量:")
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY', 
        'SUPABASE_DB_PASSWORD'
    ]
    
    for var in required_vars:
        value = getattr(settings, var, None)
        if value:
            # 敏感信息只显示前几个字符
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = f"{value[:10]}..."
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: 未设置")
    
    # 运行连接测试
    success = await test_database_connection()
    
    if success:
        print("\n🎊 测试完成！数据库连接配置正确。")
        sys.exit(0)
    else:
        print("\n💥 测试失败！请检查数据库配置。")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
