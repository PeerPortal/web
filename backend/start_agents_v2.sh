#!/bin/bash
"""
PeerPortal AI智能体系统 v2.0 一键启动脚本
"""

echo "🚀 PeerPortal AI智能体系统 v2.0 启动脚本"
echo "================================================"

# 检查Python环境
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
echo "🔍 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    echo "   python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 虚拟环境激活失败"
    exit 1
fi
echo "✅ 虚拟环境已激活"

# 检查环境变量文件
echo "🔍 检查环境变量..."
if [ ! -f ".env" ]; then
    echo "❌ .env文件不存在，请先配置环境变量"
    echo "   参考: configs/env_example.txt"
    exit 1
fi

# 加载环境变量
set -a
source .env
set +a
echo "✅ 环境变量已加载"

# 检查必需的环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY 未设置，请在.env文件中配置"
    exit 1
fi
echo "✅ 必需环境变量已设置"

# 安装依赖（如果需要）
echo "🔍 检查依赖..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 安装缺失的依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi
echo "✅ 依赖检查完成"

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p uploads logs
echo "✅ 目录创建完成"

# 显示启动信息
echo ""
echo "🌐 服务器信息:"
echo "   主页: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   智能体状态: http://localhost:8000/api/v2/agents/status"
echo "   智能体健康检查: http://localhost:8000/api/v2/agents/health"
echo ""

# 启动选项
echo "🚀 启动选项:"
echo "   [1] 启动服务器（前台运行）"
echo "   [2] 启动服务器（后台运行）"
echo "   [3] 运行系统测试"
echo "   [4] 运行API测试"
echo "   [q] 退出"
echo ""

while true; do
    read -p "请选择操作 [1-4/q]: " choice
    case $choice in
        1)
            echo ""
            echo "🚀 启动FastAPI服务器（前台运行）..."
            echo "   按 Ctrl+C 停止服务器"
            echo ""
            uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
            break
            ;;
        2)
            echo ""
            echo "🚀 启动FastAPI服务器（后台运行）..."
            nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
            SERVER_PID=$!
            echo "✅ 服务器已启动，PID: $SERVER_PID"
            echo "   日志文件: server.log"
            echo "   停止服务器: kill $SERVER_PID"
            echo ""
            break
            ;;
        3)
            echo ""
            echo "🧪 运行系统配置测试..."
            python test_v2_config.py
            echo ""
            ;;
        4)
            echo ""
            echo "🧪 运行API功能测试..."
            echo "   确保服务器已启动 (http://localhost:8000)"
            read -p "服务器是否已启动? [y/N]: " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                python test_agents_api.py
            else
                echo "请先启动服务器"
            fi
            echo ""
            ;;
        q|Q)
            echo ""
            echo "👋 退出启动脚本"
            break
            ;;
        *)
            echo "❌ 无效选择，请重试"
            ;;
    esac
done

echo ""
echo "🎉 感谢使用PeerPortal AI智能体系统 v2.0！" 