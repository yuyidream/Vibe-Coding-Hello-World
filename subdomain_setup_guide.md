# Hello World 子域名配置指南

## 目标

将 Hello World 项目迁移到独立子域名：
- **旧地址**: https://renxinayi.com/Vibe-Coding-Hello-World/
- **新地址**: https://helloworld.renxinayi.com/

---

## 执行步骤

### 步骤1: DNS 配置 ⏱️ 5分钟

在域名服务商（华为云/阿里云）添加A记录：

```
类型:   A
主机记录: helloworld
记录值:  123.249.68.162
TTL:    600（10分钟）
```

**验证DNS生效**:
```bash
# 在本地执行
nslookup helloworld.renxinayi.com

# 或
ping helloworld.renxinayi.com
```

---

### 步骤2: 申请SSL证书 ⏱️ 10分钟

```bash
# SSH登录服务器
ssh root@123.249.68.162

# 使用Certbot申请SSL证书
sudo certbot certonly --nginx -d helloworld.renxinayi.com

# 验证证书申请成功
sudo ls -la /etc/letsencrypt/live/helloworld.renxinayi.com/
```

**预期输出**:
```
cert.pem
chain.pem
fullchain.pem
privkey.pem
```

---

### 步骤3: 更新Nginx配置 ⏱️ 5分钟

```bash
# 上传新配置（在本地执行）
scp nginx_helloworld_subdomain.conf root@123.249.68.162:/tmp/

# SSH登录服务器
ssh root@123.249.68.162

# 备份现有配置
sudo cp /etc/nginx/sites-available/renxinayi-admin.conf /etc/nginx/sites-available/renxinayi-admin.conf.backup

# 创建新的独立配置
sudo cp /tmp/nginx_helloworld_subdomain.conf /etc/nginx/sites-available/helloworld.conf

# 启用配置
sudo ln -sf /etc/nginx/sites-available/helloworld.conf /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

---

### 步骤4: 更新前端配置 ⏱️ 15分钟

#### 4.1 更新主页前端配置

```bash
# 编辑 frontend/.env.production
cd e:\projects\Vibe-Coding-Hello-World\frontend
```

**修改 `.env.production`**:
```bash
# 旧配置
# VITE_API_BASE_URL=https://renxinayi.com/Vibe-Coding-Hello-World/api

# 新配置
VITE_API_BASE_URL=https://helloworld.renxinayi.com/api
```

#### 4.2 更新管理后台配置

```bash
# 编辑 frontend-admin/.env.production
cd e:\projects\Vibe-Coding-Hello-World\frontend-admin
```

**修改 `.env.production`**:
```bash
# 旧配置
# VITE_API_BASE_URL=https://renxinayi.com/Vibe-Coding-Hello-World/api

# 新配置
VITE_API_BASE_URL=https://helloworld.renxinayi.com/api
```

#### 4.3 检查 router 配置

**frontend/src/router/index.ts**:
```typescript
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // 确保 BASE_URL 为 '/' 而不是 '/Vibe-Coding-Hello-World/'
  routes
})
```

**frontend-admin/src/router/index.ts**:
```typescript
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // 确保 BASE_URL 为 '/' 而不是 '/admin/'
  routes
})
```

---

### 步骤5: 重新构建前端 ⏱️ 10分钟

```bash
# 构建主页
cd e:\projects\Vibe-Coding-Hello-World\frontend
npm run build

# 构建管理后台
cd e:\projects\Vibe-Coding-Hello-World\frontend-admin
npm run build
```

---

### 步骤6: 部署到服务器 ⏱️ 5分钟

```bash
# 上传主页
scp -r frontend/dist/* root@123.249.68.162:/www/wwwroot/hello-world/frontend/

# 上传管理后台
scp -r frontend-admin/dist/* root@123.249.68.162:/www/wwwroot/hello-world/frontend-admin/

# 设置权限
ssh root@123.249.68.162 "sudo chown -R www-data:www-data /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin && sudo chmod -R 755 /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin"
```

---

### 步骤7: 更新后端CORS配置（可选） ⏱️ 2分钟

如果后端有CORS配置，需要添加新域名：

```bash
# SSH登录服务器
ssh root@123.249.68.162

# 编辑后端配置
cd /www/wwwroot/hello-world/backend-fastapi
sudo nano app/main.py
```

**检查/更新CORS配置**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://helloworld.renxinayi.com",  # 添加新域名
        "https://renxinayi.com",             # 保留旧域名（可选）
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**重启后端**:
```bash
cd /www/wwwroot/hello-world/backend-fastapi
docker-compose restart
```

---

### 步骤8: 验证部署 ⏱️ 5分钟

#### 8.1 访问测试

1. **主页**: https://helloworld.renxinayi.com/
2. **管理后台**: https://helloworld.renxinayi.com/admin/
3. **API文档**: https://helloworld.renxinayi.com/docs
4. **API测试**: https://helloworld.renxinayi.com/api/health

#### 8.2 功能测试

- [ ] 主页加载正常
- [ ] 管理后台登录正常
- [ ] API调用正常
- [ ] 子路由跳转正常
- [ ] SSL证书有效
- [ ] HTTP自动跳转HTTPS

#### 8.3 浏览器测试

```bash
# 测试API
curl -I https://helloworld.renxinayi.com/api/health

# 测试主页
curl -I https://helloworld.renxinayi.com/

# 测试管理后台
curl -I https://helloworld.renxinayi.com/admin/
```

---

### 步骤9: 配置301重定向（可选） ⏱️ 5分钟

如果希望旧URL自动跳转到新域名：

**编辑 `/etc/nginx/sites-available/renxinayi-admin.conf`**:

```nginx
# 添加到 server 块中
location /Vibe-Coding-Hello-World {
    return 301 https://helloworld.renxinayi.com$request_uri;
}

location /Vibe-Coding-Hello-World/ {
    return 301 https://helloworld.renxinayi.com$request_uri;
}
```

**重载Nginx**:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

### 步骤10: 更新文档 ⏱️ 10分钟

更新所有文档中的URL引用：

**需要更新的文件**:
- README.md
- 新版管理后台部署指南.md
- 升级管理后台指南.md
- 数据库配置说明.md
- 技术栈对比报告.md
- 等其他文档

**查找替换**:
```bash
# 旧URL
renxinayi.com/Vibe-Coding-Hello-World

# 新URL
helloworld.renxinayi.com
```

---

## 完整的一键执行脚本

我已经创建了自动化脚本 `deploy_subdomain.bat`，可以一键完成步骤4-6。

---

## 回滚方案

如果出现问题，可以快速回滚：

```bash
# 1. 禁用新配置
sudo rm /etc/nginx/sites-enabled/helloworld.conf

# 2. 恢复旧配置
sudo cp /etc/nginx/sites-available/renxinayi-admin.conf.backup /etc/nginx/sites-available/renxinayi-admin.conf

# 3. 重载Nginx
sudo nginx -t && sudo systemctl reload nginx

# 4. 恢复前端配置（重新构建旧版本）
```

---

## 时间估算

| 步骤 | 时间 | 难度 |
|------|------|------|
| DNS配置 | 5分钟 | ⭐ |
| SSL证书 | 10分钟 | ⭐⭐ |
| Nginx配置 | 5分钟 | ⭐ |
| 前端配置 | 15分钟 | ⭐⭐ |
| 构建部署 | 15分钟 | ⭐ |
| 验证测试 | 10分钟 | ⭐ |
| **总计** | **约60分钟** | |

---

## 注意事项

1. **DNS生效时间**: 10分钟-24小时（通常10分钟内）
2. **SSL证书**: 必须等DNS生效后才能申请
3. **旧URL**: 建议保留301重定向3-6个月
4. **缓存清理**: 部署后清理浏览器缓存
5. **备份**: 执行前务必备份配置和数据

---

## 优势对比

### 旧地址
```
❌ https://renxinayi.com/Vibe-Coding-Hello-World/
❌ https://renxinayi.com/Vibe-Coding-Hello-World/admin/
❌ https://renxinayi.com/Vibe-Coding-Hello-World/api
```

### 新地址
```
✅ https://helloworld.renxinayi.com/
✅ https://helloworld.renxinayi.com/admin/
✅ https://helloworld.renxinayi.com/api
```

**优势**:
- ✅ URL更简洁
- ✅ 完全独立
- ✅ 易于迁移
- ✅ 易于管理
- ✅ 更专业

---

## 准备好开始了吗？

执行 `deploy_subdomain.bat` 即可自动完成大部分步骤！
