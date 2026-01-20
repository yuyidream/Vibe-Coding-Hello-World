# -*- coding: utf-8 -*-
"""
数据库操作模块
处理MySQL数据库连接和所有数据库操作
FastAPI版本（初期使用同步PyMySQL，后续可改为异步aiomysql）
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
                SELECT id, username, password_hash, created_at
                FROM admin_users
                WHERE username = %s
            """, (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                logger.info(f"管理员登录成功: {username}")
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'created_at': user['created_at']
                }
            
            logger.warning(f"管理员登录失败: {username}")
            return None
    
    def get_admin_by_id(self, admin_id):
        """根据ID获取管理员信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, created_at
                FROM admin_users
                WHERE id = %s
            """, (admin_id,))
            return cursor.fetchone()
    
    def get_admin_by_username(self, username):
        """根据用户名获取管理员信息（包含密码哈希）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, created_at
                FROM admin_users
                WHERE username = %s
            """, (username,))
            return cursor.fetchone()
    
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
    
    def get_access_logs(self, page=1, page_size=50):
        """
        获取访问日志（分页）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页记录数
        
        Returns:
            日志列表
        """
        offset = (page - 1) * page_size
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ip_address, user_agent, access_time
                FROM access_logs
                ORDER BY access_time DESC
                LIMIT %s OFFSET %s
            """, (page_size, offset))
            logs = cursor.fetchall()
            
            # 转换datetime为字符串
            for log in logs:
                if isinstance(log.get('access_time'), datetime):
                    log['access_time'] = log['access_time'].strftime('%Y-%m-%d %H:%M:%S')
            
            return logs
    
    def get_access_logs_count(self):
        """获取日志总数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM access_logs")
            result = cursor.fetchone()
            return result['count'] if result else 0
