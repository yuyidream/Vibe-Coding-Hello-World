# -*- coding: utf-8 -*-
"""
FastAPI应用主文件
提供API接口和路由处理
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from .config import Config
from .routers import public, admin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="Hello World API",
    description="Hello World 网站管理后台 API",
    version="2.0.0",
    docs_url="/api/docs",      # Swagger UI
    redoc_url="/api/redoc",    # ReDoc
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(public.router, prefix="/api", tags=["公开API"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理后台"])

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "success": True,
        "message": "Hello World API",
        "version": "2.0.0",
        "docs": "/api/docs"
    }

# 健康检查
@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "success": True,
        "message": "API运行正常",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )
