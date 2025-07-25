from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

app = FastAPI()

# 静态数据样本
SCHOOLS = [
    {"school": "哈佛大学", "major": "计算机科学"},
    {"school": "斯坦福大学", "major": "电子工程"},
    {"school": "麻省理工学院", "major": "机械工程"},
    {"school": "加州大学伯克利分校", "major": "经济学"},
    {"school": "普林斯顿大学", "major": "数学"},
    {"school": "耶鲁大学", "major": "生物学"},
    {"school": "芝加哥大学", "major": "物理学"},
    {"school": "哥伦比亚大学", "major": "心理学"},
    {"school": "宾夕法尼亚大学", "major": "金融学"},
    {"school": "杜克大学", "major": "化学"}
]

# JWT 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# 用户模型
class User(BaseModel):
    username: str
    password: str

# 注册/登录用的内存用户存储（后续替换为数据库）
fake_users_db = {}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(username: str):
    user = fake_users_db.get(username)
    if user:
        return User(username=username, password=user["password"]) 
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user.password):
        return False
    return user

# 注册接口
@app.post("/api/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {"password": hashed_password}
    return {"msg": "注册成功"}

# 登录接口
@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# 检索接口
@app.get("/api/search")
def search(school: Optional[str] = None, major: Optional[str] = None):
    results = SCHOOLS
    if school:
        results = [s for s in results if school in s["school"]]
    if major:
        results = [s for s in results if major in s["major"]]
    return results

# WebSocket 聊天接口（占位）
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"收到: {data}")
    except WebSocketDisconnect:
        pass 