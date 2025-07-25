import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 从 .env 文件加载环境变量
load_dotenv()

# 从环境变量中获取 URL 和 Key
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# 检查是否成功加载了环境变量
if not url or not key:
    raise ValueError("Supabase URL 或 Key 未在 .env 文件中设置。")

# 创建客户端实例
try:
    supabase: Client = create_client(url, key)
    print("✅ 成功通过环境变量创建 Supabase 客户端！")
except Exception as e:
    print(f"❌ 创建客户端失败：{e}")


# --- 验证连接：执行一个简单查询 ---
# 假设你有一个名为 'countries' 的表
try:
    # 使用创建好的 supabase 对象进行查询
    response = supabase.table('countries').select("*").limit(3).execute()

    # 打印查询到的数据
    print("\n🚀 执行查询以验证连接...")
    print("查询成功，获取到数据：")
    print(response.data)

except Exception as e:
    print(f"❌ 查询失败：{e}")
    print("请检查：1. 表名是否正确。 2. 是否为该表设置了允许读取的 RLS 策略。")