#!/usr/bin/env python3
"""
启动新的 FastAPI 应用
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        import uvicorn
        from app.main import app
        from app.core.config import settings
        
        print(f"🚀 启动 {settings.APP_NAME}")
        print(f"📍 地址: http://{settings.HOST}:{settings.PORT}")
        print(f"📚 文档: http://{settings.HOST}:{settings.PORT}/docs")
        print(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
        
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if settings.DEBUG else "warning"
        )
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"❌ 启动失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        sys.exit(1) 