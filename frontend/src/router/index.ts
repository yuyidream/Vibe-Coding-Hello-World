import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/admin/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

// 路由守卫：保护需要认证的页面
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  
  if (to.meta.requiresAuth && !token) {
    // 需要认证但没有 token，跳转到登录页
    next('/admin/login')
  } else if (to.path === '/admin/login' && token) {
    // 已登录用户访问登录页，跳转到管理后台
    next('/admin')
  } else {
    next()
  }
})

export default router
