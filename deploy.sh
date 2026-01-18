#!/bin/bash

# 华为云ECS网站部署脚本
# 用途：自动安装Nginx并部署Hello World网站

echo "=========================================="
echo "  华为云ECS网站自动部署脚本"
echo "=========================================="
echo ""

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用root权限运行此脚本"
    echo "使用命令：sudo bash deploy.sh"
    exit 1
fi

# 检测包管理器
if command -v apt-get &> /dev/null; then
    PACKAGE_MANAGER="apt"
elif command -v yum &> /dev/null; then
    PACKAGE_MANAGER="yum"
else
    echo "❌ 错误：无法识别的包管理器"
    exit 1
fi

# 1. 检查Nginx是否已安装
echo "🔍 步骤 1/5: 检查Nginx状态..."
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | grep -oP '(?<=nginx/)\d+\.\d+\.\d+')
    echo "✅ 检测到已安装的Nginx版本：$NGINX_VERSION"
    echo "⏭️  跳过Nginx安装步骤"
    NGINX_INSTALLED=true
else
    echo "📦 未检测到Nginx，将进行安装..."
    NGINX_INSTALLED=false
fi
echo ""

# 2. 安装Nginx（如果需要）
if [ "$NGINX_INSTALLED" = false ]; then
    echo "🔧 步骤 2/5: 安装Nginx..."
    
    # 更新系统包
    echo "正在更新系统包..."
    if [ "$PACKAGE_MANAGER" = "apt" ]; then
        apt update -y
        apt install nginx -y
    else
        yum update -y
        yum install nginx -y
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ Nginx安装失败"
        exit 1
    fi
    echo "✅ Nginx安装完成"
else
    echo "⏭️  步骤 2/5: Nginx已安装，跳过"
fi
echo ""

# 3. 创建网站目录
echo "📁 步骤 3/5: 创建网站目录..."
WEBSITE_DIR="/var/www/hello-world"
mkdir -p $WEBSITE_DIR

# 检查index.html是否存在于当前目录
if [ -f "index.html" ]; then
    cp index.html $WEBSITE_DIR/
    echo "✅ 网站文件已复制到 $WEBSITE_DIR"
else
    echo "⚠️  警告：当前目录未找到index.html"
    echo "请手动上传index.html到服务器"
fi
echo ""

# 4. 配置Nginx
echo "⚙️  步骤 4/5: 配置Nginx..."

# 创建Nginx配置文件
cat > /etc/nginx/sites-available/hello-world <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    root /var/www/hello-world;
    index index.html;
    
    server_name _;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # 安全头设置
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 日志文件
    access_log /var/log/nginx/hello-world-access.log;
    error_log /var/log/nginx/hello-world-error.log;
}
EOF

# 对于CentOS系统，配置路径不同
if [ "$PACKAGE_MANAGER" = "yum" ]; then
    cp /etc/nginx/sites-available/hello-world /etc/nginx/conf.d/hello-world.conf
    # 禁用默认配置
    mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup 2>/dev/null
    cat > /etc/nginx/nginx.conf <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    include /etc/nginx/conf.d/*.conf;
}
EOF
else
    # Ubuntu/Debian系统
    mkdir -p /etc/nginx/sites-enabled
    ln -sf /etc/nginx/sites-available/hello-world /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
fi

# 设置文件权限
chown -R www-data:www-data $WEBSITE_DIR 2>/dev/null || chown -R nginx:nginx $WEBSITE_DIR
chmod -R 755 $WEBSITE_DIR

echo "✅ Nginx配置完成"
echo ""

# 5. 重启Nginx服务
echo "🚀 步骤 5/5: 重启Nginx服务..."

# 测试Nginx配置
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败"
    echo "请检查配置文件语法"
    exit 1
fi

# 检查Nginx是否正在运行
if systemctl is-active --quiet nginx; then
    echo "🔄 Nginx正在运行，重新加载配置..."
    systemctl reload nginx
    if [ $? -eq 0 ]; then
        echo "✅ Nginx配置已重新加载"
    else
        echo "⚠️  重新加载失败，尝试重启..."
        systemctl restart nginx
        if [ $? -eq 0 ]; then
            echo "✅ Nginx服务已重启"
        else
            echo "❌ Nginx重启失败"
            exit 1
        fi
    fi
else
    echo "🚀 启动Nginx服务..."
    systemctl start nginx
    systemctl enable nginx
    if [ $? -eq 0 ]; then
        echo "✅ Nginx服务已启动并设置为开机自启"
    else
        echo "❌ Nginx服务启动失败"
        exit 1
    fi
fi
echo ""

# 获取服务器IP地址
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "无法获取")

echo "=========================================="
echo "  🎉 部署完成！"
echo "=========================================="
echo ""
echo "📋 部署信息："
echo "   网站目录：$WEBSITE_DIR"
echo "   Nginx配置：/etc/nginx/sites-available/hello-world"
echo "   服务器IP：$SERVER_IP"
echo ""
echo "🌐 访问地址："
echo "   http://$SERVER_IP"
echo ""
echo "📝 管理命令："
echo "   查看状态：systemctl status nginx"
echo "   重启服务：systemctl restart nginx"
echo "   停止服务：systemctl stop nginx"
echo "   查看日志：tail -f /var/log/nginx/hello-world-access.log"
echo ""
echo "=========================================="
