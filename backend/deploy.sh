#!/bin/bash
set -e

# PeerPortal AI智能体系统 v2.0 - Docker部署脚本
# 自动化部署脚本，支持多种部署模式

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示标题
echo -e "${BLUE}"
echo "🤖 PeerPortal AI智能体系统 v2.0"
echo "==============================="
echo "专业的留学规划AI顾问部署工具"
echo -e "${NC}"

# 检查Docker和Docker Compose
check_requirements() {
    echo -e "${YELLOW}🔍 检查系统要求...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose未安装，请先安装Docker Compose${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker和Docker Compose已安装${NC}"
}

# 配置环境变量
setup_env() {
    echo -e "${YELLOW}🔧 配置环境变量...${NC}"
    
    if [ ! -f .env ]; then
        echo -e "${BLUE}📝 创建.env文件...${NC}"
        cp docker-env-example.txt .env
        
        echo -e "${YELLOW}⚠️  请编辑.env文件，设置以下必需配置:${NC}"
        echo "   1. OPENAI_API_KEY - OpenAI API密钥"
        echo "   2. SUPABASE_* - Supabase数据库配置"
        echo ""
        echo -e "${BLUE}提示: 使用 nano .env 或 vim .env 编辑配置文件${NC}"
        
        read -p "按回车键继续..."
    else
        echo -e "${GREEN}✅ .env文件已存在${NC}"
    fi
    
    # 检查关键配置
    if ! grep -q "sk-proj-" .env 2>/dev/null; then
        echo -e "${YELLOW}⚠️  请确保已设置有效的OPENAI_API_KEY${NC}"
    fi
}

# 显示部署选项
show_deployment_options() {
    echo -e "${BLUE}📋 选择部署模式:${NC}"
    echo "1. 🚀 快速启动 (AI Agent + Redis)"
    echo "2. 🏢 完整部署 (包含向量数据库)"
    echo "3. 🌐 生产部署 (包含Nginx)"
    echo "4. 🔧 自定义部署"
    echo "5. 🛑 停止所有服务"
    echo "6. 🧹 清理数据卷"
    echo ""
    read -p "请选择部署模式 (1-6): " choice
}

# 快速启动
quick_start() {
    echo -e "${GREEN}🚀 启动基础AI Agent服务...${NC}"
    docker-compose up -d ai-agent redis
    show_services_info
}

# 完整部署
full_deployment() {
    echo -e "${GREEN}🏢 启动完整AI Agent栈...${NC}"
    docker-compose --profile full-stack up -d
    show_services_info
}

# 生产部署
production_deployment() {
    echo -e "${GREEN}🌐 启动生产环境...${NC}"
    docker-compose --profile production up -d
    show_services_info
}

# 自定义部署
custom_deployment() {
    echo -e "${BLUE}🔧 可用服务:${NC}"
    echo "- ai-agent (AI智能体主服务)"
    echo "- redis (短期记忆缓存)"
    echo "- mongodb (文档存储)"
    echo "- milvus (向量数据库)"
    echo "- nginx (反向代理)"
    echo ""
    read -p "请输入要启动的服务名称 (空格分隔): " services
    
    if [ ! -z "$services" ]; then
        echo -e "${GREEN}🔧 启动自定义服务: $services${NC}"
        docker-compose up -d $services
        show_services_info
    fi
}

# 停止服务
stop_services() {
    echo -e "${YELLOW}🛑 停止所有服务...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
}

# 清理数据
cleanup_data() {
    echo -e "${RED}🧹 这将删除所有数据卷，包括：${NC}"
    echo "   - Redis缓存数据"
    echo "   - MongoDB文档数据"
    echo "   - Milvus向量数据"
    echo "   - 上传的文件"
    echo ""
    read -p "确认删除所有数据？(y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        docker-compose down -v
        docker volume prune -f
        echo -e "${GREEN}✅ 数据卷已清理${NC}"
    else
        echo -e "${BLUE}💡 操作已取消${NC}"
    fi
}

# 显示服务信息
show_services_info() {
    echo ""
    echo -e "${GREEN}🎉 部署完成！服务信息:${NC}"
    echo -e "${BLUE}===============================${NC}"
    
    # 等待服务启动
    echo -e "${YELLOW}⏳ 等待服务启动中...${NC}"
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "ai-agent.*Up"; then
        echo -e "${GREEN}✅ AI智能体服务: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API文档: http://localhost:8000/docs${NC}"
        echo -e "${GREEN}🔍 健康检查: http://localhost:8000/health${NC}"
        echo -e "${GREEN}🤖 Agent状态: http://localhost:8000/api/v2/agents/status${NC}"
    else
        echo -e "${RED}❌ AI智能体服务启动失败${NC}"
    fi
    
    if docker-compose ps | grep -q "redis.*Up"; then
        echo -e "${GREEN}✅ Redis缓存: localhost:6379${NC}"
    fi
    
    if docker-compose ps | grep -q "mongodb.*Up"; then
        echo -e "${GREEN}✅ MongoDB: localhost:27017${NC}"
    fi
    
    if docker-compose ps | grep -q "milvus.*Up"; then
        echo -e "${GREEN}✅ Milvus向量库: localhost:19530${NC}"
    fi
    
    if docker-compose ps | grep -q "minio.*Up"; then
        echo -e "${GREEN}✅ MinIO控制台: http://localhost:9001${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📋 常用命令:${NC}"
    echo "   查看日志: docker-compose logs -f ai-agent"
    echo "   重启服务: docker-compose restart ai-agent"
    echo "   停止服务: docker-compose down"
    echo ""
    
    # 测试AI Agent
    echo -e "${YELLOW}🧪 测试AI Agent连接...${NC}"
    sleep 5
    
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo -e "${GREEN}✅ AI Agent服务正常运行${NC}"
        
        # 显示快速测试命令
        echo ""
        echo -e "${BLUE}💡 快速测试示例:${NC}"
        echo 'curl -X POST "http://localhost:8000/api/v2/agents/planner/chat" \'
        echo '  -H "Content-Type: application/json" \'
        echo '  -d '"'"'{"message": "你好，请介绍一下你的功能", "user_id": "test_user"}'"'"
    else
        echo -e "${YELLOW}⚠️  AI Agent服务正在启动中，请稍后访问${NC}"
    fi
}

# 显示日志
show_logs() {
    echo -e "${BLUE}📋 查看服务日志:${NC}"
    echo "1. AI Agent服务日志"
    echo "2. Redis日志"
    echo "3. MongoDB日志"
    echo "4. 所有服务日志"
    echo ""
    read -p "选择查看的日志 (1-4): " log_choice
    
    case $log_choice in
        1) docker-compose logs -f ai-agent ;;
        2) docker-compose logs -f redis ;;
        3) docker-compose logs -f mongodb ;;
        4) docker-compose logs -f ;;
        *) echo -e "${RED}无效选择${NC}" ;;
    esac
}

# 主菜单
main() {
    check_requirements
    setup_env
    
    while true; do
        echo ""
        show_deployment_options
        
        case $choice in
            1) quick_start ;;
            2) full_deployment ;;
            3) production_deployment ;;
            4) custom_deployment ;;
            5) stop_services ;;
            6) cleanup_data ;;
            *) 
                echo -e "${RED}无效选择，请重新输入${NC}"
                continue
                ;;
        esac
        
        echo ""
        read -p "按回车键继续，或输入 'q' 退出: " continue_choice
        if [ "$continue_choice" = "q" ]; then
            break
        fi
    done
    
    echo -e "${BLUE}👋 感谢使用PeerPortal AI智能体系统！${NC}"
}

# 如果直接运行脚本
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi 