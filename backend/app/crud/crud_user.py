"""
用户相关的CRUD操作
支持asyncpg连接池和Supabase客户端两种模式
"""
import asyncpg
from passlib.context import CryptContext
from typing import Optional, Union, Dict, Any
from supabase import Client

from app.schemas.user_schema import UserCreate, UserUpdate, UserRead, ProfileUpdate, ProfileRead

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

# 通用数据库操作函数
async def get_user_by_id(db_conn: Dict[str, Any], user_id: int) -> Optional[Dict]:
    """根据ID获取用户"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                "SELECT id, username, email, password_hash, role, is_active, created_at FROM users WHERE id = $1",
                user_id
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('users').select(
                'id, username, email, password_hash, role, is_active, created_at'
            ).eq('id', user_id).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None

async def get_user_by_username(db_conn: Dict[str, Any], username: str) -> Optional[Dict]:
    """根据用户名获取用户"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                "SELECT id, username, email, password_hash, role, is_active, created_at FROM users WHERE username = $1",
                username
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('users').select(
                'id, username, email, password_hash, role, is_active, created_at'
            ).eq('username', username).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None

async def get_user_by_email(db_conn: Dict[str, Any], email: str) -> Optional[Dict]:
    """根据邮箱获取用户"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                "SELECT id, username, email, password_hash, role, is_active, created_at FROM users WHERE email = $1",
                email
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('users').select(
                'id, username, email, password_hash, role, is_active, created_at'
            ).eq('email', email).execute()
            return result.data[0] if result.data else None
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None

async def create_user(db_conn: Dict[str, Any], user: UserCreate) -> Optional[Dict]:
    """创建新用户"""
    try:
        # 检查用户名是否已存在
        existing_user = await get_user_by_username(db_conn, user.username)
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在（如果提供了邮箱）
        if user.email:
            existing_email = await get_user_by_email(db_conn, user.email)
            if existing_email:
                raise ValueError("邮箱已存在")
        
        # 哈希密码
        hashed_password = get_password_hash(user.password)
        
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.fetchrow(
                """
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, username, email, role, is_active, created_at
                """,
                user.username, user.email, hashed_password, 
                getattr(user, 'role', 'user'), True
            )
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('users').insert({
                'username': user.username,
                'email': user.email,
                'password_hash': hashed_password,
                'role': getattr(user, 'role', 'user'),
                'is_active': True
            }).execute()
            return result.data[0] if result.data else None
            
    except Exception as e:
        print(f"创建用户失败: {e}")
        raise ValueError(f"创建用户失败: {str(e)}")

async def authenticate_user(db_conn: Dict[str, Any], username: str, password: str) -> Optional[Dict]:
    """验证用户登录"""
    user = await get_user_by_username(db_conn, username)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    if not user.get('is_active', True):
        return None
    return user

async def update_user(db_conn: Dict[str, Any], user_id: int, user_update: UserUpdate) -> Optional[Dict]:
    """更新用户信息"""
    try:
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return await get_user_by_id(db_conn, user_id)
        
        # 如果要更新密码，需要哈希
        if 'password' in update_data:
            update_data['password_hash'] = get_password_hash(update_data.pop('password'))
        
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
            query = f"""
                UPDATE users SET {set_clause}, updated_at = NOW()
                WHERE id = $1
                RETURNING id, username, email, role, is_active, created_at
            """
            result = await conn.fetchrow(query, user_id, *update_data.values())
            return dict(result) if result else None
        else:
            client: Client = db_conn["connection"]
            result = client.table('users').update(update_data).eq('id', user_id).execute()
            return result.data[0] if result.data else None
            
    except Exception as e:
        print(f"更新用户失败: {e}")
        return None

async def delete_user(db_conn: Dict[str, Any], user_id: int) -> bool:
    """删除用户"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            result = await conn.execute("DELETE FROM users WHERE id = $1", user_id)
            return result == "DELETE 1"
        else:
            client: Client = db_conn["connection"]
            result = client.table('users').delete().eq('id', user_id).execute()
            return len(result.data) > 0
    except Exception as e:
        print(f"删除用户失败: {e}")
        return False

# Profile 相关操作
async def get_user_profile(db_conn: Dict[str, Any], user_id: int) -> Optional[Dict]:
    """获取用户资料"""
    try:
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 添加连接验证
            try:
                result = await conn.fetchrow(
                    """
                    SELECT 
                        u.id, u.username, u.email, u.role, u.is_active, u.created_at,
                        p.full_name, p.avatar_url, p.bio, p.phone, p.location, p.website, p.birth_date
                    FROM users u
                    LEFT JOIN profiles p ON u.id = p.user_id
                    WHERE u.id = $1
                    """,
                    user_id
                )
                return dict(result) if result else None
            except Exception as db_error:
                print(f"数据库连接错误，尝试使用备用方案: {db_error}")
                # 如果数据库连接失败，尝试降级到基本用户信息
                try:
                    basic_result = await conn.fetchrow(
                        "SELECT id, username, email, role, is_active, created_at FROM users WHERE id = $1",
                        user_id
                    )
                    if basic_result:
                        return dict(basic_result)
                except:
                    return None
        else:
            client: Client = db_conn["connection"]
            # 先获取用户信息
            try:
                user_result = client.table('users').select(
                    'id, username, email, role, is_active, created_at'
                ).eq('id', user_id).execute()
                
                if not user_result.data:
                    return None
                    
                user_data = user_result.data[0]
                
                # 尝试获取profile信息，如果失败也不影响基本用户信息返回
                try:
                    profile_result = client.table('profiles').select(
                        'full_name, avatar_url, bio, phone, location, website, birth_date'
                    ).eq('user_id', user_id).execute()
                    
                    # 合并数据
                    if profile_result.data:
                        profile_data = profile_result.data[0]
                        # 安全地合并数据，避免键冲突
                        for key, value in profile_data.items():
                            if key not in user_data:  # 避免覆盖用户基本信息
                                user_data[key] = value
                except Exception as profile_error:
                    print(f"获取profile信息失败，但用户基本信息仍可用: {profile_error}")
                    # 继续返回用户基本信息
                
                return user_data
            except Exception as supabase_error:
                print(f"Supabase查询失败: {supabase_error}")
                return None
    except Exception as e:
        print(f"获取用户资料失败: {e}")
        return None

async def update_user_profile(db_conn: Dict[str, Any], user_id: int, profile: ProfileUpdate) -> Optional[Dict]:
    """更新用户资料"""
    try:
        update_data = profile.model_dump(exclude_unset=True)
        if not update_data:
            return await get_user_profile(db_conn, user_id)
        
        if db_conn["type"] == "asyncpg":
            conn = db_conn["connection"]
            # 先检查profile是否存在
            existing = await conn.fetchval("SELECT id FROM profiles WHERE user_id = $1", user_id)
            
            if existing:
                # 更新现有profile
                set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
                query = f"""
                    UPDATE profiles SET {set_clause}, updated_at = NOW()
                    WHERE user_id = $1
                """
                await conn.execute(query, user_id, *update_data.values())
            else:
                # 创建新profile
                update_data['user_id'] = user_id
                columns = ", ".join(update_data.keys())
                placeholders = ", ".join([f"${i+1}" for i in range(len(update_data))])
                query = f"INSERT INTO profiles ({columns}) VALUES ({placeholders})"
                await conn.execute(query, *update_data.values())
                
            return await get_user_profile(db_conn, user_id)
        else:
            client: Client = db_conn["connection"]
            # 检查profile是否存在
            existing = client.table('profiles').select('id').eq('user_id', user_id).execute()
            
            if existing.data:
                # 更新
                result = client.table('profiles').update(update_data).eq('user_id', user_id).execute()
            else:
                # 创建
                update_data['user_id'] = user_id
                result = client.table('profiles').insert(update_data).execute()
            
            return await get_user_profile(db_conn, user_id)
            
    except Exception as e:
        print(f"更新用户资料失败: {e}")
        return None 