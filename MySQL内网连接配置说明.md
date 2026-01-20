# MySQL内网连接配置说明

## 📋 您的MySQL配置信息

- **内网地址**：`192.168.0.243`
- **端口**：`3306`
- **连接类型**：内网连接（VPC内部）

---

## ✅ 内网连接的优势

相比公网连接，使用内网地址有以下优势：

1. **更安全** 🔐
   - 数据库不暴露到公网
   - 只能从同一VPC内访问
   - 减少被攻击风险

2. **更快速** ⚡
   - 内网传输延迟低
   - 带宽更高
   - 不受公网波动影响

3. **更经济** 💰
   - 不消耗公网流量
   - 无需配置公网IP
   - 降低成本

---

## 🔧 配置步骤

### 步骤1：确认网络连通性

确保您的ECS服务器和RDS在同一VPC：

```bash
# SSH登录ECS服务器
ssh root@123.249.68.162

# 测试内网连通性
ping 192.168.0.243

# 测试MySQL端口
telnet 192.168.0.243 3306
# 或使用
nc -zv 192.168.0.243 3306
```

**预期结果**：
- ping能通（有响应）
- telnet/nc能连接到3306端口

### 步骤2：配置环境变量

在服务器上创建 `.env` 文件：

```bash
cd /www/wwwroot/hello-world/backend

cat > .env << 'EOF'
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here-change-this

# MySQL配置（使用内网地址）
MYSQL_HOST=192.168.0.243
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=hello_world
EOF

# 设置文件权限
chmod 600 .env
```

**重要提示**：
- 将 `SECRET_KEY` 改为随机字符串
- 将 `MYSQL_PASSWORD` 改为您的实际密码
- 将 `MYSQL_USER` 改为您的实际用户名（如果不是root）

### 步骤3：生成随机密钥

```bash
# 生成随机SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
```

复制输出的字符串，替换 `.env` 文件中的 `SECRET_KEY`。

### 步骤4：测试数据库连接

```bash
cd /www/wwwroot/hello-world/backend

# 测试连接
python3 << 'PYEOF'
import pymysql

try:
    conn = pymysql.connect(
        host='192.168.0.243',
        port=3306,
        user='root',
        password='你的密码',
        database='hello_world',
        charset='utf8mb4'
    )
    print("✅ 数据库连接成功！")
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")
PYEOF
```

### 步骤5：创建数据库（如果尚未创建）

```bash
# 连接MySQL
mysql -h 192.168.0.243 -u root -p

# 在MySQL命令行中执行
CREATE DATABASE hello_world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

---

## 🚀 完整部署配置示例

### 环境变量文件 (.env)

```bash
# Flask环境
FLASK_ENV=production

# 安全密钥（必须修改为随机值）
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef

# MySQL数据库配置（内网连接）
MYSQL_HOST=192.168.0.243
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YourStrongPassword123!
MYSQL_DATABASE=hello_world
```

### 部署脚本配置

在运行 `deploy-backend.sh` 时，脚本会提示输入MySQL信息：

```
请输入MySQL数据库配置：
MySQL主机地址: 192.168.0.243
MySQL端口 (默认3306): 3306
MySQL用户名: root
MySQL密码: [输入您的密码]
数据库名 (默认hello_world): hello_world
```

---

## 🔍 网络配置检查

### 检查ECS和RDS是否在同一VPC

1. **登录华为云控制台**
2. **检查ECS VPC**：
   - 进入 ECS 控制台
   - 查看您的ECS实例
   - 记录VPC名称和子网

3. **检查RDS VPC**：
   - 进入 RDS 控制台
   - 查看您的MySQL实例
   - 记录VPC名称和子网

4. **确认一致性**：
   - ECS和RDS必须在同一个VPC
   - 建议在同一个子网（但不强制）

### 如果不在同一VPC

需要进行VPC对等连接或使用云连接服务，请参考华为云文档。

---

## 🛡️ 安全组配置

### RDS安全组规则

确保RDS的安全组允许ECS访问：

1. **进入RDS控制台**
2. **点击实例 → 安全组**
3. **添加入方向规则**：
   - **优先级**：1
   - **策略**：允许
   - **协议端口**：TCP 3306
   - **源地址**：
     - 方式1：输入ECS的内网IP
     - 方式2：输入ECS的安全组ID（推荐）
     - 方式3：VPC内网段（如 192.168.0.0/24）

### ECS安全组规则

ECS的出方向规则通常默认允许所有，无需修改。

---

## 📝 配置文件完整示例

### backend/config.py

配置文件已正确实现，会自动读取环境变量：

```python
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'hello_world'
```

只需确保 `.env` 文件配置正确即可。

---

## ✅ 验证配置

### 1. 测试Python连接

```bash
cd /www/wwwroot/hello-world/backend
python3 -c "from database import Database; from config import Config; db = Database(Config); print('数据库配置正确')"
```

### 2. 初始化数据库

```bash
python3 init_db.py
```

### 3. 启动应用

```bash
systemctl start hello-world-backend
systemctl status hello-world-backend
```

### 4. 测试API

```bash
curl http://localhost:5000/api/health
```

---

## 🚨 常见问题

### 问题1：无法连接到数据库

**症状**：`Can't connect to MySQL server`

**排查步骤**：

```bash
# 1. 检查网络连通性
ping 192.168.0.243

# 2. 检查端口
telnet 192.168.0.243 3306

# 3. 检查ECS和RDS是否在同一VPC
# 登录华为云控制台确认

# 4. 检查RDS安全组规则
# 确保允许ECS的IP访问
```

### 问题2：Access denied

**症状**：`Access denied for user 'root'@'xxx.xxx.xxx.xxx'`

**解决方案**：

```bash
# 1. 确认用户名密码正确
# 2. 确认MySQL用户允许从该IP连接
mysql -h 192.168.0.243 -u root -p

# 在MySQL中检查用户权限
SELECT user, host FROM mysql.user;

# 如需创建新用户
CREATE USER 'hello_world'@'%' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON hello_world.* TO 'hello_world'@'%';
FLUSH PRIVILEGES;
```

### 问题3：Database doesn't exist

**解决方案**：

```bash
# 创建数据库
mysql -h 192.168.0.243 -u root -p -e "CREATE DATABASE hello_world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

---

## 💡 最佳实践

### 1. 使用专用数据库用户

不要使用root用户，创建专用用户：

```sql
-- 连接MySQL
mysql -h 192.168.0.243 -u root -p

-- 创建专用用户
CREATE USER 'hello_world_app'@'%' IDENTIFIED BY 'StrongPassword123!';

-- 授予权限
GRANT SELECT, INSERT, UPDATE, DELETE ON hello_world.* TO 'hello_world_app'@'%';

-- 刷新权限
FLUSH PRIVILEGES;
```

然后在 `.env` 中使用：
```
MYSQL_USER=hello_world_app
MYSQL_PASSWORD=StrongPassword123!
```

### 2. 使用强密码

密码建议：
- 至少12个字符
- 包含大小写字母、数字、特殊字符
- 不使用常见单词或生日

### 3. 定期备份

```bash
# 备份数据库
mysqldump -h 192.168.0.243 -u root -p hello_world > backup_$(date +%Y%m%d_%H%M%S).sql

# 或使用华为云RDS自动备份功能
```

### 4. 监控连接

```bash
# 查看当前连接
mysql -h 192.168.0.243 -u root -p -e "SHOW PROCESSLIST;"

# 查看连接数
mysql -h 192.168.0.243 -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
```

---

## 📞 需要帮助？

如果遇到问题，请提供：
1. 错误信息截图
2. ping和telnet测试结果
3. ECS和RDS的VPC配置
4. Python连接测试的错误信息

---

**配置完成后，您的应用将通过安全、快速的内网连接访问MySQL数据库！** ✅
