"""
API 接口测试脚本
"""
import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

def test_search_api():
    """测试搜索接口"""
    print("🔍 测试搜索接口...")
    
    try:
        # 测试基本搜索
        response = requests.get(f"{BASE_URL}/api/search")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 基本搜索成功，返回 {len(data)} 条记录")
            
            # 测试按学校搜索
            response = requests.get(f"{BASE_URL}/api/search?school=哈佛")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 学校搜索成功，返回 {len(data)} 条记录")
            
            # 测试按专业搜索
            response = requests.get(f"{BASE_URL}/api/search?major=计算机")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 专业搜索成功，返回 {len(data)} 条记录")
                
        else:
            print(f"❌ 搜索接口失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 搜索接口测试失败: {e}")

def test_register_api():
    """测试注册接口"""
    print("📝 测试注册接口...")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # 生成唯一的用户名
            timestamp = int(time.time() * 1000)  # 毫秒级时间戳
            random_num = random.randint(1000, 9999)
            test_user = {
                "username": f"test_user_{timestamp}_{random_num}",
                "password": "test_password_123"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/register",
                json=test_user,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"✅ 用户注册成功: {test_user['username']}")
                return test_user
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "未知错误")
                if "用户名已存在" in error_detail:
                    print(f"⚠️  用户名已存在，重试 ({attempt + 1}/{max_retries})")
                    time.sleep(0.1)  # 短暂等待
                    continue
                else:
                    print(f"❌ 用户注册失败: {response.status_code} - {error_detail}")
                    return None
            else:
                print(f"❌ 用户注册失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 注册接口测试失败: {e}")
            return None
    
    print(f"❌ 经过 {max_retries} 次重试后仍无法创建用户")
    return None

def test_login_api(user):
    """测试登录接口"""
    if not user:
        print("⚠️  跳过登录测试（没有有效用户）")
        return None
        
    print("🔐 测试登录接口...")
    
    try:
        # 登录数据需要使用 form data 格式
        login_data = {
            "username": user["username"],
            "password": user["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ 用户登录成功")
            print(f"  Token类型: {token_data.get('token_type')}")
            return token_data.get("access_token")
        else:
            print(f"❌ 用户登录失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 登录接口测试失败: {e}")
        return None

def test_docs_api():
    """测试文档接口"""
    print("📚 测试文档接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API 文档页面访问成功")
        else:
            print(f"❌ API 文档页面访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 文档接口测试失败: {e}")

def run_api_tests():
    """运行所有API测试"""
    print("🚀 开始 API 接口测试...")
    print("=" * 50)
    
    # 测试文档接口
    test_docs_api()
    
    # 测试搜索接口
    test_search_api()
    
    # 测试注册和登录
    user = test_register_api()
    token = test_login_api(user)
    
    if token:
        print(f"🎉 获得访问令牌: {token[:20]}...")
    
    print("\n✨ API 接口测试完成!")

if __name__ == "__main__":
    run_api_tests() 