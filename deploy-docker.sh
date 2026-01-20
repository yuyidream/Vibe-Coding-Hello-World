#!/bin/bash

set -e

echo "========================================="
echo "Hello World FastAPI Docker 部署脚本"
echo "========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 项目目录
PROJECT_DIR="/www/wwwroot/hello-world"
BACKEND_DIR="$PROJECT_DIR/backend-fastapi"

echo ""
echo -e "${YELLOW}1. 检查 Docker 是否安装...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker 未安装，开始安装...${NC}"
    
    # 更新包索引
    sudo apt-get update
    
    # 安装必要的包
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加 Docker 官方 GPG 密钥
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # 设置 Docker 仓库
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 更新包索引
    sudo apt-get update
    
    # 安装 Docker Engine
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 启动 Docker 服务
    sudo systemctl enable docker
    sudo systemctl start docker
    
    echo -e "${GREEN}✓ Docker 安装完成${NC}"
else
    echo -e "${GREEN}✓ Docker 已安装${NC}"
fi

echo ""
echo -e "${YELLOW}2. 检查 Docker Compose 是否安装...${NC}"
# 检测 Docker Compose 命令形式
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo -e "${GREEN}✓ Docker Compose 已安装 (独立命令)${NC}"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    echo -e "${GREEN}✓ Docker Compose 已安装 (插件)${NC}"
else
    echo -e "${RED}✗ Docker Compose 未安装${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}3. 停止 Systemd 服务（如果存在）...${NC}"
if systemctl is-active --quiet hello-world-fastapi; then
    echo "停止 hello-world-fastapi 服务..."
    sudo systemctl stop hello-world-fastapi
    sudo systemctl disable hello-world-fastapi
    echo -e "${GREEN}✓ Systemd 服务已停止${NC}"
else
    echo -e "${GREEN}✓ Systemd 服务未运行${NC}"
fi

echo ""
echo -e "${YELLOW}4. 进入项目目录...${NC}"
cd "$BACKEND_DIR"
echo -e "${GREEN}✓ 当前目录: $(pwd)${NC}"

echo ""
echo -e "${YELLOW}5. 检查 .env 文件...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}✗ .env 文件不存在！${NC}"
    echo "请先创建 .env 文件并配置环境变量"
    exit 1
else
    echo -e "${GREEN}✓ .env 文件存在${NC}"
fi

echo ""
echo -e "${YELLOW}6. 停止并删除旧容器（如果存在）...${NC}"
$DOCKER_COMPOSE down || true
echo -e "${GREEN}✓ 旧容器已清理${NC}"

echo ""
echo -e "${YELLOW}7. 构建 Docker 镜像...${NC}"
$DOCKER_COMPOSE build --no-cache

echo ""
echo -e "${YELLOW}8. 启动 Docker 容器...${NC}"
$DOCKER_COMPOSE up -d

echo ""
echo -e "${YELLOW}9. 等待服务启动...${NC}"
sleep 5

echo ""
echo -e "${YELLOW}10. 检查容器状态...${NC}"
$DOCKER_COMPOSE ps

echo ""
echo -e "${YELLOW}11. 查看容器日志...${NC}"
$DOCKER_COMPOSE logs --tail=20

echo ""
echo -e "${YELLOW}12. 测试 API...${NC}"
if curl -f http://127.0.0.1:8000/api/health &> /dev/null; then
    echo -e "${GREEN}✓ API 健康检查通过${NC}"
else
    echo -e "${RED}✗ API 健康检查失败${NC}"
    echo "查看完整日志: $DOCKER_COMPOSE logs -f"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "========================================="
echo ""
echo "常用命令："
echo "  查看容器状态:   $DOCKER_COMPOSE ps"
echo "  查看日志:       $DOCKER_COMPOSE logs -f"
echo "  重启容器:       $DOCKER_COMPOSE restart"
echo "  停止容器:       $DOCKER_COMPOSE down"
echo "  进入容器:       $DOCKER_COMPOSE exec fastapi bash"
echo ""
