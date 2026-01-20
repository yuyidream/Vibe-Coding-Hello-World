#!/bin/bash

# FastAPI 后端部署脚本 - Ubuntu 22.04
# 用途：部署 FastAPI 后端到华为云 ECS

set -e  # 遇到错误立即退出

echo "========================================="
echo "开始部署 FastAPI 后端"
echo "========================================="

# 1. 确保在正确的目录
cd /var/www/hello-world || exit 1

# 2. 备份旧版本（如果存在）
if [ -d "backend-fastapi" ]; then
    echo "备份现有 backend-fastapi 目录..."
    sudo mv backend-fastapi backend-fastapi.backup.$(date +%Y%m%d_%H%M%S) || true
fi

# 3. 创建 backend-fastapi 目录结构
echo "创建目录结构..."
sudo mkdir -p backend-fastapi/app/models
sudo mkdir -p backend-fastapi/app/routers
sudo mkdir -p backend-fastapi/tests

# 4. 设置目录权限
echo "设置目录权限..."
sudo chown -R www-data:www-data backend-fastapi
sudo chmod -R 755 backend-fastapi

# 5. 安装 Python 依赖
echo "安装 Python 依赖..."
cd backend-fastapi
sudo pip3 install fastapi uvicorn pydantic python-jose passlib python-multipart pymysql cryptography python-dotenv werkzeug || {
    echo "警告: 部分依赖安装失败，继续..."
}

# 6. 创建 .env 配置文件
echo "创建 .env 配置文件..."
sudo tee .env > /dev/null <<EOF
# .env配置文件 - 生产环境（华为云）

# 应用环境
FLASK_ENV=production

# 安全密钥（生产环境必须修改）
SECRET_KEY=$(openssl rand -hex 32)

# MySQL数据库配置（华为云RDS内网）
MYSQL_HOST=192.168.0.243
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YU@yi811231
MYSQL_DATABASE=hello_world

# API服务器配置
HOST=0.0.0.0
PORT=8001
RELOAD=false
WORKERS=4

# 日志级别
LOG_LEVEL=INFO

# CORS配置（允许前端域名访问）
CORS_ORIGINS=http://123.249.68.162,http://localhost
EOF

# 7. 设置 .env 文件权限（保护敏感信息）
echo "设置 .env 文件权限..."
sudo chown www-data:www-data .env
sudo chmod 600 .env

echo "========================================="
echo "FastAPI 后端部署准备完成！"
echo "========================================="
echo ""
echo "下一步操作："
echo "1. 请使用 SCP 或 FTP 上传以下文件到服务器的 /var/www/hello-world/backend-fastapi/ 目录："
echo "   - app/__init__.py"
echo "   - app/main.py"
echo "   - app/config.py"
echo "   - app/database.py"
echo "   - app/dependencies.py"
echo "   - app/models/__init__.py"
echo "   - app/routers/__init__.py"
echo "   - app/routers/public.py"
echo "   - app/routers/admin.py"
echo "   - run.py"
echo ""
echo "2. 上传完成后，运行以下命令启动 FastAPI："
echo "   cd /var/www/hello-world/backend-fastapi"
echo "   sudo -u www-data python3 run.py"
echo ""
echo "3. 测试 API："
echo "   curl http://localhost:8001/api/health"
echo ""
