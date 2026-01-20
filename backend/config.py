# -*- coding: utf-8 -*-
"""
配置文件
存储应用程序配置和数据库连接信息
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session配置
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # MySQL数据库配置
    # 从环境变量读取，如果没有则使用默认值（需要在部署时修改）
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'hello_world'
    
    # 数据库连接池配置
    MYSQL_POOL_SIZE = 5
    MYSQL_POOL_RECYCLE = 3600
    
    # CORS配置
    CORS_ORIGINS = ['*']  # 生产环境应该限制为具体域名
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
    
    @staticmethod
    def get_mysql_uri():
        """获取MySQL连接URI"""
        return f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}?charset=utf8mb4"


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # 生产环境必须设置随机的SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
