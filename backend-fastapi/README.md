# FastAPI后端 - Hello World V2

FastAPI版本的Hello World后端API，替代原Flask版本。

## 🚀 特性

- ✅ **FastAPI框架**：现代、快速、基于标准Python类型提示
- ✅ **自动API文档**：Swagger UI 和 ReDoc
- ✅ **JWT认证**：无状态的Token认证
- ✅ **Pydantic验证**：自动数据验证和序列化
- ✅ **类型提示**：完整的类型注解支持
- ✅ **异步支持**：为未来的异步数据库做准备
- ✅ **测试覆盖**：pytest测试框架

## 📋 项目结构

```
backend-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库操作
│   ├── dependencies.py   # JWT认证等依赖
│   ├── models/           # Pydantic数据模型
│   │   └── __init__.py
│   └── routers/          # API路由
│       ├── __init__.py
│       ├── public.py     # 公开API
│       └── admin.py      # 管理API
├── tests/                # 测试文件
│   └── test_main.py
├── requirements-fastapi.txt  # Python依赖
├── run.py                # 启动脚本
├── env.example           # 环境变量示例
└── README.md             # 本文件
```

## 🔧 安装和运行

### 1. 安装依赖

```bash
cd backend-fastapi
pip install -r requirements-fastapi.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp env.example .env

# 编辑.env文件，设置MySQL连接信息
vim .env
```

### 3. 运行应用

#### 开发模式（自动重载）

```bash
python run.py
```

或直接使用uvicorn：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 生产模式

```bash
# 使用环境变量控制
export RELOAD=false
export WORKERS=2
python run.py
```

或：

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
```

### 4. 访问API文档

应用启动后，访问：

- **Swagger UI**: http://127.0.0.1:8000/api/docs
- **ReDoc**: http://127.0.0.1:8000/api/redoc
- **健康检查**: http://127.0.0.1:8000/api/health

## 📡 API端点

### 公开API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API根路径 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/config` | 获取网站配置 |
| POST | `/api/log` | 记录访问日志 |

### 管理API（需要JWT认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login` | 管理员登录 |
| POST | `/api/admin/logout` | 管理员登出 |
| GET | `/api/admin/config` | 获取配置 |
| PUT | `/api/admin/config` | 更新配置 |
| GET | `/api/admin/logs` | 获取访问日志 |
| GET | `/api/admin/profile` | 获取管理员信息 |

## 🔐 认证方式

FastAPI版本使用**JWT (JSON Web Token)**认证，替代Flask的Session。

### 登录获取Token

```bash
curl -X POST "http://127.0.0.1:8000/api/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

响应：

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "admin": {
      "id": 1,
      "username": "admin"
    }
  }
}
```

### 使用Token访问管理API

```bash
curl -X GET "http://127.0.0.1:8000/api/admin/config" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=app tests/

# 运行特定测试文件
pytest tests/test_main.py -v
```

## 🔄 从Flask迁移

### API兼容性

FastAPI版本保持了与Flask版本相同的API接口，但有以下变化：

1. **认证方式**：Session → JWT Token
2. **响应格式**：完全兼容
3. **端口**：Flask(5000) → FastAPI(8000)

### 前端适配

前端需要修改：

1. **存储Token**：登录成功后保存token到localStorage
2. **请求头**：添加 `Authorization: Bearer <token>`
3. **错误处理**：处理401未授权响应

示例（JavaScript）：

```javascript
// 登录
const response = await fetch('/api/admin/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const data = await response.json();
if (data.success) {
  // 保存token
  localStorage.setItem('token', data.data.token);
}

// 使用token访问管理API
const token = localStorage.getItem('token');
fetch('/api/admin/config', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 📦 部署

### 使用Systemd

创建 `/etc/systemd/system/hello-world-backend.service`：

```ini
[Unit]
Description=Hello World FastAPI Backend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/www/wwwroot/hello-world/backend-fastapi
EnvironmentFile=/www/wwwroot/hello-world/backend-fastapi/.env
ExecStart=/usr/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start hello-world-backend
sudo systemctl enable hello-world-backend
sudo systemctl status hello-world-backend
```

### Nginx配置

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 🆚 Flask vs FastAPI 对比

| 特性 | Flask | FastAPI |
|------|-------|---------|
| 认证方式 | Session | JWT Token |
| 数据验证 | 手动 | Pydantic自动 |
| API文档 | 需要手动编写 | 自动生成 |
| 类型提示 | 可选 | 强制 |
| 异步支持 | 有限 | 原生支持 |
| 性能 | 一般 | 更快 |

## 📝 开发注意事项

1. **环境变量**：生产环境必须修改SECRET_KEY
2. **数据库连接**：初期使用同步PyMySQL，后续可改为异步aiomysql
3. **日志**：使用Python标准logging模块
4. **错误处理**：FastAPI自动处理Pydantic验证错误

## 🐛 常见问题

### 1. 端口冲突

如果8000端口被占用，修改 `.env` 文件中的 `PORT` 值。

### 2. MySQL连接失败

检查 `.env` 文件中的MySQL配置是否正确。

### 3. 401未授权

Token可能过期（24小时），需要重新登录。

## 📚 相关文档

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Pydantic文档](https://docs.pydantic.dev/)
- [Uvicorn文档](https://www.uvicorn.org/)

---

**现在开始使用FastAPI构建更好的API！** 🚀
