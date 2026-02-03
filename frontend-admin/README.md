# Hello World 企业级管理后台

基于 **Vben Admin** 风格 + **Ant Design Vue** + **vue-i18n** 的现代化管理后台。

## ✨ 特性

- 🎨 **Ant Design Vue** - 企业级 UI 组件库
- 🌍 **国际化** - 支持中文/英文切换（vue-i18n）
- 🔐 **JWT 认证** - 安全的 Token 认证
- 📱 **响应式设计** - 完美适配桌面和移动端
- 🎯 **TypeScript** - 类型安全
- ⚡ **Vite** - 极速的开发体验
- 📦 **组件自动导入** - unplugin-vue-components
- 🔄 **Pinia** - 现代化的状态管理

## 📦 技术栈

- Vue 3.4+
- TypeScript 5.3+
- Vite 5.0+
- Ant Design Vue 4.1+
- Vue Router 4.2+
- Pinia 2.1+
- vue-i18n 9.9+
- Axios
- Day.js

## 🚀 快速开始

### 安装依赖

\`\`\`bash
cd frontend-admin
npm install
\`\`\`

### 开发

\`\`\`bash
npm run dev
\`\`\`

访问: http://localhost:5174

### 构建

\`\`\`bash
npm run build
\`\`\`

构建产物在 `dist/` 目录。

### 类型检查

\`\`\`bash
npm run type-check
\`\`\`

## 📁 项目结构

\`\`\`
frontend-admin/
├── src/
│   ├── api/              # API 接口
│   │   ├── index.ts      # axios 封装
│   │   └── admin.ts      # 管理后台 API
│   ├── assets/           # 静态资源
│   ├── layouts/          # 布局组件
│   │   └── BasicLayout.vue  # 基础布局
│   ├── locales/          # 国际化
│   │   ├── index.ts
│   │   └── lang/
│   │       ├── zh-CN.ts  # 中文
│   │       └── en-US.ts  # 英文
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # Pinia 状态管理
│   │   └── user.ts       # 用户状态
│   ├── styles/           # 全局样式
│   │   └── index.scss
│   ├── views/            # 页面组件
│   │   ├── login/        # 登录页
│   │   ├── dashboard/    # 仪表盘
│   │   ├── content/      # 内容管理
│   │   └── logs/         # 访问日志
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── index.html
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
└── package.json
\`\`\`

## 🎯 功能模块

### 1. 登录系统
- JWT Token 认证
- 密码登录
- 自动跳转
- 国际化支持

### 2. 仪表盘
- 总访问量统计
- 今日访问量
- 快捷操作入口

### 3. 内容管理
- 编辑主页标题
- 编辑副标题
- 实时保存

### 4. 访问日志
- 日志列表
- 分页查询
- 时间格式化
- IP 地址显示
- User Agent 显示

## 🌍 国际化

支持语言：
- 中文（zh-CN）
- 英文（en-US）

切换语言：登录页面右下角可切换语言。

添加新语言：
1. 在 `src/locales/lang/` 目录下创建新的语言文件
2. 在 `src/locales/index.ts` 中注册新语言
3. 在 `LOCALE_OPTIONS` 中添加选项

## 🔐 权限系统

- 路由守卫：自动检查登录状态
- Token 验证：所有请求自动携带 Token
- 401 处理：自动跳转到登录页
- 403 处理：权限不足提示

## 📝 API 接口

### 登录
\`\`\`typescript
POST /api/admin/login
Body: { password: string }
Response: { success: boolean, data: { token: string, admin: {...} } }
\`\`\`

### 获取配置
\`\`\`typescript
GET /api/admin/config
Headers: { Authorization: 'Bearer <token>' }
Response: { success: boolean, data: { main_title: string, sub_title: string } }
\`\`\`

### 更新配置
\`\`\`typescript
PUT /api/admin/config
Headers: { Authorization: 'Bearer <token>' }
Body: { main_title: string, sub_title: string }
Response: { success: boolean }
\`\`\`

### 获取日志
\`\`\`typescript
GET /api/admin/logs?page=1&page_size=20
Headers: { Authorization: 'Bearer <token>' }
Response: { success: boolean, data: [...], pagination: {...} }
\`\`\`

## 🎨 主题定制

修改 `src/styles/index.scss` 可自定义全局样式。

Ant Design Vue 主题通过 CSS 变量自定义。

## 📦 部署

### 构建生产版本

\`\`\`bash
npm run build
\`\`\`

### 部署到服务器

将 `dist/` 目录下的所有文件上传到服务器的指定目录。

Nginx 配置示例：

\`\`\`nginx
location /Vibe-Coding-Hello-World/admin {
    alias /www/wwwroot/hello-world/frontend-admin;
    index index.html;
    try_files $uri $uri/ /Vibe-Coding-Hello-World/admin/index.html;
}
\`\`\`

## 📄 License

MIT

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
