# -*- coding: utf-8 -*-
"""
数据库操作模块
处理MySQL数据库连接和所有数据库操作
"""

import pymysql
from pymysql import cursors
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Database:
    """数据库管理类"""
    
    def __init__(self, config):
        """初始化数据库连接配置"""
        self.config = {
            'host': config.MYSQL_HOST,
            'port': config.MYSQL_PORT,
            'user': config.MYSQL_USER,
            'password': config.MYSQL_PASSWORD,
            'database': config.MYSQL_DATABASE,
            'charset': 'utf8mb4',
            'cursorclass': cursors.DictCursor,
            'autocommit': False
        }
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = pymysql.connect(**self.config)
            yield connection
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库错误: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    config_key VARCHAR(50) UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 创建管理员用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # 创建访问日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    ip_address VARCHAR(45) NOT NULL,
                    user_agent TEXT,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_access_time (access_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            conn.commit()
            logger.info("数据库表初始化完成")
    
    def insert_default_data(self, admin_password='admin123'):
        """插入默认数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 插入默认配置
            default_configs = [
                ('main_title', 'Hello World'),
                ('sub_title', '🎉 欢迎来到我的网站 🎉')
            ]
            
            for key, value in default_configs:
                cursor.execute("""
                    INSERT INTO config (config_key, config_value)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE config_value = %s
                """, (key, value, value))
            
            # 插入默认管理员账号
            password_hash = generate_password_hash(admin_password)
            try:
                cursor.execute("""
                    INSERT INTO admin_users (username, password_hash)
                    VALUES (%s, %s)
                """, ('admin', password_hash))
                logger.info(f"默认管理员账号创建成功，密码: {admin_password}")
            except pymysql.IntegrityError:
                logger.info("管理员账号已存在，跳过创建")
            
            conn.commit()
    
    # ==================== 配置管理 ====================
    
    def get_config(self, key):
        """获取配置项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_value FROM config WHERE config_key = %s", (key,))
            result = cursor.fetchone()
            return result['config_value'] if result else None
    
    def get_all_config(self):
        """获取所有配置"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT config_key, config_value FROM config")
            results = cursor.fetchall()
            return {row['config_key']: row['config_value'] for row in results}
    
    def update_config(self, key, value):
        """更新配置项"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO config (config_key, config_value)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE config_value = %s, updated_at = CURRENT_TIMESTAMP
            """, (key, value, value))
            conn.commit()
            logger.info(f"配置更新: {key} = {value}")
    
    # ==================== 管理员认证 ====================
    
    def verify_admin(self, username, password):
        """验证管理员账号密码"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash
                FROM admin_users
                WHERE username = %s
            """, (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                logger.info(f"管理员登录成功: {username}")
                return {'id': user['id'], 'username': user['username']}
            
            logger.warning(f"管理员登录失败: {username}")
            return None
    
    def update_admin_password(self, username, new_password):
        """更新管理员密码"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE admin_users
                SET password_hash = %s
                WHERE username = %s
            """, (password_hash, username))
            conn.commit()
            logger.info(f"管理员密码已更新: {username}")
    
    # ==================== 访问日志 ====================
    
    def add_access_log(self, ip_address, user_agent):
        """记录访问日志"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO access_logs (ip_address, user_agent)
                    VALUES (%s, %s)
                """, (ip_address, user_agent))
                conn.commit()
        except Exception as e:
            logger.error(f"记录访问日志失败: {str(e)}")
    
    def get_access_logs(self, limit=100, offset=0):
        """获取访问日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ip_address, user_agent, access_time
                FROM access_logs
                ORDER BY access_time DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            logs = cursor.fetchall()
            
            # 转换datetime为字符串
            for log in logs:
                if isinstance(log['access_time'], datetime):
                    log['access_time'] = log['access_time'].strftime('%Y-%m-%d %H:%M:%S')
            
            return logs
    
    def get_logs_count(self):
        """获取日志总数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM access_logs")
            result = cursor.fetchone()
            return result['count'] if result else 0
