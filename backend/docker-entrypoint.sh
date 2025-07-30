#!/bin/bash
set -e

echo "🚀 PeerPortal AI智能体系统 v2.0 启动中..."

# 等待外部服务（如Redis）就绪
if [ ! -z "$REDIS_URL" ]; then
    echo "🔄 等待Redis服务启动..."
    # 提取Redis主机和端口
    if [[ $REDIS_URL =~ redis://([^:]+):([0-9]+) ]]; then
        REDIS_HOST=${BASH_REMATCH[1]}
        REDIS_PORT=${BASH_REMATCH[2]}
        
        # 等待Redis可用
        timeout=30
        while ! nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; do
            timeout=$((timeout - 1))
            if [ $timeout -eq 0 ]; then
                echo "⚠️  Redis连接超时，将使用本地内存缓存"
                break
            fi
            echo "    等待Redis连接... ($timeout秒)"
            sleep 1
        done
        
        if [ $timeout -gt 0 ]; then
            echo "✅ Redis连接成功"
        fi
    fi
fi

# 检查必需的环境变量
echo "🔍 检查环境配置..."

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ 错误: OPENAI_API_KEY 环境变量未设置"
    echo "   请设置OpenAI API密钥以启用AI功能"
    exit 1
fi

echo "✅ OpenAI API密钥已配置"

# 验证Python环境和AI Agent系统
echo "🔧 验证AI Agent系统..."

# 运行快速配置测试
python3 -c "
import sys
import os
sys.path.append('/app')

try:
    # 测试基础导入
    from app.agents.v2 import create_study_planner
    print('✅ AI Agent模块导入成功')
    
    # 测试配置
    from app.agents.v2.config import config_manager
    print('✅ 配置管理器初始化成功')
    
    print('🎯 AI智能体系统验证完成')
except Exception as e:
    print(f'❌ AI Agent系统验证失败: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ AI Agent系统验证失败，容器启动中止"
    exit 1
fi

# 创建日志目录
mkdir -p /app/logs

# 输出启动信息
echo "📊 系统配置摘要:"
echo "   🤖 AI模型: ${DEFAULT_MODEL:-gpt-4o-mini}"
echo "   💾 Redis缓存: ${REDIS_URL:+已配置}"
echo "   🔍 Milvus向量库: ${MILVUS_HOST:+已配置}"
echo "   📄 MongoDB文档库: ${MONGODB_URL:+已配置}"
echo "   🐛 调试模式: ${DEBUG:-false}"
echo ""

echo "🎉 系统启动完成，开始运行AI智能体服务..."
echo "📡 API文档: http://localhost:8000/docs"
echo "🔍 健康检查: http://localhost:8000/health"
echo "🤖 AI Agent状态: http://localhost:8000/api/v2/agents/status"

# 执行传入的命令
exec "$@" 