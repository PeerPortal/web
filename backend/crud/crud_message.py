"""
消息系统的数据库操作
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.schemas.message_schema import (
    MessageCreate, MessageUpdate, Message, ConversationCreate,
    ConversationListItem, MessageType, MessageStatus
)

class MessageCRUD:
    """消息CRUD操作类"""
    
    async def create_message(self, db_conn: Tuple[Any, str], sender_id: int, message_data: MessageCreate) -> Optional[Message]:
        """创建新消息"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                # PostgreSQL 实现
                query = """
                    INSERT INTO messages (conversation_id, sender_id, recipient_id, content, message_type, status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    RETURNING id, conversation_id, sender_id, recipient_id, content, message_type, status, is_read, created_at, updated_at, read_at
                """
                now = datetime.now()
                result = await connection.fetchrow(
                    query,
                    message_data.conversation_id,
                    sender_id,
                    message_data.recipient_id,
                    message_data.content,
                    message_data.message_type.value,
                    MessageStatus.sent.value,
                    now,
                    now
                )
                
                if result:
                    return Message(
                        id=result['id'],
                        conversation_id=result['conversation_id'],
                        sender_id=result['sender_id'],
                        recipient_id=result['recipient_id'],
                        content=result['content'],
                        message_type=MessageType(result['message_type']),
                        status=MessageStatus(result['status']),
                        is_read=result['is_read'],
                        created_at=result['created_at'],
                        updated_at=result['updated_at'],
                        read_at=result['read_at']
                    )
                    
            else:
                # Supabase 实现
                now = datetime.now().isoformat()
                result = await connection.table("messages").insert({
                    "conversation_id": message_data.conversation_id,
                    "sender_id": sender_id,
                    "recipient_id": message_data.recipient_id,
                    "content": message_data.content,
                    "message_type": message_data.message_type.value,
                    "status": MessageStatus.sent.value,
                    "created_at": now,
                    "updated_at": now
                }).execute()
                
                if result.data:
                    msg_data = result.data[0]
                    return Message(
                        id=msg_data['id'],
                        conversation_id=msg_data['conversation_id'],
                        sender_id=msg_data['sender_id'],
                        recipient_id=msg_data['recipient_id'],
                        content=msg_data['content'],
                        message_type=MessageType(msg_data['message_type']),
                        status=MessageStatus(msg_data['status']),
                        is_read=msg_data.get('is_read', False),
                        created_at=datetime.fromisoformat(msg_data['created_at']),
                        updated_at=datetime.fromisoformat(msg_data['updated_at']),
                        read_at=datetime.fromisoformat(msg_data['read_at']) if msg_data.get('read_at') else None
                    )
                    
        except Exception as e:
            print(f"创建消息失败: {e}")
            
        return None
    
    async def get_messages(self, db_conn: Tuple[Any, str], user_id: int, 
                          limit: int = 20, offset: int = 0) -> List[Message]:
        """获取用户的消息列表"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                query = """
                    SELECT id, conversation_id, sender_id, recipient_id, content, 
                           message_type, status, is_read, created_at, updated_at, read_at
                    FROM messages 
                    WHERE sender_id = $1 OR recipient_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2 OFFSET $3
                """
                results = await connection.fetch(query, user_id, limit, offset)
                
                return [
                    Message(
                        id=row['id'],
                        conversation_id=row['conversation_id'],
                        sender_id=row['sender_id'],
                        recipient_id=row['recipient_id'],
                        content=row['content'],
                        message_type=MessageType(row['message_type']),
                        status=MessageStatus(row['status']),
                        is_read=row['is_read'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        read_at=row['read_at']
                    )
                    for row in results
                ]
                
            else:
                # Supabase 实现
                result = await connection.table("messages").select("*").or_(
                    f"sender_id.eq.{user_id},recipient_id.eq.{user_id}"
                ).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
                
                if result.data:
                    return [
                        Message(
                            id=msg['id'],
                            conversation_id=msg['conversation_id'],
                            sender_id=msg['sender_id'],
                            recipient_id=msg['recipient_id'],
                            content=msg['content'],
                            message_type=MessageType(msg['message_type']),
                            status=MessageStatus(msg['status']),
                            is_read=msg.get('is_read', False),
                            created_at=datetime.fromisoformat(msg['created_at']),
                            updated_at=datetime.fromisoformat(msg['updated_at']),
                            read_at=datetime.fromisoformat(msg['read_at']) if msg.get('read_at') else None
                        )
                        for msg in result.data
                    ]
                    
        except Exception as e:
            print(f"获取消息列表失败: {e}")
            
        return []
    
    async def get_conversations(self, db_conn: Tuple[Any, str], user_id: int, 
                               limit: int = 20) -> List[ConversationListItem]:
        """获取用户的对话列表"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                # 获取对话列表的复杂查询
                query = """
                    WITH conversation_users AS (
                        SELECT DISTINCT 
                            CASE 
                                WHEN sender_id = $1 THEN recipient_id 
                                ELSE sender_id 
                            END as other_user_id,
                            MAX(created_at) as last_message_time
                        FROM messages 
                        WHERE sender_id = $1 OR recipient_id = $1
                        GROUP BY other_user_id
                    ),
                    latest_messages AS (
                        SELECT DISTINCT ON (
                            CASE 
                                WHEN sender_id = $1 THEN recipient_id 
                                ELSE sender_id 
                            END
                        )
                        id, content, created_at,
                        CASE 
                            WHEN sender_id = $1 THEN recipient_id 
                            ELSE sender_id 
                        END as other_user_id
                        FROM messages 
                        WHERE sender_id = $1 OR recipient_id = $1
                        ORDER BY other_user_id, created_at DESC
                    )
                    SELECT 
                        cu.other_user_id,
                        u.username,
                        u.avatar_url,
                        u.role,
                        lm.content as last_message,
                        cu.last_message_time,
                        COALESCE(unread.count, 0) as unread_count
                    FROM conversation_users cu
                    JOIN users u ON u.id = cu.other_user_id
                    LEFT JOIN latest_messages lm ON lm.other_user_id = cu.other_user_id
                    LEFT JOIN (
                        SELECT 
                            sender_id,
                            COUNT(*) as count
                        FROM messages 
                        WHERE recipient_id = $1 AND is_read = false
                        GROUP BY sender_id
                    ) unread ON unread.sender_id = cu.other_user_id
                    ORDER BY cu.last_message_time DESC
                    LIMIT $2
                """
                results = await connection.fetch(query, user_id, limit)
                
                conversations = []
                for row in results:
                    # 根据角色判断是导师还是学生
                    if row['role'] == 'mentor':
                        conversations.append(ConversationListItem(
                            conversation_id=row['other_user_id'],  # 临时使用用户ID作为对话ID
                            mentor_id=row['other_user_id'],
                            mentor_name=row['username'],
                            mentor_avatar=row['avatar_url'],
                            last_message=row['last_message'],
                            last_message_time=row['last_message_time'],
                            unread_count=row['unread_count'],
                            is_online=False  # TODO: 实现在线状态
                        ))
                    else:
                        conversations.append(ConversationListItem(
                            conversation_id=row['other_user_id'],
                            student_id=row['other_user_id'],
                            student_name=row['username'],
                            student_avatar=row['avatar_url'],
                            last_message=row['last_message'],
                            last_message_time=row['last_message_time'],
                            unread_count=row['unread_count'],
                            is_online=False
                        ))
                
                return conversations
                
            else:
                # Supabase 实现 - 简化版本
                # 这里需要复杂的子查询，暂时返回基础数据
                return []
                
        except Exception as e:
            print(f"获取对话列表失败: {e}")
            
        return []
    
    async def get_conversation_messages(self, db_conn: Tuple[Any, str], 
                                      conversation_id: int, user_id: int,
                                      limit: int = 50, offset: int = 0) -> List[Message]:
        """获取对话中的消息"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                # 基于用户ID获取双方的消息
                query = """
                    SELECT id, conversation_id, sender_id, recipient_id, content, 
                           message_type, status, is_read, created_at, updated_at, read_at
                    FROM messages 
                    WHERE (sender_id = $1 AND recipient_id = $2) 
                       OR (sender_id = $2 AND recipient_id = $1)
                    ORDER BY created_at ASC
                    LIMIT $3 OFFSET $4
                """
                results = await connection.fetch(query, user_id, conversation_id, limit, offset)
                
                return [
                    Message(
                        id=row['id'],
                        conversation_id=row['conversation_id'] or 0,
                        sender_id=row['sender_id'],
                        recipient_id=row['recipient_id'],
                        content=row['content'],
                        message_type=MessageType(row['message_type']),
                        status=MessageStatus(row['status']),
                        is_read=row['is_read'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        read_at=row['read_at']
                    )
                    for row in results
                ]
                
            else:
                # Supabase 实现
                result = await connection.table("messages").select("*").or_(
                    f"and(sender_id.eq.{user_id},recipient_id.eq.{conversation_id}),"
                    f"and(sender_id.eq.{conversation_id},recipient_id.eq.{user_id})"
                ).order("created_at", desc=False).range(offset, offset + limit - 1).execute()
                
                if result.data:
                    return [
                        Message(
                            id=msg['id'],
                            conversation_id=msg.get('conversation_id', 0),
                            sender_id=msg['sender_id'],
                            recipient_id=msg['recipient_id'],
                            content=msg['content'],
                            message_type=MessageType(msg['message_type']),
                            status=MessageStatus(msg['status']),
                            is_read=msg.get('is_read', False),
                            created_at=datetime.fromisoformat(msg['created_at']),
                            updated_at=datetime.fromisoformat(msg['updated_at']),
                            read_at=datetime.fromisoformat(msg['read_at']) if msg.get('read_at') else None
                        )
                        for msg in result.data
                    ]
                    
        except Exception as e:
            print(f"获取对话消息失败: {e}")
            
        return []
    
    async def mark_message_as_read(self, db_conn: Tuple[Any, str], message_id: int, user_id: int) -> bool:
        """标记消息为已读"""
        connection, db_type = db_conn
        
        try:
            if db_type == "postgres":
                query = """
                    UPDATE messages 
                    SET is_read = true, read_at = $1, updated_at = $1
                    WHERE id = $2 AND recipient_id = $3
                """
                now = datetime.now()
                result = await connection.execute(query, now, message_id, user_id)
                return result == "UPDATE 1"
                
            else:
                # Supabase 实现
                now = datetime.now().isoformat()
                result = await connection.table("messages").update({
                    "is_read": True,
                    "read_at": now,
                    "updated_at": now
                }).eq("id", message_id).eq("recipient_id", user_id).execute()
                
                return len(result.data) > 0
                
        except Exception as e:
            print(f"标记消息已读失败: {e}")
            
        return False

# 创建全局实例
message_crud = MessageCRUD() 