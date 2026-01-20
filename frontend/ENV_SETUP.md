# 环境变量配置说明

## 📋 文件说明

本项目使用 Vite 的环境变量系统，通过 `.env` 文件管理不同环境的配置。

## 🔧 设置步骤

### 方法1：使用命令行（推荐）

在 `frontend/` 目录下执行：

```bash
# Windows PowerShell
Copy-Item env.development .env.development
Copy-Item env.production .env.production

# Linux/Mac
cp env.development .env.development
cp env.production .env.production
```

### 方法2：手动复制

1. 将 `env.development` 复制为 `.env.development`
2. 将 `env.production` 复制为 `.env.production`

## 📁 文件说明

- `env.development` - 开发环境配置模板
- `env.production` - 生产环境配置模板
- `.env.development` - 实际开发环境配置（不会被提交到 Git）
- `.env.production` - 实际生产环境配置（不会被提交到 Git）

## 🎯 环境变量说明

### VITE_API_BASE_URL
- **开发环境**: `/api` (通过 Vite 代理到本地后端)
- **生产环境**: `/api` (通过 Nginx 反向代理)

### VITE_APP_TITLE
- 应用标题，显示在浏览器标签页

### VITE_ENABLE_DEVTOOLS
- `true`: 启用 Vue DevTools
- `false`: 禁用 Vue DevTools（生产环境推荐）

### VITE_LOG_LEVEL
- `debug`: 显示所有日志
- `error`: 只显示错误日志

## 🚀 使用方式

Vite 会根据运行命令自动选择环境：

```bash
# 开发环境（使用 .env.development）
npm run dev

# 生产构建（使用 .env.production）
npm run build
```

## 📝 注意事项

1. **安全性**: 不要将包含敏感信息的 `.env` 文件提交到 Git
2. **命名规则**: 只有以 `VITE_` 开头的变量才会暴露给客户端代码
3. **修改后重启**: 修改环境变量后需要重启开发服务器

## 🔍 在代码中使用

```typescript
// 获取环境变量
const apiUrl = import.meta.env.VITE_API_BASE_URL
const appTitle = import.meta.env.VITE_APP_TITLE

// 判断环境
const isDev = import.meta.env.DEV
const isProd = import.meta.env.PROD
```

## ✅ 验证配置

启动开发服务器后，在浏览器控制台执行：

```javascript
console.log(import.meta.env)
```

应该能看到所有以 `VITE_` 开头的环境变量。
