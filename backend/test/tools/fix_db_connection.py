#!/usr/bin/env python3
"""
Supabase 数据库连接修复脚本
尝试不同的连接方式来解决连接问题
"""
import asyncio
import asyncpg
import ssl
from app.core.config import settings

async def test_connection_variants():
    """测试不同的连接配置"""
    print("🔧 尝试不同的数据库连接配置...")
    
    base_url = f"postgresql://postgres:{settings.SUPABASE_DB_PASSWORD}@db.mbpqctxpzxehrevxlhfl.supabase.co:5432/postgres"
    
    # 测试配置列表
    test_configs = [
        {
            "name": "标准连接",
            "url": base_url,
            "ssl": None
        },
        {
            "name": "SSL要求连接", 
            "url": base_url + "?sslmode=require",
            "ssl": None
        },
        {
            "name": "SSL优先连接",
            "url": base_url + "?sslmode=prefer", 
            "ssl": None
        },
        {
            "name": "禁用SSL连接",
            "url": base_url + "?sslmode=disable",
            "ssl": None
        },
        {
            "name": "自定义SSL配置",
            "url": base_url,
            "ssl": ssl.create_default_context()
        }
    ]
    
    for config in test_configs:
        print(f"\n🧪 测试: {config['name']}")
        try:
            if config['ssl']:
                connection = await asyncpg.connect(
                    config['url'],
                    timeout=15,
                    ssl=config['ssl']
                )
            else:
                connection = await asyncpg.connect(
                    config['url'],
                    timeout=15
                )
            
            # 执行测试查询
            result = await connection.fetchval("SELECT 'Connection successful!'")
            print(f"✅ {config['name']} 成功: {result}")
            
            await connection.close()
            return config  # 返回成功的配置
            
        except Exception as e:
            print(f"❌ {config['name']} 失败: {e}")
            continue
    
    return None

async def check_supabase_project_status():
    """检查 Supabase 项目状态"""
    print("\n🔍 检查 Supabase 项目状态...")
    
    try:
        import httpx
        
        # 检查 Supabase API 是否可访问
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/",
                headers={"apikey": settings.SUPABASE_KEY},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Supabase REST API 可访问")
            else:
                print(f"⚠️  Supabase REST API 返回状态码: {response.status_code}")
                
    except ImportError:
        print("⚠️  未安装 httpx，跳过 API 检查")
    except Exception as e:
        print(f"❌ Supabase API 检查失败: {e}")

async def main():
    """主函数"""
    print("🚀 Supabase 数据库连接诊断和修复")
    print("=" * 60)
    
    # 检查项目状态
    await check_supabase_project_status()
    
    # 测试不同连接方式
    successful_config = await test_connection_variants()
    
    if successful_config:
        print(f"\n🎉 找到可用的连接配置: {successful_config['name']}")
        print("💡 建议更新你的数据库连接配置")
        
        # 生成建议的配置
        if "sslmode=" in successful_config['url']:
            ssl_param = successful_config['url'].split("?sslmode=")[1]
            print(f"📝 建议在连接字符串中添加: ?sslmode={ssl_param}")
        
    else:
        print("\n💥 所有连接配置都失败了！")
        print("🔧 建议的解决步骤:")
        print("1. 检查 Supabase 项目是否暂停（登录 Supabase 仪表板查看）")
        print("2. 验证数据库密码是否正确")
        print("3. 确认项目 ID 是否正确")
        print("4. 检查网络防火墙设置")
        print("5. 尝试重新启动 Supabase 项目")

if __name__ == "__main__":
    asyncio.run(main())
