import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { setupI18n } from './locales'
import './styles/index.scss'

const app = createApp(App)

// Pinia 状态管理
app.use(createPinia())

// 路由
app.use(router)

// 国际化
setupI18n(app)

app.mount('#app')
