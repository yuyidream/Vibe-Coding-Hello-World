# Hello World 项目迁移指南

## 当前配置共用情况

### ⚠️ 共用资源

1. **域名**: renxinayi.com
2. **SSL证书**: /etc/letsencrypt/live/renxinayi.com-0001/
3. **Nginx配置**: 单一配置文件包含两个项目

### ❌ 迁移问题

如果将Hello World迁移到其他服务器，会遇到：
- URL变更（renxinayi.com → 新域名）
- SSL证书需重新申请
- 用户访问链接失效
- 无法独立管理配置

---

## 解决方案

### 方案1: 拆分Nginx配置（推荐，已完成）

**优点**: 配置独立管理，易于维护
**缺点**: 仍然共用域名和SSL证书

**文件**:
- `nginx_hello_world.conf` - Hello World独立配置
- `nginx_housekeeping.conf` - 家政平台独立配置
- `nginx_combined.conf` - 当前组合配置（已拆分注释）

### 方案2: 配置子域名（推荐，需执行）

**目标**:
```
hello.renxinayi.com  → Hello World
renxinayi.com        → 家政平台
```

**优点**: 完全独立，可随时迁移
**缺点**: 需要修改DNS和用户访问链接

**执行步骤**:

#### 1. DNS配置

在域名服务商添加A记录：
```
hello.renxinayi.com  A  123.249.68.162
```

#### 2. 申请SSL证书

```bash
# 在服务器上执行
sudo certbot certonly --nginx -d hello.renxinayi.com

# 或使用现有证书（如果支持通配符）
# *.renxinayi.com
```

#### 3. 修改Nginx配置

```nginx
server {
    listen 80;
    server_name hello.renxinayi.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name hello.renxinayi.com;

    ssl_certificate /etc/letsencrypt/live/hello.renxinayi.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hello.renxinayi.com/privkey.pem;

    # 管理后台
    location /admin/ {
        alias /www/wwwroot/hello-world/frontend-admin/;
        try_files $uri $uri/ /admin/index.html;
    }

    # FastAPI 后端
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 主页
    location / {
        alias /www/wwwroot/hello-world/frontend/;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

#### 4. 更新应用配置

**前端** (`frontend/.env.production`):
```bash
VITE_API_BASE_URL=https://hello.renxinayi.com/api
```

**前端管理后台** (`frontend-admin/.env.production`):
```bash
VITE_API_BASE_URL=https://hello.renxinayi.com/api
```

**后端** (`backend-fastapi/.env`):
```bash
# 如果需要CORS配置
CORS_ORIGINS=https://hello.renxinayi.com
```

#### 5. 重新构建和部署

```bash
# 前端
cd frontend
npm run build

# 管理后台
cd frontend-admin
npm run build

# 上传到服务器
scp -r frontend/dist/* root@123.249.68.162:/www/wwwroot/hello-world/frontend/
scp -r frontend-admin/dist/* root@123.249.68.162:/www/wwwroot/hello-world/frontend-admin/

# 重启Nginx
ssh root@123.249.68.162 "sudo nginx -t && sudo systemctl reload nginx"

# 重启后端
ssh root@123.249.68.162 "cd /www/wwwroot/hello-world/backend-fastapi && docker-compose restart"
```

#### 6. 更新文档

更新所有文档中的URL：
- `renxinayi.com/Vibe-Coding-Hello-World/` → `hello.renxinayi.com/`
- `renxinayi.com/Vibe-Coding-Hello-World/admin/` → `hello.renxinayi.com/admin/`
- `renxinayi.com/Vibe-Coding-Hello-World/api` → `hello.renxinayi.com/api`

---

## 方案3: 独立域名（最彻底）

如果有独立域名（如 helloworld.com）：

1. DNS配置A记录指向服务器IP
2. 申请SSL证书
3. 修改Nginx配置（与方案2类似，但用新域名）
4. 更新应用配置和文档

---

## 当前部署方式（临时解决方案）

### 使用组合配置

```bash
# 上传配置到服务器
scp nginx_combined.conf root@123.249.68.162:/tmp/

# 备份现有配置
ssh root@123.249.68.162 "sudo cp /etc/nginx/sites-available/renxinayi-admin.conf /etc/nginx/sites-available/renxinayi-admin.conf.backup"

# 应用新配置
ssh root@123.249.68.162 "sudo cp /tmp/nginx_combined.conf /etc/nginx/sites-available/renxinayi-admin.conf && sudo nginx -t && sudo systemctl reload nginx"
```

**说明**: 这只是将配置拆分为清晰的注释块，仍然共用域名和SSL。

---

## 推荐执行顺序

### 立即执行（已完成）
1. ✅ 拆分Nginx配置文件

### 近期执行（推荐）
2. 🔄 配置子域名 hello.renxinayi.com
3. 🔄 申请SSL证书
4. 🔄 更新Nginx配置使用子域名
5. 🔄 更新应用配置
6. 🔄 更新文档

### 长期考虑
7. 考虑独立域名（如果业务需要）

---

## 迁移到其他服务器的步骤

当有了独立子域名/域名后：

### 1. 在新服务器上部署

```bash
# 克隆项目
git clone <repository> /www/wwwroot/hello-world

# 构建后端
cd /www/wwwroot/hello-world/backend-fastapi
docker-compose up -d --build

# 部署前端（从本地上传构建文件）
# ... 上传frontend/dist 和 frontend-admin/dist
```

### 2. 配置新服务器的Nginx

使用 `nginx_hello_world.conf` 配置

### 3. 修改DNS

将子域名A记录指向新服务器IP

### 4. 迁移SSL证书（或重新申请）

```bash
# 方法1: 复制证书
scp -r /etc/letsencrypt/live/hello.renxinayi.com/ new_server:/etc/letsencrypt/live/

# 方法2: 重新申请
sudo certbot certonly --nginx -d hello.renxinayi.com
```

### 5. 验证和切换

- 验证新服务器正常运行
- 修改DNS生效后，旧服务器自动失效

---

## 总结

**当前问题**: Hello World与家政平台共用域名、SSL证书和Nginx配置

**解决方案**: 
1. ✅ 已拆分Nginx配置（便于管理）
2. 🔄 建议配置子域名（完全独立）

**优先级**: 
- **高**: 配置子域名 hello.renxinayi.com
- **中**: 拆分Nginx配置（已完成）
- **低**: 独立域名（如果需要）

---

**需要执行子域名配置吗？** 这将使Hello World完全独立，可随时迁移到其他服务器而不影响家政平台。
