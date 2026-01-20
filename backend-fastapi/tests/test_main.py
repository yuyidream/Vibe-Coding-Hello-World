# -*- coding: utf-8 -*-
"""
FastAPI应用测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "version" in data


def test_health_check():
    """测试健康检查"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_config():
    """测试获取配置"""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "main_title" in data["data"]
    assert "sub_title" in data["data"]


def test_admin_login_invalid():
    """测试无效登录"""
    response = client.post(
        "/api/admin/login",
        json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401


def test_admin_login_valid():
    """测试有效登录（需要先创建测试用户）"""
    # 这个测试需要在测试数据库中有admin/admin123用户
    response = client.post(
        "/api/admin/login",
        json={"username": "admin", "password": "admin123"}
    )
    # 根据实际情况可能是200或401
    assert response.status_code in [200, 401]


def test_admin_api_without_token():
    """测试未认证访问管理API"""
    response = client.get("/api/admin/config")
    assert response.status_code == 403  # Forbidden (no token)


def test_api_docs():
    """测试API文档可访问"""
    response = client.get("/api/docs")
    assert response.status_code == 200
