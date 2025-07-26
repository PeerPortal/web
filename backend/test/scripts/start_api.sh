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
#!/bin/bash
# AI留学规划师API启动脚本

echo "🚀 启动AI留学规划师API服务"
echo "================================"

# 检查Python环境
echo "🐍 检查Python环境..."
python --version

# 检查依赖包
echo "📦 检查关键依赖包..."
python -c "import fastapi, langchain, openai" 2>/dev/null && echo "✅ 核心包已安装" || echo "❌ 缺少核心包，请运行: pip install -r requirements.txt"

# 检查环境配置
echo "🌍 检查环境配置..."
if [ -f ".env" ]; then
    echo "✅ 发现 .env 配置文件"
    
    # 检查关键配置
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "✅ OpenAI API密钥已配置"
    else
        echo "⚠️ OpenAI API密钥未配置或格式不正确"
    fi
    
    if grep -q "LANGCHAIN_TRACING_V2=true" .env; then
        echo "✅ LangSmith追踪已启用"
    else
        echo "ℹ️ LangSmith追踪未启用（可选）"
    fi
else
    echo "⚠️ 未找到 .env 文件，请从 configs/env_example.txt 创建"
fi

# 检查端口占用
echo "🔍 检查端口8001..."
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null; then
    echo "⚠️ 端口8001已被占用，请先停止相关进程"
    lsof -Pi :8001 -sTCP:LISTEN
    echo ""
    echo "💡 停止占用进程: kill -9 \$(lsof -t -i:8001)"
    exit 1
else
    echo "✅ 端口8001可用"
fi

echo ""
echo "🌟 启动API服务..."
echo "📍 服务地址: http://localhost:8001"
echo "📚 API文档: http://localhost:8001/docs"
echo "🏥 健康检查: http://localhost:8001/api/v1/advanced-planner/health"
echo ""
echo "💡 停止服务: Ctrl+C"
echo "================================"

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
