# 🚀 子域名快速部署指南

## 域名: helloworld.renxinayi.com

---

## ✅ 已完成的准备工作

1. ✅ 创建了 Nginx 配置文件 (`nginx_helloworld_subdomain.conf`)
2. ✅ 更新了前端配置文件 (`.env.production`)
3. ✅ 创建了一键部署脚本 (`deploy_subdomain.bat`)
4. ✅ 创建了详细部署指南 (`subdomain_setup_guide.md`)

---

## 🎯 快速执行（3步完成）

### 第1步: 配置DNS ⏱️ 2分钟

在域名服务商（华为云/阿里云）控制台：

```
类型:     A
主机记录: helloworld
记录值:   123.249.68.162
TTL:      600
```

**验证**: 
```bash
ping helloworld.renxinayi.com
```

---

### 第2步: 运行部署脚本 ⏱️ 15分钟

```bash
# 在项目根目录执行
deploy_subdomain.bat 123.249.68.162
```

**脚本会自动完成**:
- ✅ 更新前端配置
- ✅ 构建前端和管理后台
- ✅ 上传到服务器
- ✅ 上传Nginx配置

---

### 第3步: 服务器配置 ⏱️ 10分钟

SSH登录服务器后依次执行：

```bash
# 1. 申请SSL证书
sudo certbot certonly --nginx -d helloworld.renxinayi.com

# 2. 安装Nginx配置
sudo cp /tmp/nginx_helloworld_subdomain.conf /etc/nginx/sites-available/helloworld.conf
sudo ln -sf /etc/nginx/sites-available/helloworld.conf /etc/nginx/sites-enabled/

# 3. 测试并重载
sudo nginx -t
sudo systemctl reload nginx

# 4. 设置权限
sudo chown -R www-data:www-data /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin
sudo chmod -R 755 /www/wwwroot/hello-world/frontend /www/wwwroot/hello-world/frontend-admin
```

---

## 🎉 完成！

访问以下地址验证：
- **主页**: https://helloworld.renxinayi.com/
- **管理后台**: https://helloworld.renxinayi.com/admin/
- **API文档**: https://helloworld.renxinayi.com/docs

---

## 📋 可选步骤

### 配置旧URL自动跳转

编辑 `/etc/nginx/sites-available/renxinayi-admin.conf`，添加：

```nginx
# 在 server 块中添加
location /Vibe-Coding-Hello-World {
    return 301 https://helloworld.renxinayi.com$request_uri;
}
```

然后重载：
```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## 🆘 遇到问题？

查看详细文档：
- **完整指南**: `subdomain_setup_guide.md`
- **资源隔离报告**: `resource_isolation_report.md`
- **迁移指南**: `nginx_migration_guide.md`

---

**总耗时**: 约30分钟  
**难度**: ⭐⭐ (简单)
