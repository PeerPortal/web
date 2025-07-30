#!/bin/bash

# PeerPortal AI智能体系统 v2.0 - Docker构建脚本
# 支持生产和开发环境构建

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="peerportal-ai-agent"
VERSION="2.0"

# 显示帮助信息
show_help() {
    echo -e "${BLUE}PeerPortal AI智能体系统 Docker构建脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  prod, production     构建生产环境镜像"
    echo "  dev, development     构建开发环境镜像"
    echo "  both                 构建生产和开发环境镜像"
    echo "  clean               清理Docker缓存和悬空镜像"
    echo "  push                推送镜像到仓库"
    echo "  help, -h, --help    显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 prod              # 构建生产环境镜像"
    echo "  $0 dev               # 构建开发环境镜像"
    echo "  $0 both              # 构建所有镜像"
    echo "  $0 clean             # 清理Docker缓存"
}

# 清理函数
cleanup_docker() {
    echo -e "${YELLOW}🧹 清理Docker缓存和悬空镜像...${NC}"
    
    # 清理构建缓存
    docker builder prune -f
    
    # 清理悬空镜像
    docker image prune -f
    
    # 清理未使用的镜像
    docker image ls | grep "<none>" | awk '{print $3}' | xargs -r docker rmi
    
    echo -e "${GREEN}✅ Docker清理完成${NC}"
}

# 构建生产环境镜像
build_production() {
    echo -e "${BLUE}🏗️ 构建生产环境镜像...${NC}"
    
    # 检查requirements-docker.txt是否存在
    if [ ! -f "requirements-docker.txt" ]; then
        echo -e "${YELLOW}⚠️ requirements-docker.txt 不存在，使用 requirements.txt${NC}"
        cp requirements.txt requirements-docker.txt
    fi
    
    # 构建镜像
    docker build \
        --file Dockerfile \
        --tag ${PROJECT_NAME}:${VERSION} \
        --tag ${PROJECT_NAME}:latest \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown') \
        .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 生产环境镜像构建成功${NC}"
        echo -e "   镜像标签: ${PROJECT_NAME}:${VERSION}, ${PROJECT_NAME}:latest"
    else
        echo -e "${RED}❌ 生产环境镜像构建失败${NC}"
        exit 1
    fi
}

# 构建开发环境镜像
build_development() {
    echo -e "${BLUE}🏗️ 构建开发环境镜像...${NC}"
    
    docker build \
        --file Dockerfile.dev \
        --tag ${PROJECT_NAME}:${VERSION}-dev \
        --tag ${PROJECT_NAME}:dev \
        --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
        --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown') \
        .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 开发环境镜像构建成功${NC}"
        echo -e "   镜像标签: ${PROJECT_NAME}:${VERSION}-dev, ${PROJECT_NAME}:dev"
    else
        echo -e "${RED}❌ 开发环境镜像构建失败${NC}"
        exit 1
    fi
}

# 推送镜像
push_images() {
    echo -e "${BLUE}📤 推送镜像到仓库...${NC}"
    
    # 检查是否设置了Docker仓库地址
    if [ -z "$DOCKER_REGISTRY" ]; then
        echo -e "${YELLOW}⚠️ 未设置 DOCKER_REGISTRY 环境变量，跳过推送${NC}"
        echo -e "   设置示例: export DOCKER_REGISTRY=your-registry.com${NC}"
        return
    fi
    
    # 重新标记镜像
    docker tag ${PROJECT_NAME}:latest ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
    docker tag ${PROJECT_NAME}:${VERSION} ${DOCKER_REGISTRY}/${PROJECT_NAME}:${VERSION}
    docker tag ${PROJECT_NAME}:dev ${DOCKER_REGISTRY}/${PROJECT_NAME}:dev
    
    # 推送镜像
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:${VERSION}
    docker push ${DOCKER_REGISTRY}/${PROJECT_NAME}:dev
    
    echo -e "${GREEN}✅ 镜像推送完成${NC}"
}

# 显示镜像信息
show_images() {
    echo -e "${BLUE}📋 构建的镜像列表:${NC}"
    docker images | grep ${PROJECT_NAME} | head -10
    echo ""
    
    # 显示镜像大小对比
    if docker images | grep -q "${PROJECT_NAME}.*latest"; then
        PROD_SIZE=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "${PROJECT_NAME}:latest" | awk '{print $2}')
        echo -e "生产环境镜像大小: ${GREEN}${PROD_SIZE}${NC}"
    fi
    
    if docker images | grep -q "${PROJECT_NAME}.*dev"; then
        DEV_SIZE=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "${PROJECT_NAME}:dev" | awk '{print $2}')
        echo -e "开发环境镜像大小: ${YELLOW}${DEV_SIZE}${NC}"
    fi
}

# 主逻辑
case "${1:-help}" in
    "prod"|"production")
        echo -e "${BLUE}🚀 开始构建生产环境镜像${NC}"
        build_production
        show_images
        ;;
    "dev"|"development")
        echo -e "${BLUE}🛠️ 开始构建开发环境镜像${NC}"
        build_development
        show_images
        ;;
    "both"|"all")
        echo -e "${BLUE}🏗️ 开始构建所有镜像${NC}"
        build_production
        build_development
        show_images
        ;;
    "clean")
        cleanup_docker
        ;;
    "push")
        push_images
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知选项: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 操作完成！${NC}" 