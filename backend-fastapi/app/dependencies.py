# -*- coding: utf-8 -*-
"""
依赖注入
用于API路由的依赖，如JWT认证验证
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from .config import Config

logger = logging.getLogger(__name__)

# JWT配置
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24小时

# HTTP Bearer认证
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据（通常包含用户ID等）
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
    
    Returns:
        解码后的数据字典
    
    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    获取当前登录的管理员信息（依赖注入函数）
    
    Args:
        credentials: HTTP Bearer凭证
    
    Returns:
        管理员信息字典
    
    Raises:
        HTTPException: 未登录或令牌无效
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    admin_id = payload.get("admin_id")
    username = payload.get("username")
    
    if admin_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息"
        )
    
    return {
        "admin_id": admin_id,
        "username": username
    }


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实IP地址
    
    Args:
        request: FastAPI请求对象
    
    Returns:
        客户端IP地址
    """
    # 优先从X-Real-IP获取（Nginx配置）
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    
    # 其次从X-Forwarded-For获取
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    
    # 最后使用直接连接IP
    return request.client.host if request.client else '0.0.0.0'
