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
    
    # 应用配置
    APP_NAME = "Hello World API"
    APP_VERSION = "2.0.0"
    
    # 安全密钥（用于JWT签名）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT配置
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24小时
    
    # MySQL数据库配置
    # 从环境变量读取，如果没有则使用默认值
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'hello_world'
    
    # 数据库连接池配置
    MYSQL_POOL_SIZE = 5
    MYSQL_POOL_RECYCLE = 3600
    MYSQL_POOL_TIMEOUT = 30
    
    # CORS配置
    CORS_ORIGINS = ['*']  # 生产环境应该限制为具体域名
    CORS_ALLOW_CREDENTIALS = True
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'app.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # API配置
    API_PREFIX = "/api"
    API_DOCS_URL = "/api/docs"
    API_REDOC_URL = "/api/redoc"
    
    @staticmethod
    def get_mysql_uri():
        """获取MySQL连接URI"""
        return f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}?charset=utf8mb4"
    
    @staticmethod
    def get_database_config():
        """获取数据库配置字典"""
        return {
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE,
            'charset': 'utf8mb4'
        }


# 开发环境配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    RELOAD = True  # 自动重载


# 生产环境配置
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    RELOAD = False
    
    # 生产环境必须设置随机的SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")
    
    # 生产环境限制CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else ['*']


# 测试环境配置
class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # 测试数据库（可选）
    MYSQL_DATABASE = 'hello_world_test'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# 获取当前环境配置
def get_config():
    """获取当前环境的配置类"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)
