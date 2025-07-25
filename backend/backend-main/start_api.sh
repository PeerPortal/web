#!/bin/bash
# 启动脚本：启动FastAPI服务器

echo "🚀 启动启航引路人后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境，请先运行 python -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖包..."
pip install -r requirements.txt

# 启动服务
echo "🌐 启动FastAPI服务器 (端口8001)..."
python -m uvicorn app.main:app --reload --port 8001
