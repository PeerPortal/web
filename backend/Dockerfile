# PeerPortal AI智能体系统 v2.0 - Docker镜像
# 专为留学规划AI顾问优化

FROM python:3.11-slim

# 构建参数
ARG BUILD_DATE
ARG VCS_REF

# 镜像元数据
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.name="PeerPortal AI Agent" \
      org.label-schema.description="AI-powered study abroad planning system" \
      org.label-schema.version="2.0"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖（包含AI和文档处理相关）
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        wget \
        git \
        # PDF和文档处理
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-chi-sim \
        tesseract-ocr-chi-tra \
        # 图像处理
        libmagic1 \
        # 网络工具
        netcat-openbsd \
        # 清理缓存
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制requirements文件并安装Python依赖
# 优先使用requirements-docker.txt（如果存在）
COPY requirements*.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    if [ -f requirements-docker.txt ]; then \
        echo "Using requirements-docker.txt for Docker build" && \
        pip install --no-cache-dir -r requirements-docker.txt \
        --timeout 300 \
        --retries 5; \
    else \
        echo "Using requirements.txt for Docker build" && \
        pip install --no-cache-dir -r requirements.txt \
        --timeout 300 \
        --retries 5; \
    fi

# 复制应用代码
COPY app/ ./app/
COPY configs/ ./configs/
COPY knowledge_base/ ./knowledge_base/
# 移除测试配置文件，它不是运行时必需的
COPY AI_AGENT_快速入门.md ./

# 创建必要的目录
RUN mkdir -p /app/uploads /app/logs /app/vector_store

# 创建非root用户
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查 - 针对AI Agent API
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# AI Agent系统预热检查
COPY docker-entrypoint.sh /app/
USER root
RUN chmod +x /app/docker-entrypoint.sh
USER appuser

# 启动命令
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]