#!/bin/bash

# OfferIn 新增功能测试启动脚本
# 测试论坛、消息、文件上传、AI路由等新功能

echo "🚀 OfferIn 新增功能综合测试"
echo "=================================="

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 虚拟环境已激活: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️  虚拟环境未激活，尝试激活..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    else
        echo "❌ 未找到虚拟环境，请确保已创建并激活虚拟环境"
        echo "   创建虚拟环境: python -m venv venv"
        echo "   激活虚拟环境: source venv/bin/activate"
        exit 1
    fi
fi

# 检查服务器是否运行
echo ""
echo "🔍 检查服务器状态..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ 后端服务器运行正常"
else
    echo "❌ 后端服务器未运行"
    echo "请在另一个终端启动服务器:"
    echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    read -p "是否现在启动服务器? (y/n): " start_server
    if [[ $start_server == "y" || $start_server == "Y" ]]; then
        echo "🚀 启动后端服务器..."
        nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
        SERVER_PID=$!
        echo "📝 服务器PID: $SERVER_PID"
        echo "📄 日志文件: server.log"
        echo "⏳ 等待服务器启动..."
        sleep 5
        
        # 再次检查
        if curl -s http://localhost:8000/ > /dev/null; then
            echo "✅ 服务器启动成功"
        else
            echo "❌ 服务器启动失败，请检查日志: tail -f server.log"
            exit 1
        fi
    else
        exit 1
    fi
fi

# 检查依赖
echo ""
echo "📦 检查Python依赖..."
python -c "import httpx, asyncio" 2>/dev/null || {
    echo "❌ 缺少测试依赖，正在安装..."
    echo "   注意: asyncio 是Python内置模块，只安装httpx..."
    pip install httpx
}
echo "✅ 测试依赖已安装"

# 运行数据库表结构验证
echo ""
echo "🗄️ 运行数据库表结构验证..."
python test_database_tables.py
DB_TEST_EXIT_CODE=$?

echo ""
echo "==============================================="

# 运行API功能测试
echo ""
echo "🌐 运行API功能测试..."
python test_new_features.py
API_TEST_EXIT_CODE=$?

# 生成综合报告
echo ""
echo "📊 生成综合测试报告..."

# 创建综合报告
cat > comprehensive_test_summary.md << EOF
# OfferIn 新增功能测试综合报告

## 测试执行时间
$(date)

## 测试概述

### 数据库表结构验证
- 状态: $([ $DB_TEST_EXIT_CODE -eq 0 ] && echo "✅ 成功" || echo "❌ 失败")
- 退出代码: $DB_TEST_EXIT_CODE

### API功能测试
- 状态: $([ $API_TEST_EXIT_CODE -eq 0 ] && echo "✅ 成功" || echo "❌ 失败")
- 退出代码: $API_TEST_EXIT_CODE

## 测试涵盖范围

### 🏛️ 论坛系统
- 论坛分类获取
- 帖子创建和查询
- 回复功能
- 点赞功能
- 热门标签

### 💬 消息系统
- 对话列表
- 消息发送和接收
- 消息已读状态

### 📁 文件上传
- 头像上传
- 文档上传
- 文件类型验证
- 大小限制检查

### 🤖 AI功能
- AI能力查询
- AI对话接口
- 路由修复验证

### 👤 用户管理
- 用户信息获取
- 基础信息端点

### 🗄️ 数据库
- 表结构验证
- 索引检查
- 触发器验证
- 视图检查

## 文件生成

以下测试报告文件已生成：
- \`database_verification_report_*.json\` - 数据库验证详细报告
- \`new_features_test_report_*.json\` - API功能测试详细报告

## 总体状态

$([ $DB_TEST_EXIT_CODE -eq 0 ] && [ $API_TEST_EXIT_CODE -eq 0 ] && echo "🎉 所有测试通过！系统功能正常。" || echo "⚠️ 部分测试失败，请检查详细报告。")

---
测试完成时间: $(date)
EOF

echo "📄 综合报告已保存: comprehensive_test_summary.md"

# 输出结果摘要
echo ""
echo "📈 测试结果摘要:"
echo "=================="
echo "🗄️ 数据库验证: $([ $DB_TEST_EXIT_CODE -eq 0 ] && echo "✅ 通过" || echo "❌ 失败")"
echo "🌐 API功能测试: $([ $API_TEST_EXIT_CODE -eq 0 ] && echo "✅ 通过" || echo "❌ 失败")"

# 显示生成的文件
echo ""
echo "📁 生成的文件:"
echo "=============="
ls -la *report*.json 2>/dev/null | head -10
ls -la comprehensive_test_summary.md 2>/dev/null

echo ""
if [ $DB_TEST_EXIT_CODE -eq 0 ] && [ $API_TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 所有测试完成！系统功能正常。"
    echo "📄 查看详细报告: cat comprehensive_test_summary.md"
else
    echo "⚠️ 部分测试失败，请检查详细报告进行排查。"
    echo "📊 数据库报告: ls database_verification_report_*.json"
    echo "📊 API测试报告: ls new_features_test_report_*.json"
fi

# 如果启动了服务器，询问是否关闭
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    read -p "🛑 是否关闭自动启动的服务器? (y/n): " stop_server
    if [[ $stop_server == "y" || $stop_server == "Y" ]]; then
        kill $SERVER_PID 2>/dev/null
        echo "🛑 服务器已关闭"
    else
        echo "🔄 服务器继续运行 (PID: $SERVER_PID)"
        echo "   手动关闭: kill $SERVER_PID"
    fi
fi

echo ""
echo "🎯 测试完成！感谢使用 OfferIn 测试工具。" 