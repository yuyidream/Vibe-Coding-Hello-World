# Flask → FastAPI + 原生JS → Vue 3 改造方案

## 📋 改造目标

1. **后端**：Flask → FastAPI（更好的性能、自动API文档、异步支持）
2. **前端**：原生JavaScript → Vue 3（组件化、响应式、更好的维护性）

---

## 第一阶段：后端 Flask → FastAPI

### 1. 项目结构对比

#### 当前Flask结构：
```
backend/
├── app.py              # Flask主应用（306行）
├── config.py           # 配置文件
├── database.py         # 数据库操作
├── init_db.py          # 数据库初始化
└── requirements.txt    # 依赖
```

#### 新FastAPI结构：
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI主应用
│   ├── config.py         # 配置（复用）
│   ├── database.py       # 数据库（改造为支持异步）
│   ├── models/           # Pydantic数据模型
│   │   ├── __init__.py
│   │   ├── schemas.py
│   ├── routers/          # API路由（分模块）
│   │   ├── __init__.py
│   │   ├── public.py     # 公开API
│   │   └── admin.py      # 管理API
│   ├── dependencies.py   # 依赖注入
│   └── utils.py          # 工具函数
├── tests/                # 测试
├── init_db.py            # 数据库初始化
└── requirements.txt      # 新依赖
```

### 2. 核心改动说明

#### 2.1 依赖变化

**移除：**
- `flask`
- `flask-cors`

**新增：**
- `fastapi` - Web框架
- `uvicorn` - ASGI服务器
- `pydantic` - 数据验证
- `aiomysql` - 异步MySQL驱动（可选，初期可继续用pymysql）
- `python-jose` - JWT认证
- `passlib` - 密码哈希

#### 2.2 主要API端点映射

| Flask路由 | FastAPI路由 | 说明 |
|----------|------------|------|
| `/api/health` | `/api/health` | 健康检查 |
| `/api/config` | `/api/config` | 获取配置 |
| `/api/log` | `/api/log` | 记录日志 |
| `/api/admin/login` | `/api/admin/login` | 管理员登录 |
| `/api/admin/logout` | `/api/admin/logout` | 管理员登出 |
| `/api/admin/config` | `/api/admin/config` | 更新配置 |
| `/api/admin/logs` | `/api/admin/logs` | 获取日志 |

#### 2.3 认证方式改变

**Flask（Session）：**
```python
@require_login
def update_config():
    if 'admin_id' not in session:
        return jsonify({'success': False}), 401
```

**FastAPI（JWT）：**
```python
@router.post("/config")
async def update_config(
    config_data: ConfigUpdateRequest,
    current_admin: Admin = Depends(get_current_admin)
):
    # current_admin 从JWT token自动解析
```

### 3. 迁移步骤

#### 步骤1：安装新依赖

```bash
cd backend
pip install -r requirements-fastapi.txt
```

#### 步骤2：复制并改造代码

1. 创建新目录结构
2. 复制`config.py`和`database.py`（暂时不改）
3. 创建FastAPI主应用（`app/main.py`）
4. 创建Pydantic模型（`app/models/`）
5. 创建API路由（`app/routers/`）

#### 步骤3：测试并行运行

```bash
# 旧Flask（端口5000）
gunicorn -w 2 -b 127.0.0.1:5000 app:app

# 新FastAPI（端口8000）
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 步骤4：更新Nginx配置

临时配置，两个后端并行：

```nginx
# 旧Flask API（保留）
location /api-old/ {
    proxy_pass http://127.0.0.1:5000/api/;
}

# 新FastAPI（测试）
location /api-new/ {
    proxy_pass http://127.0.0.1:8000/api/;
}
```

#### 步骤5：切换到FastAPI

测试通过后，修改Nginx配置：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/api/;
}
```

更新Systemd服务：

```ini
[Service]
ExecStart=/usr/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
```

---

## 第二阶段：前端 原生JS → Vue 3

### 1. 项目结构对比

#### 当前结构：
```
.
├── index.html          # 主页（165行，内联CSS和JS）
├── admin.html          # 管理后台（462行，内联CSS和JS）
└── static/
    └── admin.js        # 管理后台逻辑（部分外置）
```

#### 新Vue 3结构：
```
frontend/
├── public/
│   └── index.html      # HTML模板
├── src/
│   ├── main.js         # 入口文件
│   ├── App.vue         # 根组件
│   ├── router/         # 路由
│   │   └── index.js
│   ├── views/          # 页面组件
│   │   ├── Home.vue    # 主页
│   │   └── Admin.vue   # 管理后台
│   ├── components/     # 公共组件
│   │   ├── LoginForm.vue
│   │   ├── ConfigForm.vue
│   │   └── LogTable.vue
│   ├── api/            # API调用
│   │   └── index.js
│   └── stores/         # 状态管理（Pinia）
│       └── admin.js
├── package.json
└── vite.config.js      # Vite配置
```

### 2. 技术栈

- **构建工具**：Vite
- **框架**：Vue 3（Composition API）
- **路由**：Vue Router 4
- **状态管理**：Pinia
- **HTTP客户端**：Axios
- **UI库**：可选（Element Plus / Naive UI）

### 3. 迁移步骤

#### 步骤1：创建Vue 3项目

```bash
# 使用Vite创建项目
npm create vite@latest frontend -- --template vue

cd frontend
npm install

# 安装额外依赖
npm install vue-router@4 pinia axios
```

#### 步骤2：配置开发代理

`vite.config.js`：

```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
}
```

#### 步骤3：创建API服务

`src/api/index.js`：

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
});

export const getConfig = () => api.get('/config');
export const updateConfig = (data) => api.put('/admin/config', data);
export const login = (data) => api.post('/admin/login', data);
export const getLogs = (params) => api.get('/admin/logs', { params });
```

#### 步骤4：转换页面为Vue组件

**主页 (Home.vue)：**

```vue
<template>
  <div class="home">
    <div class="circle" v-for="i in 3" :key="i"></div>
    <div class="container">
      <h1>{{ config.main_title }}</h1>
      <p class="subtitle">{{ config.sub_title }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getConfig } from '@/api';

const config = ref({
  main_title: 'Hello World',
  sub_title: '🎉 欢迎来到我的网站 🎉'
});

onMounted(async () => {
  try {
    const { data } = await getConfig();
    if (data.success) {
      config.value = data.data;
    }
  } catch (error) {
    console.error('加载配置失败:', error);
  }
});
</script>

<style scoped>
/* 复用原有CSS */
</style>
```

#### 步骤5：构建和部署

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build
```

构建后的文件在`dist/`目录，部署到Nginx：

```nginx
location / {
    root /www/wwwroot/hello-world/frontend/dist;
    try_files $uri $uri/ /index.html;
}
```

---

## 4. 完整迁移时间线

### 阶段1：准备（1天）
- [ ] 创建`backend-fastapi/`目录
- [ ] 安装FastAPI依赖
- [ ] 复制现有代码到新结构

### 阶段2：后端迁移（2-3天）
- [ ] 创建FastAPI主应用
- [ ] 迁移公开API（config, log）
- [ ] 迁移管理API（login, logout, config, logs）
- [ ] 改造认证为JWT
- [ ] 编写测试

### 阶段3：后端测试（1天）
- [ ] 在8000端口并行运行
- [ ] 使用Postman/curl测试所有API
- [ ] 确认与前端兼容

### 阶段4：前端准备（1天）
- [ ] 创建Vue 3项目
- [ ] 配置路由和状态管理
- [ ] 创建API服务层

### 阶段5：前端迁移（3-4天）
- [ ] 转换主页为Vue组件
- [ ] 转换管理后台为Vue组件
- [ ] 拆分为小组件（LoginForm, ConfigForm, LogTable）
- [ ] 样式适配

### 阶段6：集成测试（1-2天）
- [ ] 前后端联调
- [ ] 功能测试
- [ ] UI测试

### 阶段7：部署（1天）
- [ ] 更新Systemd服务
- [ ] 更新Nginx配置
- [ ] 部署Vue构建产物
- [ ] 验证生产环境

**总计：10-14天**

---

## 5. 风险和注意事项

### 风险
1. **认证方式变化**：Session → JWT，需要前端存储token
2. **异步改造**：如果使用aiomysql，database.py需要大改
3. **API兼容性**：确保响应格式一致

### 注意事项
1. **渐进式迁移**：两个版本并行，逐步切换
2. **保留备份**：旧代码不要删除，打上tag
3. **文档更新**：及时更新部署文档
4. **自动化测试**：为新API编写测试

---

## 6. 快速开始

### 方案A：完全重写（推荐用于新项目）

```bash
# 1. 创建新项目
mkdir hello-world-v2
cd hello-world-v2

# 2. 后端
mkdir backend && cd backend
# 复制配置和数据库文件
# 创建FastAPI应用

# 3. 前端
npm create vite@latest frontend -- --template vue
cd frontend && npm install

# 4. 开发
# 后端：uvicorn app.main:app --reload
# 前端：npm run dev
```

### 方案B：逐步迁移（推荐用于现有项目）

```bash
# 1. 在当前项目创建新目录
mkdir backend-fastapi
mkdir frontend-vue

# 2. 并行开发
# 新后端在8000端口
# 旧后端在5000端口
# 前端开发服务器在5173端口

# 3. 测试通过后替换
```

---

## 7. 文件清单

已创建的文件：
- ✅ `backend/requirements-fastapi.txt` - FastAPI依赖
- ✅ `backend-fastapi/app/main.py` - FastAPI主应用
- ✅ `backend-fastapi/app/models/__init__.py` - Pydantic模型
- ✅ `backend-fastapi/app/routers/public.py` - 公开API路由

待创建的文件：
- ⏳ `backend-fastapi/app/routers/admin.py` - 管理API路由
- ⏳ `backend-fastapi/app/dependencies.py` - JWT认证依赖
- ⏳ `backend-fastapi/app/routers/__init__.py`
- ⏳ 前端Vue 3项目（完整）

---

**下一步：您想继续创建剩余的FastAPI文件，还是先创建Vue 3前端项目？**
