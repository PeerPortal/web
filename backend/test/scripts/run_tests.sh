#!/bin/bash
# AI留学规划师Agent完整测试套件

echo "🧪 AI留学规划师Agent测试套件"
echo "========================================"

# 显示可用的测试选项
show_menu() {
    echo ""
    echo "📋 可用测试选项："
    echo "1) 🔧 LangSmith集成测试"
    echo "2) 🤖 Agent综合功能测试"
    echo "3) 💬 Agent交互式测试"
    echo "4) 🌐 API端点测试"
    echo "5) ⚡ 快速验证脚本"
    echo "6) � 启动API服务"
    echo "7) 📊 查看测试报告"
    echo "0) 🚪 退出"
    echo ""
}

# LangSmith集成测试
test_langsmith() {
    echo "🔧 运行LangSmith集成测试..."
    echo "========================================"
    python test_langsmith_integration.py
}

# Agent综合测试
test_agent_comprehensive() {
    echo "🤖 运行Agent综合功能测试..."
    echo "========================================"
    python test_agent_comprehensive.py
}

# 交互式测试
test_interactive() {
    echo "💬 启动Agent交互式测试..."
    echo "========================================"
    echo "💡 提示：输入 'help' 查看测试建议，输入 'quit' 退出"
    echo ""
    python test_agent_interactive.py
}

# API测试
test_api() {
    echo "🌐 运行API端点测试..."
    echo "========================================"
    echo "💡 提示：请确保API服务已启动"
    echo ""
    python test_api_endpoints.py
}

# 快速验证
quick_verify() {
    echo "⚡ 运行快速验证..."
    echo "========================================"
    ./verify_langsmith.sh
}

# 启动API服务
start_api() {
    echo "🚀 启动API服务..."
    echo "========================================"
    ./start_api.sh
}

# 查看测试报告
view_reports() {
    echo "📊 查看测试报告..."
    echo "========================================"
    
    if [ -f "agent_test_report.json" ]; then
        echo "📄 Agent测试报告 (agent_test_report.json):"
        echo "----------------------------------------"
        python -c "
import json
with open('agent_test_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(f'总测试数: {data[\"total_tests\"]}')
    print(f'通过测试: {data[\"passed_tests\"]}') 
    print(f'成功率: {data[\"success_rate\"]:.1f}%')
"
        echo ""
    else
        echo "❌ 未找到 agent_test_report.json"
    fi
    
    if [ -f "LANGSMITH_INTEGRATION_REPORT.md" ]; then
        echo "📋 LangSmith集成报告 (LANGSMITH_INTEGRATION_REPORT.md):"
        echo "----------------------------------------"
        echo "✅ 报告文件存在，可以使用文本编辑器查看详细内容"
        echo ""
    else
        echo "❌ 未找到 LANGSMITH_INTEGRATION_REPORT.md"
    fi
    
    if [ -f "AGENT_TESTING_GUIDE.md" ]; then
        echo "📖 测试指南 (AGENT_TESTING_GUIDE.md):"
        echo "----------------------------------------"
        echo "✅ 测试指南存在，包含详细的手动测试说明"
        echo ""
    else
        echo "❌ 未找到 AGENT_TESTING_GUIDE.md"
    fi
}

# 检查环境
check_environment() {
    echo "🌍 环境检查"
    echo "========================================"
    
    # 检查Python
    echo "🐍 Python版本:"
    python --version
    echo ""
    
    # 检查关键包
    echo "📦 关键依赖包:"
    python -c "
import sys
packages = ['fastapi', 'langchain', 'openai', 'langsmith', 'supabase']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg} (未安装)')
" 2>/dev/null
    echo ""
    
    # 检查环境变量
    echo "🔧 环境配置:"
    if [ -f ".env" ]; then
        echo "✅ .env 文件存在"
        
        # 检查关键配置（隐藏敏感信息）
        if grep -q "OPENAI_API_KEY=sk-" .env; then
            echo "✅ OpenAI API密钥已配置"
        else
            echo "❌ OpenAI API密钥未配置"
        fi
        
        if grep -q "LANGCHAIN_TRACING_V2=true" .env; then
            echo "✅ LangSmith追踪已启用"
        else
            echo "ℹ️ LangSmith追踪未启用"
        fi
        
        if grep -q "SUPABASE_URL=https://" .env; then
            echo "✅ Supabase数据库已配置"
        else
            echo "❌ Supabase数据库未配置"
        fi
    else
        echo "❌ .env 文件不存在"
        echo "💡 请从 configs/env_example.txt 创建 .env 文件"
    fi
    echo ""
}

# 主循环
main() {
    # 初始环境检查
    check_environment
    
    while true; do
        show_menu
        read -p "请选择测试选项 (0-7): " choice
        
        case $choice in
            1)
                test_langsmith
                ;;
            2)
                test_agent_comprehensive
                ;;
            3)
                test_interactive
                ;;
            4)
                test_api
                ;;
            5)
                quick_verify
                ;;
            6)
                start_api
                ;;
            7)
                view_reports
                ;;
            0)
                echo "👋 测试结束，谢谢使用！"
                exit 0
                ;;
            *)
                echo "❌ 无效选项，请选择 0-7"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
    done
}

# 如果直接运行脚本，启动主循环
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main
fi
