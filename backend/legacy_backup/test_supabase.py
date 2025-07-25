import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase

# 测试获取用户表数据
if __name__ == "__main__":
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        print("Supabase 连接成功，返回:", response.data)
    except Exception as e:
        print("Supabase 连接失败:", e) 