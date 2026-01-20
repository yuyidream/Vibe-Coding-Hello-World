# -*- coding: utf-8 -*-
"""
管理后台API路由
需要JWT认证的管理员接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from ..models import (
    ResponseModel, 
    AdminLoginRequest, 
    ConfigUpdateRequest,
    AccessLog
)
from ..dependencies import get_current_admin, create_access_token, get_client_ip
from ..database import Database
from ..config import Config
from werkzeug.security import check_password_hash
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化数据库
db = Database(Config)


@router.post("/login")
async def admin_login(request: Request, login_data: AdminLoginRequest):
    """
    管理员登录
    
    只验证密码，默认用户名为 admin
    """
    try:
        # 使用固定用户名 "admin" 验证密码
        admin = db.verify_admin("admin", login_data.password)
        
        if not admin:
            # 记录失败的登录尝试
            ip_address = get_client_ip(request)
            logger.warning(f"登录失败: admin from {ip_address}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="密码错误"
            )
        
        # 创建JWT令牌
        access_token = create_access_token(
            data={
                "admin_id": admin['id'],
                "username": admin['username']
            },
            expires_delta=timedelta(hours=24)
        )
        
        # 记录成功的登录
        ip_address = get_client_ip(request)
        logger.info(f"管理员登录成功: {admin['username']} from {ip_address}")
        
        return {
            "success": True,
            "message": "登录成功",
            "data": {
                "token": access_token,
                "admin": {
                    "id": admin['id'],
                    "username": admin['username']
                }
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )


@router.post("/logout")
async def admin_logout(current_admin: dict = Depends(get_current_admin)):
    """
    管理员登出
    
    JWT是无状态的，登出主要是让前端删除token
    """
    logger.info(f"管理员登出: {current_admin['username']}")
    
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get("/config")
async def get_admin_config(current_admin: dict = Depends(get_current_admin)):
    """
    获取网站配置（管理员）
    
    与公开API相同，但需要认证
    """
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置失败"
        )


@router.put("/config")
async def update_config(
    config_data: ConfigUpdateRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """
    更新网站配置
    
    只有登录的管理员才能更新配置
    """
    try:
        updates = {}
        
        if config_data.main_title is not None:
            updates['main_title'] = config_data.main_title
        
        if config_data.sub_title is not None:
            updates['sub_title'] = config_data.sub_title
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有要更新的内容"
            )
        
        # 更新配置
        for key, value in updates.items():
            db.update_config(key, value)
        
        logger.info(f"配置已更新 by {current_admin['username']}: {updates}")
        
        return {
            "success": True,
            "message": "配置更新成功",
            "data": updates
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新配置失败"
        )


@router.get("/logs")
async def get_logs(
    page: int = 1,
    page_size: int = 50,
    current_admin: dict = Depends(get_current_admin)
):
    """
    获取访问日志
    
    支持分页查询
    """
    try:
        # 参数验证
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 50
        
        # 获取日志
        logs = db.get_access_logs(page=page, page_size=page_size)
        total = db.get_access_logs_count()
        
        return {
            "success": True,
            "data": logs,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取日志失败"
        )


@router.get("/profile")
async def get_admin_profile(current_admin: dict = Depends(get_current_admin)):
    """
    获取当前管理员信息
    """
    try:
        admin_info = db.get_admin_by_id(current_admin['admin_id'])
        
        if not admin_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="管理员信息不存在"
            )
        
        return {
            "success": True,
            "data": {
                "id": admin_info['id'],
                "username": admin_info['username'],
                "created_at": admin_info['created_at'].isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取管理员信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取信息失败"
        )
