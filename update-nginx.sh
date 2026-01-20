#!/bin/bash

# Nginx配置更新脚本
# 用途：更新Nginx配置以支持API反向代理

echo "=========================================="
echo "  Nginx配置更新脚本"
echo "=========================================="
echo ""

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 错误：请使用root权限运行此脚本"
    echo "使用命令：sudo bash update-nginx.sh"
    exit 1
fi

# 检测Nginx配置目录
if [ -d "/www/server/panel/vhost/nginx" ]; then
    # 宝塔面板
    NGINX_CONF_DIR="/www/server/panel/vhost/nginx"
    NGINX_CONF_FILE="$NGINX_CONF_DIR/123.249.68.162.conf"
    echo "检测到宝塔面板Nginx"
elif [ -d "/etc/nginx/sites-available" ]; then
    # Ubuntu/Debian
    NGINX_CONF_DIR="/etc/nginx/sites-available"
    NGINX_CONF_FILE="$NGINX_CONF_DIR/hello-world"
    echo "检测到系统Nginx (Ubuntu/Debian)"
elif [ -d "/etc/nginx/conf.d" ]; then
    # CentOS
    NGINX_CONF_DIR="/etc/nginx/conf.d"
    NGINX_CONF_FILE="$NGINX_CONF_DIR/hello-world.conf"
    echo "检测到系统Nginx (CentOS)"
else
    echo "❌ 错误：未找到Nginx配置目录"
    exit 1
fi

echo "配置文件位置：$NGINX_CONF_FILE"
echo ""

# 备份现有配置
if [ -f "$NGINX_CONF_FILE" ]; then
    BACKUP_FILE="${NGINX_CONF_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$NGINX_CONF_FILE" "$BACKUP_FILE"
    echo "✅ 已备份现有配置到：$BACKUP_FILE"
fi

# 复制新配置
if [ -f "nginx-backend.conf" ]; then
    cp nginx-backend.conf "$NGINX_CONF_FILE"
    echo "✅ 配置文件已更新"
else
    echo "❌ 错误：未找到nginx-backend.conf文件"
    exit 1
fi

# 如果是Ubuntu/Debian，创建软链接
if [ -d "/etc/nginx/sites-enabled" ]; then
    ln -sf "$NGINX_CONF_FILE" "/etc/nginx/sites-enabled/"
    echo "✅ 已创建软链接"
fi

echo ""
echo "🔍 测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx配置测试通过"
    echo ""
    echo "🔄 重新加载Nginx..."
    systemctl reload nginx || nginx -s reload
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx重新加载成功"
    else
        echo "❌ Nginx重新加载失败"
        exit 1
    fi
else
    echo "❌ Nginx配置测试失败"
    echo "正在恢复备份配置..."
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$NGINX_CONF_FILE"
        echo "✅ 已恢复备份配置"
    fi
    exit 1
fi

echo ""
echo "=========================================="
echo "  ✅ 配置更新完成！"
echo "=========================================="
echo ""
echo "🌐 现在可以访问："
echo "   主页：http://123.249.68.162"
echo "   管理后台：http://123.249.68.162/admin.html"
echo ""
echo "💡 提示："
echo "   - API地址：http://123.249.68.162/api/"
echo "   - 静态文件：http://123.249.68.162/static/"
echo ""
