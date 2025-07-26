#!/bin/bash
# LangSmith集成快速启动脚本
# 用于验证和测试LangSmith集成功能

echo "🚀 AI留学规划师 - LangSmith集成验证"
echo "=========================================="

# 检查Python环境
echo "🐍 检查Python环境..."
python --version

# 检查必要的包
echo "📦 检查依赖包..."
pip list | grep -E "(langsmith|langchain|fastapi)" || echo "⚠️ 请先安装依赖包: pip install -r requirements.txt"

# 检查环境变量
echo "🌍 检查环境变量配置..."
if [ -f ".env" ]; then
    echo "✅ 发现 .env 文件"
    if grep -q "LANGCHAIN_TRACING_V2" .env; then
        echo "✅ LangSmith配置存在"
    else
        echo "⚠️ 未发现LangSmith配置，将使用离线模式"
    fi
else
    echo "⚠️ 未发现 .env 文件，请从 configs/env_example.txt 创建"
fi

# 运行集成测试
echo "🧪 运行LangSmith集成测试..."
python test_langsmith_integration.py

# 检查API服务状态
echo "🌐 检查API服务状态..."
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    echo "✅ API服务正在运行"
    echo "📡 可以访问 http://localhost:8001/docs 查看API文档"
else
    echo "ℹ️ API服务未运行，可以使用以下命令启动："
    echo "   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload"
fi

echo ""
echo "📊 LangSmith Dashboard访问指南:"
echo "1. 注册/登录 https://smith.langchain.com"
echo "2. 创建项目: AI留学规划师"
echo "3. 获取API密钥并添加到 .env 文件"
echo "4. 设置 LANGCHAIN_TRACING_V2=true"
echo ""
echo "🎯 集成验证完成！查看详细报告: LANGSMITH_INTEGRATION_REPORT.md"
