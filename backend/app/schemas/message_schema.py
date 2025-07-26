"""
消息系统的数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    text = "text"
    image = "image"
    file = "file"
    system = "system"

class MessageStatus(str, Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"

class MessageCreate(BaseModel):
    """创建消息"""
    recipient_id: int = Field(..., description="接收者ID")
    content: str = Field(..., min_length=1, max_length=10000, description="消息内容")
    message_type: MessageType = Field(default=MessageType.text, description="消息类型")
    conversation_id: Optional[int] = Field(None, description="对话ID")

class MessageUpdate(BaseModel):
    """更新消息"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000, description="消息内容")
    status: Optional[MessageStatus] = Field(None, description="消息状态")

class Message(BaseModel):
    """消息详情"""
    id: int
    conversation_id: int
    sender_id: int
    recipient_id: int
    content: str
    message_type: MessageType
    status: MessageStatus = MessageStatus.sent
    is_read: bool = False
    created_at: datetime
    updated_at: datetime
    read_at: Optional[datetime] = None

class ConversationParticipant(BaseModel):
    """对话参与者"""
    id: int
    username: str
    avatar_url: Optional[str] = None
    role: str

class Conversation(BaseModel):
    """对话详情"""
    id: int
    participants: List[ConversationParticipant]
    last_message: Optional[Message] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime

class ConversationCreate(BaseModel):
    """创建对话"""
    participant_ids: List[int] = Field(..., min_items=1, description="参与者ID列表")

class ConversationListItem(BaseModel):
    """对话列表项"""
    conversation_id: int
    mentor_id: Optional[int] = None
    mentor_name: Optional[str] = None
    mentor_avatar: Optional[str] = None
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_avatar: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0
    is_online: bool = False

class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: List[Message]
    total: int
    has_next: bool

class ConversationListResponse(BaseModel):
    """对话列表响应"""
    conversations: List[ConversationListItem]
    total: int 