#!/bin/bash

# PeerPortal AI智能体系统 v2.0 - 网络优化构建脚本
# 专门处理网络连接问题和依赖下载失败

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
MAX_RETRIES=3

echo -e "${BLUE}🔄 PeerPortal AI智能体系统 - 网络优化构建${NC}"
echo ""

# 检查网络连接
check_network() {
    echo -e "${YELLOW}🌐 检查网络连接...${NC}"
    
    # 检查PyPI连接
    if curl -I https://pypi.org --connect-timeout 10 --max-time 30 &>/dev/null; then
        echo -e "${GREEN}✅ PyPI 连接正常${NC}"
        USE_MIRROR=false
    else
        echo -e "${YELLOW}⚠️ PyPI 连接缓慢，将使用国内镜像${NC}"
        USE_MIRROR=true
    fi
    
    # 检查清华镜像
    if curl -I https://pypi.tuna.tsinghua.edu.cn --connect-timeout 10 --max-time 30 &>/dev/null; then
        echo -e "${GREEN}✅ 清华镜像连接正常${NC}"
        MIRROR_OK=true
    else
        echo -e "${YELLOW}⚠️ 清华镜像连接异常，将尝试其他镜像${NC}"
        MIRROR_OK=false
    fi
}

# 创建临时requirements文件
create_temp_requirements() {
    local dockerfile_type=$1
    local temp_file="requirements-temp.txt"
    
    echo -e "${BLUE}📝 创建临时requirements文件...${NC}"
    
    if [ "$dockerfile_type" = "dev" ]; then
        # 开发环境使用完整依赖
        cp requirements.txt $temp_file
    else
        # 生产环境使用优化依赖
        cp requirements-docker.txt $temp_file
    fi
    
    # 添加镜像源配置到临时文件顶部
    if [ "$USE_MIRROR" = true ]; then
        cat > temp_pip_config << EOF
# 使用国内镜像源和重试机制
--index-url https://pypi.tuna.tsinghua.edu.cn/simple/
--trusted-host pypi.tuna.tsinghua.edu.cn
--timeout 300
--retries 5
EOF
        cat temp_pip_config $temp_file > requirements-network-optimized.txt
        rm temp_pip_config $temp_file
    else
        # 即使不使用镜像，也添加重试机制
        cat > temp_pip_config << EOF
# 增强网络重试机制
--timeout 300
--retries 5
EOF
        cat temp_pip_config $temp_file > requirements-network-optimized.txt
        rm temp_pip_config $temp_file
    fi
    
    echo -e "${GREEN}✅ 网络优化的requirements文件已创建${NC}"
}

# 构建镜像（带重试）
build_with_retry() {
    local dockerfile_name=$1
    local image_tag=$2
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        echo -e "${BLUE}🏗️ 开始构建镜像 (尝试 $((retry_count + 1))/$MAX_RETRIES)...${NC}"
        
        if docker build \
            --file $dockerfile_name \
            --tag $image_tag \
            --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
            --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown') \
            --progress=plain \
            .; then
            echo -e "${GREEN}✅ 镜像构建成功: $image_tag${NC}"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $MAX_RETRIES ]; then
                echo -e "${YELLOW}⚠️ 构建失败，等待30秒后重试...${NC}"
                sleep 30
                
                # 清理失败的构建缓存
                docker builder prune -f >/dev/null 2>&1 || true
            else
                echo -e "${RED}❌ 构建失败，已达到最大重试次数${NC}"
                return 1
            fi
        fi
    done
}

# 主要构建函数
build_image() {
    local build_type=${1:-dev}
    
    echo -e "${BLUE}🚀 开始构建 $build_type 环境镜像${NC}"
    
    # 检查网络
    check_network
    
    # 选择构建目标
    case "$build_type" in
        "dev"|"development")
            echo -e "${YELLOW}🛠️ 构建开发环境镜像...${NC}"
            create_temp_requirements "dev"
            build_with_retry "Dockerfile.dev" "${PROJECT_NAME}:${VERSION}-dev"
            if [ $? -eq 0 ]; then
                docker tag "${PROJECT_NAME}:${VERSION}-dev" "${PROJECT_NAME}:dev"
            fi
            ;;
        "prod"|"production")
            echo -e "${YELLOW}🏭 构建生产环境镜像...${NC}"
            create_temp_requirements "prod"
            build_with_retry "Dockerfile" "${PROJECT_NAME}:${VERSION}"
            if [ $? -eq 0 ]; then
                docker tag "${PROJECT_NAME}:${VERSION}" "${PROJECT_NAME}:latest"
            fi
            ;;
        *)
            echo -e "${RED}❌ 未知的构建类型: $build_type${NC}"
            echo "可用选项: dev, prod"
            exit 1
            ;;
    esac
    
    # 清理临时文件
    rm -f requirements-network-optimized.txt
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [构建类型]"
    echo ""
    echo "构建类型:"
    echo "  dev, development     构建开发环境镜像"
    echo "  prod, production     构建生产环境镜像"
    echo ""
    echo "特性:"
    echo "  ✅ 自动检测网络状况"
    echo "  ✅ 智能选择镜像源"
    echo "  ✅ 网络错误自动重试"
    echo "  ✅ 构建失败自动重试"
    echo ""
    echo "示例:"
    echo "  $0 dev               # 构建开发环境"
    echo "  $0 prod              # 构建生产环境"
}

# 主逻辑
case "${1:-dev}" in
    "dev"|"development"|"prod"|"production")
        build_image "$1"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知参数: $1${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 构建完成！${NC}" 