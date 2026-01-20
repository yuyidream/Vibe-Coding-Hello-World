# -*- coding: utf-8 -*-
"""
公开API路由
不需要登录验证的接口
"""

from fastapi import APIRouter, Request, HTTPException
from ..models import ResponseModel, ConfigData, LogCreateRequest
from ..database import Database
from ..config import Config
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化数据库
db = Database(Config)

def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        return request.client.host if request.client else '0.0.0.0'

@router.get("/config", response_model=dict)
async def get_config():
    """获取网站配置（主标题、副标题）"""
    try:
        configs = db.get_all_config()
        return {
            "success": True,
            "data": {
                "main_title": configs.get('main_title', 'Hello World'),
                "sub_title": configs.get('sub_title', '🎉 欢迎来到我的网站 🎉')
            }
        }
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取配置失败")

@router.post("/log")
async def add_log(request: Request, log_data: LogCreateRequest = None):
    """记录访问日志"""
    try:
        ip_address = get_client_ip(request)
        user_agent = request.headers.get('User-Agent', '')
        
        db.add_access_log(
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "success": True,
            "message": "日志记录成功"
        }
    except Exception as e:
        logger.error(f"记录访问日志失败: {str(e)}")
        # 访问日志失败不应该影响用户体验，返回成功
        return {
            "success": True,
            "message": "日志记录失败，但不影响访问"
        }
