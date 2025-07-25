#!/bin/bash
# 启动脚本：启动Streamlit Web界面

echo "🚀 启动启航AI留学规划师Web界面..."

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

# 启动Streamlit
echo "🌐 启动Streamlit界面 (端口8503)..."
export STREAMLIT_EMAIL=""
python -m streamlit run app/streamlit_app.py --server.port 8503
