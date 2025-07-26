"""
修复后的学生CRUD操作 - 匹配实际的 user_learning_needs 表结构
"""
from typing import Optional, List
from app.core.supabase_client import get_supabase_client
from app.schemas.student_schema import StudentCreate, StudentProfile, StudentUpdate
from datetime import datetime, timedelta

class StudentCRUD:
    def __init__(self):
        self.table = "user_learning_needs"
    
    async def get_student_profile(self, user_id: int) -> Optional[dict]:
        """获取申请者资料"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters={"user_id": user_id}
            )
            if response and len(response) > 0:
                return response[0]
            return None
        except Exception as e:
            print(f"获取申请者资料失败: {e}")
            return None
    
    async def create_student_profile(self, user_id: int, student_data: StudentCreate) -> Optional[dict]:
        """创建申请者资料"""
        try:
            print(f"🔧 开始创建申请者资料，用户ID: {user_id}")
            supabase_client = await get_supabase_client()
            print(f"✅ 获取Supabase客户端成功")
            
            # 构建符合数据库表结构的数据
            create_data = {
                "user_id": user_id,
                "urgency_level": student_data.urgency_level,
                "budget_min": student_data.budget_min,
                "budget_max": student_data.budget_max,
                "description": student_data.description,
                "learning_goals": student_data.learning_goals,
                "preferred_format": student_data.preferred_format,
                "currency": "CNY",
                "current_level": 1,
                "target_level": 2,
                "is_active": True,
                "expires_at": (datetime.now() + timedelta(days=90)).isoformat()  # 3个月后过期
            }
            
            print(f"📤 准备插入数据: {create_data}")
            
            response = await supabase_client.insert(
                table=self.table,
                data=create_data
            )
            
            print(f"📥 数据库响应: {response}")
            
            if response:
                print(f"✅ 创建成功: {response}")
                return response
            
            print("❌ 响应为空或无数据")
            return None
            
        except Exception as e:
            print(f"💥 创建申请者资料失败，详细错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def update_student_profile(self, user_id: int, student_data: StudentUpdate) -> Optional[dict]:
        """更新申请者资料"""
        try:
            supabase_client = await get_supabase_client()
            # 构建更新数据
            update_data = {}
            if student_data.urgency_level is not None:
                update_data["urgency_level"] = student_data.urgency_level
            if student_data.budget_min is not None:
                update_data["budget_min"] = student_data.budget_min
            if student_data.budget_max is not None:
                update_data["budget_max"] = student_data.budget_max
            if student_data.description is not None:
                update_data["description"] = student_data.description
            if student_data.learning_goals is not None:
                update_data["learning_goals"] = student_data.learning_goals
            if student_data.preferred_format is not None:
                update_data["preferred_format"] = student_data.preferred_format
            if student_data.current_level is not None:
                update_data["current_level"] = student_data.current_level
            if student_data.target_level is not None:
                update_data["target_level"] = student_data.target_level
            
            if not update_data:
                return None
                
            update_data["updated_at"] = datetime.now().isoformat()
            
            response = await supabase_client.update(
                table=self.table,
                data=update_data,  
                filters={"user_id": user_id}
            )
            
            if response and len(response) > 0:
                return response[0]
            return None
            
        except Exception as e:
            print(f"更新申请者资料失败: {e}")
            return None
    
    async def delete_student_profile(self, user_id: int) -> bool:
        """删除申请者资料"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.delete(
                table=self.table,
                filters={"user_id": user_id}
            )
            return response is not None
        except Exception as e:
            print(f"删除申请者资料失败: {e}")
            return False
    
    async def search_students(self, 
                            search_query: Optional[str] = None,
                            limit: int = 20,
                            offset: int = 0) -> List[dict]:
        """搜索申请者"""
        try:
            supabase_client = await get_supabase_client()
            filters = {"is_active": True}
            
            # 如果有搜索查询，可以在这里添加搜索逻辑
            # 目前简单返回所有活跃的申请者
            
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            return response or []
            
        except Exception as e:
            print(f"搜索申请者失败: {e}")
            return []

# 创建全局实例
student_crud = StudentCRUD()
