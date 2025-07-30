#!/usr/bin/env python3
"""
启航引路人平台 - 快速健康检查
验证系统基本功能是否正常
"""
import os
import sys
import requests
import time
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*20} {title} {'='*20}")

def check_environment():
    """检查环境配置"""
    print_header("环境检查")
    
    # 检查 .env 文件
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env 文件存在")
        
        # 读取关键配置
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SECRET_KEY']
        for var in required_vars:
            if var in content and not content.split(f'{var}=')[1].split('\n')[0].strip().startswith('#'):
                print(f"✅ {var} 已配置")
            else:
                print(f"❌ {var} 未配置或被注释")
    else:
        print("❌ .env 文件不存在")
        return False
    
    # 检查必要文件
    important_files = [
        'app/main.py',
        'app/core/db.py',
        'app/core/supabase_client.py',
        'requirements.txt'
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} 存在")
        else:
            print(f"❌ {file_path} 不存在")
    
    return True

def check_server():
    """检查服务器状态"""
    print_header("服务器检查")
    
    try:
        # 检查健康端点
        response = requests.get("http://localhost:8001/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            print(f"   响应时间: {response.elapsed.total_seconds():.3f}s")
            
            try:
                data = response.json()
                print(f"   状态: {data.get('status', 'unknown')}")
                print(f"   时间: {data.get('timestamp', 'unknown')}")
            except:
                print(f"   响应内容: {response.text}")
            
            return True
        else:
            print(f"❌ 服务器响应异常: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 (localhost:8001)")
        print("💡 请运行: ./start_server.sh 或 python -m uvicorn app.main:app --port 8001")
        return False
    except requests.exceptions.Timeout:
        print("❌ 服务器响应超时")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False

def check_api_endpoints():
    """检查关键API端点"""
    print_header("API端点检查")
    
    endpoints = [
        ("/", "根路径"),
        ("/docs", "API文档"),
        ("/health", "健康检查"),
        ("/api/v1/users/me", "用户信息 (需要认证)")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"http://localhost:8001{endpoint}", timeout=5)
            
            if endpoint == "/api/v1/users/me":
                # 这个端点需要认证，401是预期的
                if response.status_code == 401:
                    print(f"✅ {description}: 正确返回401 (需要认证)")
                    results.append(True)
                else:
                    print(f"⚠️ {description}: 返回 {response.status_code} (预期401)")
                    results.append(False)
            else:
                if response.status_code in [200, 307, 308]:  # 允许重定向
                    print(f"✅ {description}: HTTP {response.status_code}")
                    results.append(True)
                else:
                    print(f"❌ {description}: HTTP {response.status_code}")
                    results.append(False)
                    
        except Exception as e:
            print(f"❌ {description}: {str(e)}")
            results.append(False)
    
    return all(results)

def check_database():
    """检查数据库连接"""
    print_header("数据库检查")
    
    try:
        # 尝试导入配置
        sys.path.append('.')
        from app.core.config import settings
        
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            print("✅ Supabase 配置已加载")
            
            # 使用简单的HTTP请求测试连接
            try:
                # 测试健康端点或者基础API访问
                import requests
                
                # 构建健康检查URL
                health_url = f"{settings.SUPABASE_URL}/rest/v1/"
                headers = {
                    "apikey": settings.SUPABASE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_KEY}"
                }
                
                response = requests.get(health_url, headers=headers, timeout=10)
                
                if response.status_code in [200, 404]:  # 404也表示连接正常，只是路径问题
                    print("✅ Supabase REST API 连接正常")
                    return True
                elif response.status_code == 401:
                    print("❌ Supabase API 密钥认证失败")
                    return False
                else:
                    print(f"⚠️ Supabase API 响应异常: HTTP {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Supabase 连接失败: {str(e)}")
                return False
        else:
            print("❌ Supabase 配置不完整")
            return False
            
    except ImportError as e:
        print(f"❌ 无法导入必要模块: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 数据库检查失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 启航引路人平台 - 快速健康检查")
    print("=" * 60)
    
    # 记录开始时间
    start_time = time.time()
    
    # 执行检查
    checks = [
        ("环境配置", check_environment),
        ("服务器状态", check_server),
        ("API端点", check_api_endpoints),
        ("数据库连接", check_database)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}检查异常: {str(e)}")
            results.append((name, False))
    
    # 汇总结果
    print_header("检查汇总")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} | {name}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    elapsed = time.time() - start_time
    
    print(f"\n📊 结果统计:")
    print(f"   检查项目: {total}")
    print(f"   通过项目: {passed}")
    print(f"   成功率: {success_rate:.1f}%")
    print(f"   耗时: {elapsed:.2f}s")
    
    if passed == total:
        print("\n🎉 所有检查都通过！系统运行正常。")
        print("\n💡 接下来可以:")
        print("   - 访问 http://localhost:8001/docs 查看API文档")
        print("   - 运行 python run_comprehensive_tests.py 进行详细测试")
        print("   - 开始使用平台功能")
        return True
    else:
        print(f"\n⚠️ {total - passed} 项检查失败，建议:")
        
        # 给出具体建议
        failed_checks = [name for name, result in results if not result]
        
        if "服务器状态" in failed_checks:
            print("   - 启动服务器: ./start_server.sh")
        if "环境配置" in failed_checks:
            print("   - 检查并配置 .env 文件")
        if "数据库连接" in failed_checks:
            print("   - 验证 Supabase 配置是否正确")
        if "API端点" in failed_checks:
            print("   - 确保服务器正常运行且端口未被占用")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
