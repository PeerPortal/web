#!/bin/bash

# PeerPortal AI智能体系统 v2.0 - 快速启动脚本
# 一键式 Docker 部署解决方案

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="PeerPortal AI智能体系统 v2.0"

# 显示欢迎信息
show_welcome() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  🚀 ${PROJECT_NAME} - Docker 快速启动${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [模式] [选项]"
    echo ""
    echo "模式:"
    echo "  dev, development     启动开发环境 (支持热重载)"
    echo "  prod, production     启动生产环境"
    echo "  full                 启动完整生产环境 (包含 Milvus)"
    echo "  tools                启动开发环境 + 管理工具"
    echo "  streamlit           启动 Streamlit 界面"
    echo ""
    echo "选项:"
    echo "  --build             强制重新构建镜像"
    echo "  --clean             启动前清理旧容器和镜像"
    echo "  --logs              启动后显示日志"
    echo "  --status            显示服务状态"
    echo "  --stop              停止所有服务"
    echo "  --help, -h          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev              # 快速启动开发环境"
    echo "  $0 prod --build     # 重新构建并启动生产环境"
    echo "  $0 dev --logs       # 启动开发环境并显示日志"
    echo "  $0 --stop           # 停止所有服务"
}

# 检查环境
check_environment() {
    echo -e "${YELLOW}🔍 检查运行环境...${NC}"
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安装或未在 PATH 中${NC}"
        echo -e "   请安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose 未安装${NC}"
        echo -e "   请安装 Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ] && [ ! -f "docker-env-example.txt" ]; then
        echo -e "${YELLOW}⚠️ 未找到环境配置文件${NC}"
        echo -e "   请创建 .env 文件或参考 docker-env-example.txt"
    fi
    
    echo -e "${GREEN}✅ 环境检查通过${NC}"
}

# 清理环境
clean_environment() {
    echo -e "${YELLOW}🧹 清理 Docker 环境...${NC}"
    
    # 停止所有相关容器
    docker-compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true
    
    # 清理悬空镜像
    docker image prune -f
    
    # 清理未使用的网络
    docker network prune -f
    
    echo -e "${GREEN}✅ 环境清理完成${NC}"
}

# 构建镜像
build_images() {
    local mode=$1
    echo -e "${BLUE}🏗️ 构建 Docker 镜像...${NC}"
    
    if [ "$mode" = "dev" ]; then
        ./docker-build.sh dev
    else
        ./docker-build.sh prod
    fi
}

# 启动开发环境
start_development() {
    echo -e "${BLUE}🛠️ 启动开发环境...${NC}"
    
    local compose_cmd="docker-compose -f docker-compose.dev.yml"
    
    # 启动基础服务
    $compose_cmd up -d ai-agent-dev redis-dev
    
    echo -e "${GREEN}✅ 开发环境启动成功！${NC}"
    echo ""
    echo -e "${PURPLE}📋 开发环境信息:${NC}"
    echo -e "  🌐 API 文档: http://localhost:8000/docs"
    echo -e "  🔍 健康检查: http://localhost:8000/health"
    echo -e "  🤖 AI Agent 状态: http://localhost:8000/api/v2/agents/status"
    echo -e "  💾 Redis: localhost:6380"
    echo ""
    echo -e "${YELLOW}💡 提示: 代码修改会自动重载，无需重启容器${NC}"
}

# 启动生产环境
start_production() {
    echo -e "${BLUE}🚀 启动生产环境...${NC}"
    
    docker-compose up -d ai-agent redis mongodb
    
    echo -e "${GREEN}✅ 生产环境启动成功！${NC}"
    echo ""
    echo -e "${PURPLE}📋 生产环境信息:${NC}"
    echo -e "  🌐 API 文档: http://localhost:8000/docs"
    echo -e "  🔍 健康检查: http://localhost:8000/health"
    echo -e "  🤖 AI Agent 状态: http://localhost:8000/api/v2/agents/status"
    echo -e "  💾 Redis: localhost:6379"
    echo -e "  📄 MongoDB: localhost:27017"
}

# 启动完整环境
start_full_stack() {
    echo -e "${BLUE}🌟 启动完整生产环境...${NC}"
    
    docker-compose --profile full-stack up -d
    
    echo -e "${GREEN}✅ 完整环境启动成功！${NC}"
    echo ""
    echo -e "${PURPLE}📋 完整环境信息:${NC}"
    echo -e "  🌐 API 文档: http://localhost:8000/docs"
    echo -e "  🔍 健康检查: http://localhost:8000/health"
    echo -e "  🤖 AI Agent 状态: http://localhost:8000/api/v2/agents/status"
    echo -e "  💾 Redis: localhost:6379"
    echo -e "  📄 MongoDB: localhost:27017"
    echo -e "  🔍 Milvus: localhost:19530"
    echo -e "  📦 MinIO: http://localhost:9001"
}

# 启动管理工具
start_with_tools() {
    echo -e "${BLUE}🔧 启动开发环境 + 管理工具...${NC}"
    
    docker-compose -f docker-compose.dev.yml --profile tools up -d
    
    echo -e "${GREEN}✅ 开发环境 + 工具启动成功！${NC}"
    echo ""
    echo -e "${PURPLE}📋 可用服务:${NC}"
    echo -e "  🌐 API 文档: http://localhost:8000/docs"
    echo -e "  🔍 健康检查: http://localhost:8000/health"
    echo -e "  🤖 AI Agent 状态: http://localhost:8000/api/v2/agents/status"
    echo -e "  💾 Redis 管理: http://localhost:8081"
}

# 启动 Streamlit
start_streamlit() {
    echo -e "${BLUE}📊 启动 Streamlit 界面...${NC}"
    
    docker-compose -f docker-compose.dev.yml --profile streamlit up -d
    
    echo -e "${GREEN}✅ Streamlit 启动成功！${NC}"
    echo ""
    echo -e "${PURPLE}📋 Streamlit 信息:${NC}"
    echo -e "  🌐 Streamlit 界面: http://localhost:8501"
    echo -e "  🔍 API 后端: http://localhost:8000"
}

# 显示服务状态
show_status() {
    echo -e "${BLUE}📊 服务状态:${NC}"
    echo ""
    
    # 检查生产环境
    if docker-compose ps | grep -q "peerportal"; then
        echo -e "${GREEN}🚀 生产环境:${NC}"
        docker-compose ps
        echo ""
    fi
    
    # 检查开发环境
    if docker-compose -f docker-compose.dev.yml ps | grep -q "peerportal"; then
        echo -e "${YELLOW}🛠️ 开发环境:${NC}"
        docker-compose -f docker-compose.dev.yml ps
        echo ""
    fi
    
    # 显示端口使用情况
    echo -e "${BLUE}🔗 端口使用情况:${NC}"
    netstat -tlnp 2>/dev/null | grep -E ":(8000|8501|6379|6380|27017|19530)" | head -10 || echo "  无相关端口在使用"
}

# 停止所有服务
stop_services() {
    echo -e "${YELLOW}🛑 停止所有服务...${NC}"
    
    docker-compose -f docker-compose.yml down --remove-orphans 2>/dev/null || true
    docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true
    
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
}

# 显示日志
show_logs() {
    local mode=$1
    
    if [ "$mode" = "dev" ]; then
        echo -e "${BLUE}📝 开发环境日志:${NC}"
        docker-compose -f docker-compose.dev.yml logs -f
    else
        echo -e "${BLUE}📝 生产环境日志:${NC}"
        docker-compose logs -f
    fi
}

# 主逻辑
main() {
    local mode=""
    local build_flag=false
    local clean_flag=false
    local logs_flag=false
    local status_flag=false
    local stop_flag=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            dev|development)
                mode="dev"
                shift
                ;;
            prod|production)
                mode="prod"
                shift
                ;;
            full)
                mode="full"
                shift
                ;;
            tools)
                mode="tools"
                shift
                ;;
            streamlit)
                mode="streamlit"
                shift
                ;;
            --build)
                build_flag=true
                shift
                ;;
            --clean)
                clean_flag=true
                shift
                ;;
            --logs)
                logs_flag=true
                shift
                ;;
            --status)
                status_flag=true
                shift
                ;;
            --stop)
                stop_flag=true
                shift
                ;;
            --help|-h)
                show_welcome
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 未知参数: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    show_welcome
    
    # 处理特殊命令
    if [ "$stop_flag" = true ]; then
        stop_services
        exit 0
    fi
    
    if [ "$status_flag" = true ]; then
        show_status
        exit 0
    fi
    
    # 检查环境
    check_environment
    
    # 清理环境（如果需要）
    if [ "$clean_flag" = true ]; then
        clean_environment
    fi
    
    # 构建镜像（如果需要）
    if [ "$build_flag" = true ]; then
        build_images "$mode"
    fi
    
    # 启动服务
    case "$mode" in
        "dev")
            start_development
            ;;
        "prod")
            start_production
            ;;
        "full")
            start_full_stack
            ;;
        "tools")
            start_with_tools
            ;;
        "streamlit")
            start_streamlit
            ;;
        *)
            echo -e "${YELLOW}⚠️ 未指定模式，启动开发环境${NC}"
            start_development
            ;;
    esac
    
    # 显示日志（如果需要）
    if [ "$logs_flag" = true ]; then
        echo ""
        echo -e "${BLUE}按 Ctrl+C 退出日志查看${NC}"
        sleep 2
        show_logs "$mode"
    fi
}

# 执行主函数
main "$@" 