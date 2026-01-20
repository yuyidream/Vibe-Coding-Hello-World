#!/bin/bash

# Hello World 管理后台部署脚本
# 用途：在服务器上部署Flask后端应用

echo "=========================================="
echo "  Hello World 管理后台部署脚本"
echo "=========================================="
echo ""

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用root权限运行此脚本"
    echo "使用命令：sudo bash deploy-backend.sh"
    exit 1
fi

# 设置变量
APP_DIR="/www/wwwroot/hello-world"
BACKEND_DIR="$APP_DIR/backend"
SERVICE_NAME="hello-world-backend"

# 步骤1: 检查Python3
echo "🔍 步骤 1/7: 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "未找到Python3，正在安装..."
    yum install python3 python3-pip -y 2>/dev/null || apt install python3 python3-pip -y
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Python版本: $PYTHON_VERSION"
echo ""

# 步骤2: 创建目录结构
echo "📁 步骤 2/7: 创建目录结构..."
mkdir -p $BACKEND_DIR
mkdir -p $APP_DIR/static
echo "✅ 目录创建完成"
echo ""

# 步骤3: 检查文件
echo "📦 步骤 3/7: 检查项目文件..."
REQUIRED_FILES=("backend/app.py" "backend/database.py" "backend/config.py" "backend/requirements.txt")
MISSING_FILES=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo "❌ 错误：缺少 $MISSING_FILES 个必需文件"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

echo "✅ 所有必需文件检查通过"
echo ""

# 步骤4: 复制文件
echo "📤 步骤 4/7: 复制项目文件..."
cp -r backend/* $BACKEND_DIR/
cp admin.html $APP_DIR/
cp -r static/* $APP_DIR/static/ 2>/dev/null || true

# 设置权限
chown -R www:www $APP_DIR 2>/dev/null || chown -R nginx:nginx $APP_DIR
chmod -R 755 $APP_DIR

echo "✅ 文件复制完成"
echo ""

# 步骤5: 配置环境变量
echo "⚙️  步骤 5/7: 配置环境变量..."

if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "请输入MySQL数据库配置："
    echo "💡 提示：使用内网地址访问RDS更安全更快"
    read -p "MySQL主机地址 (默认192.168.0.243): " MYSQL_HOST
    MYSQL_HOST=${MYSQL_HOST:-192.168.0.243}
    read -p "MySQL端口 (默认3306): " MYSQL_PORT
    MYSQL_PORT=${MYSQL_PORT:-3306}
    read -p "MySQL用户名 (默认root): " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-root}
    read -sp "MySQL密码: " MYSQL_PASSWORD
    echo ""
    read -p "数据库名 (默认hello_world): " MYSQL_DB
    MYSQL_DB=${MYSQL_DB:-hello_world}
    
    # 测试数据库连通性
    echo "🔍 测试数据库连接..."
    if command -v mysql &> /dev/null; then
        mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SELECT 1;" &>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ 数据库连接测试成功"
        else
            echo "⚠️  数据库连接测试失败，请检查配置"
            echo "按回车继续，或Ctrl+C取消"
            read
        fi
    fi
    
    # 生成随机SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    cat > $BACKEND_DIR/.env << EOF
FLASK_ENV=production
SECRET_KEY=$SECRET_KEY
MYSQL_HOST=$MYSQL_HOST
MYSQL_PORT=$MYSQL_PORT
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_DATABASE=$MYSQL_DB
EOF
    
    chmod 600 $BACKEND_DIR/.env
    echo "✅ 环境变量配置完成"
else
    echo "⏭️  环境变量文件已存在，跳过配置"
fi
echo ""

# 步骤6: 安装Python依赖
echo "📥 步骤 6/7: 安装Python依赖..."
cd $BACKEND_DIR

# 升级pip
python3 -m pip install --upgrade pip -q

# 安装依赖
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt -q
    echo "✅ Python依赖安装完成"
else
    echo "❌ 未找到requirements.txt"
    exit 1
fi
echo ""

# 步骤7: 初始化数据库
echo "🗄️  步骤 7/7: 初始化数据库..."
if [ -f "init_db.py" ]; then
    echo "是否需要初始化数据库？(如果是首次部署请选择yes)"
    read -p "初始化数据库? (yes/no): " INIT_DB
    
    if [ "$INIT_DB" = "yes" ] || [ "$INIT_DB" = "y" ]; then
        # 加载环境变量
        export $(cat .env | grep -v '^#' | xargs)
        python3 init_db.py
    else
        echo "⏭️  跳过数据库初始化"
    fi
fi
echo ""

# 创建Systemd服务文件
echo "🔧 创建系统服务..."
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Hello World Backend Service
After=network.target mysql.service

[Service]
Type=simple
User=www
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$BACKEND_DIR/venv/bin:/usr/bin"
EnvironmentFile=$BACKEND_DIR/.env
ExecStart=/usr/bin/python3 -m gunicorn -w 2 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd
systemctl daemon-reload

# 启动服务
echo "🚀 启动服务..."
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

# 检查服务状态
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败"
    echo "查看日志: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

echo ""
echo "=========================================="
echo "  🎉 部署完成！"
echo "=========================================="
echo ""
echo "📋 部署信息："
echo "   应用目录：$APP_DIR"
echo "   后端目录：$BACKEND_DIR"
echo "   服务名称：$SERVICE_NAME"
echo ""
echo "🌐 访问地址："
echo "   主页：http://$(curl -s ifconfig.me)"
echo "   管理后台：http://$(curl -s ifconfig.me)/admin.html"
echo ""
echo "📝 管理命令："
echo "   查看状态：systemctl status $SERVICE_NAME"
echo "   重启服务：systemctl restart $SERVICE_NAME"
echo "   停止服务：systemctl stop $SERVICE_NAME"
echo "   查看日志：journalctl -u $SERVICE_NAME -f"
echo ""
echo "⚠️  下一步："
echo "   1. 配置Nginx反向代理"
echo "   2. 重新加载Nginx配置"
echo ""
echo "=========================================="
