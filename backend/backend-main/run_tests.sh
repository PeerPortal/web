#!/bin/bash
# 测试运行脚本

echo "🧪 启航引路人 - Agent测试套件"
echo "=================================="

# 激活虚拟环境
source venv/bin/activate

echo "1. 🔧 基础Agent测试"
python test/agents/test_agent.py

echo -e "\n2. 🤖 简单Agent测试"
python test/agents/test_simple_agent.py

echo -e "\n3. 🧠 高级Agent测试"
python test/agents/test_advanced_agent.py

echo -e "\n4. 🌐 Agent API测试"
echo "请确保FastAPI服务器正在运行 (./start_api.sh)"
read -p "服务器已启动？ (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python test/agents/test_agent_api.py
else
    echo "跳过API测试"
fi

echo -e "\n✅ 测试完成！"
