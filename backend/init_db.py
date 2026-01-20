# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于首次部署时初始化数据库表和默认数据
"""

import sys
import os
from getpass import getpass

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database import Database
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    print("=" * 50)
    print("Hello World 管理后台 - 数据库初始化")
    print("=" * 50)
    print()
    
    # 显示数据库配置
    print("当前数据库配置：")
    print(f"  主机: {Config.MYSQL_HOST}")
    print(f"  端口: {Config.MYSQL_PORT}")
    print(f"  用户: {Config.MYSQL_USER}")
    print(f"  数据库: {Config.MYSQL_DATABASE}")
    print()
    
    # 确认是否继续
    confirm = input("确认要初始化数据库吗? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("操作已取消")
        return
    
    # 询问管理员密码
    print()
    print("设置管理员密码（默认用户名: admin）")
    password = getpass("请输入管理员密码（留空使用默认密码 admin123）: ").strip()
    if not password:
        password = 'admin123'
        print("使用默认密码: admin123")
    
    print()
    print("开始初始化...")
    print()
    
    try:
        # 初始化数据库
        db = Database(Config)
        
        # 创建表
        logger.info("创建数据库表...")
        db.init_database()
        logger.info("✓ 数据库表创建成功")
        
        # 插入默认数据
        logger.info("插入默认数据...")
        db.insert_default_data(admin_password=password)
        logger.info("✓ 默认数据插入成功")
        
        print()
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        print()
        print("登录信息：")
        print(f"  用户名: admin")
        print(f"  密码: {password}")
        print()
        print("管理后台地址: http://你的服务器IP/admin.html")
        print()
        print("⚠️  请妥善保管管理员密码！")
        print()
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        print()
        print("初始化失败！请检查：")
        print("1. MySQL服务是否正常运行")
        print("2. 数据库连接配置是否正确")
        print("3. 数据库用户是否有足够权限")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
