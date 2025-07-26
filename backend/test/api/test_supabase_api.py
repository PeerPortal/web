#!/usr/bin/env python3
"""
Supabase REST API 测试脚本
验证通过 REST API 是否可以正常工作
"""
import asyncio
import httpx
from app.core.config import settings

async def test_supabase_rest_api():
    """测试 Supabase REST API 功能"""
    print("🌐 测试 Supabase REST API...")
    
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. 测试基本连接
            print("📡 测试基本 API 连接...")
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/",
                headers=headers,
                timeout=10
            )
            print(f"✅ API 连接成功，状态码: {response.status_code}")
            
            # 2. 测试获取表信息
            print("📋 获取表信息...")
            try:
                # 尝试获取用户表信息
                response = await client.get(
                    f"{settings.SUPABASE_URL}/rest/v1/users?limit=1",
                    headers=headers
                )
                if response.status_code == 200:
                    print("✅ 用户表可访问")
                    data = response.json()
                    print(f"   返回数据示例: {data}")
                else:
                    print(f"⚠️  用户表访问状态: {response.status_code} - 可能表不存在")
                    
            except Exception as e:
                print(f"⚠️  表访问测试失败: {e}")
            
            # 3. 测试健康检查端点
            print("🏥 测试健康检查...")
            try:
                response = await client.get(
                    f"{settings.SUPABASE_URL}/rest/v1/rpc/health",
                    headers=headers
                )
                print(f"   健康检查状态: {response.status_code}")
            except:
                print("   健康检查端点不可用（正常）")
            
            return True
            
    except Exception as e:
        print(f"❌ REST API 测试失败: {e}")
        return False

async def create_wake_up_request():
    """尝试唤醒暂停的 Supabase 项目"""
    print("\n💤 尝试唤醒 Supabase 项目...")
    
    headers = {
        "apikey": settings.SUPABASE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:  # 增加超时时间
            # 发送多个请求来唤醒项目
            for i in range(3):
                print(f"   请求 {i+1}/3...")
                response = await client.get(
                    f"{settings.SUPABASE_URL}/rest/v1/",
                    headers=headers
                )
                await asyncio.sleep(2)  # 等待2秒
                
            print("✅ 唤醒请求已发送")
            print("💡 请等待几分钟让项目完全启动，然后重试数据库连接")
            
    except Exception as e:
        print(f"❌ 唤醒请求失败: {e}")

async def main():
    """主函数"""
    print("🚀 Supabase REST API 测试和项目唤醒")
    print("=" * 60)
    
    # 测试 REST API
    rest_success = await test_supabase_rest_api()
    
    if rest_success:
        print("\n✅ REST API 工作正常")
        print("💡 建议:")
        print("   1. 应用可以在 REST API 降级模式下运行")
        print("   2. 如需直接数据库连接，请检查 Supabase 项目状态")
        
        # 尝试唤醒项目
        await create_wake_up_request()
        
    else:
        print("\n❌ REST API 也无法访问")
        print("💡 建议检查:")
        print("   1. SUPABASE_URL 是否正确")
        print("   2. SUPABASE_KEY 是否有效")
        print("   3. 网络连接是否正常")

if __name__ == "__main__":
    asyncio.run(main())
