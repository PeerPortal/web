#!/bin/bash
# 启航引路人后端服务启动脚本

echo "🚀 启动启航引路人后端服务..."
echo "📍 工作目录: $(pwd)"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境，请先运行: python3 -m venv venv"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "❌ 未找到 .env 文件，请先配置环境变量"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查端口是否被占用
if lsof -i :8001 > /dev/null 2>&1; then
    echo "⚠️  端口 8001 已被占用，正在终止占用进程..."
    lsof -ti :8001 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 启动服务
echo "🌟 启动服务在端口 8001..."
echo "📖 API 文档: http://localhost:8001/docs"
echo "🏥 健康检查: http://localhost:8001/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=" * 60

# 启动 FastAPI 应用
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
