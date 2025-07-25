"""
修复后的导师CRUD操作 - 匹配实际的 mentorship_relationships 表结构
"""
from typing import Optional, List
from app.core.supabase_client import get_supabase_client
from app.schemas.mentor_schema import MentorCreate, MentorProfile, MentorUpdate
from datetime import datetime

class MentorCRUD:
    def __init__(self):
        self.table = "mentorship_relationships"
    
    async def get_mentor_profile(self, mentor_id: int) -> Optional[dict]:
        """获取指导者资料"""
        try:
            supabase_client = await get_supabase_client()
            supabase_client = await get_supabase_client()
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters={"mentor_id": mentor_id}
            )
            if response and len(response) > 0:
                return response[0]
            return None
        except Exception as e:
            print(f"获取指导者资料失败: {e}")
            return None
    
    async def create_mentor_profile(self, mentor_id: int, mentor_data: MentorCreate) -> Optional[dict]:
        """创建指导者资料"""
        try:
            supabase_client = await get_supabase_client()
            supabase_client = await get_supabase_client()
            # 构建符合数据库表结构的数据
            create_data = {
                "mentor_id": mentor_id,
                "title": mentor_data.title,
                "description": mentor_data.description,
                "learning_goals": mentor_data.learning_goals,
                "hourly_rate": float(mentor_data.hourly_rate) if mentor_data.hourly_rate else None,
                "session_duration_minutes": mentor_data.session_duration_minutes,
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "currency": "CNY",
                "payment_schedule": "per_session",
                "relationship_type": "guidance",
                "status": "active",
                "sessions_completed": 0,
                "total_hours_spent": 0.0
            }
            
            response = await supabase_client.insert(
                table=self.table,
                data=create_data
            )
            
            if response:
                return response
            return None
            
        except Exception as e:
            print(f"创建指导者资料失败: {e}")
            return None
    
    async def update_mentor_profile(self, mentor_id: int, mentor_data: MentorUpdate) -> Optional[dict]:
        """更新指导者资料"""
        try:
            supabase_client = await get_supabase_client()
            # 构建更新数据
            update_data = {}
            if mentor_data.title is not None:
                update_data["title"] = mentor_data.title
            if mentor_data.description is not None:
                update_data["description"] = mentor_data.description
            if mentor_data.learning_goals is not None:
                update_data["learning_goals"] = mentor_data.learning_goals
            if mentor_data.hourly_rate is not None:
                update_data["hourly_rate"] = float(mentor_data.hourly_rate)
            if mentor_data.session_duration_minutes is not None:
                update_data["session_duration_minutes"] = mentor_data.session_duration_minutes
            
            if not update_data:
                return None
                
            update_data["updated_at"] = datetime.now().isoformat()
            
            response = await supabase_client.update(
                table=self.table,
                data=update_data,
                filters={"mentor_id": mentor_id}
            )
            
            if response and len(response) > 0:
                return response[0]
            return None
            
        except Exception as e:
            print(f"更新指导者资料失败: {e}")
            return None
    
    async def delete_mentor_profile(self, mentor_id: int) -> bool:
        """删除指导者资料"""
        try:
            supabase_client = await get_supabase_client()
            response = await supabase_client.delete(
                table=self.table,
                filters={"mentor_id": mentor_id}
            )
            return response is not None
        except Exception as e:
            print(f"删除指导者资料失败: {e}")
            return False
    
    async def search_mentors(self, 
                           search_query: Optional[str] = None,
                           limit: int = 20,
                           offset: int = 0) -> List[dict]:
        """搜索指导者"""
        try:
            supabase_client = await get_supabase_client()
            filters = {"status": "active"}
            
            # 如果有搜索查询，可以在这里添加搜索逻辑
            # 目前简单返回所有活跃的指导者
            
            response = await supabase_client.select(
                table=self.table,
                columns="*",
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            return response or []
            
        except Exception as e:
            print(f"搜索指导者失败: {e}")
            return []

# 创建全局实例
mentor_crud = MentorCRUD()
