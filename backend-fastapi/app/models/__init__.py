# -*- coding: utf-8 -*-
"""
Pydantic数据模型
定义API请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ==================== 通用响应模型 ====================

class ResponseModel(BaseModel):
    """通用响应模型"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None

# ==================== 配置相关模型 ====================

class ConfigData(BaseModel):
    """网站配置数据"""
    main_title: str = Field(default="Hello World", description="主标题")
    sub_title: str = Field(default="🎉 欢迎来到我的网站 🎉", description="副标题")

class ConfigUpdateRequest(BaseModel):
    """更新配置请求"""
    main_title: Optional[str] = Field(None, min_length=1, max_length=100)
    sub_title: Optional[str] = Field(None, min_length=1, max_length=200)

# ==================== 管理员相关模型 ====================

class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    password: str = Field(..., min_length=1, max_length=100, description="管理员密码")

class AdminInfo(BaseModel):
    """管理员信息"""
    id: int
    username: str
    created_at: datetime

# ==================== 访问日志相关模型 ====================

class LogCreateRequest(BaseModel):
    """创建访问日志请求"""
    timestamp: Optional[str] = None

class AccessLog(BaseModel):
    """访问日志"""
    id: int
    ip_address: str
    user_agent: Optional[str] = None
    visit_time: datetime
    page_url: Optional[str] = None

class LogListResponse(BaseModel):
    """日志列表响应"""
    success: bool
    data: list[AccessLog]
    total: int
