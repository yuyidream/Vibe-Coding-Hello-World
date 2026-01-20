#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI应用启动脚本
用于开发和生产环境
"""

import uvicorn
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 从环境变量获取配置
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    workers = int(os.getenv("WORKERS", 1))
    
    print(f"🚀 Starting FastAPI application on {host}:{port}")
    print(f"📝 Reload: {reload}")
    print(f"👷 Workers: {workers}")
    print(f"📚 API Docs: http://{host}:{port}/api/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,  # reload模式不支持多worker
        log_level="info",
        access_log=True
    )
