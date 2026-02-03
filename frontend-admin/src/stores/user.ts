import { defineStore } from 'pinia'
import { login as loginApi, logout as logoutApi } from '@/api/admin'
import type { LoginParams } from '@/api/admin'
import router from '@/router'
import { message } from 'ant-design-vue'

interface UserState {
  token: string
  username: string
  isLoggedIn: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('admin_token') || '',
    username: localStorage.getItem('admin_username') || '',
    isLoggedIn: !!localStorage.getItem('admin_token'),
  }),

  actions: {
    async login(params: LoginParams) {
      try {
        const res = await loginApi(params)
        
        if (res.success) {
          this.token = res.data.token
          this.username = res.data.admin.username
          this.isLoggedIn = true
          
          localStorage.setItem('admin_token', res.data.token)
          localStorage.setItem('admin_username', res.data.admin.username)
          
          message.success('登录成功')
          router.push('/dashboard')
        }
      } catch (error) {
        console.error('登录失败:', error)
      }
    },

    async logout() {
      try {
        await logoutApi()
      } catch (error) {
        console.error('登出失败:', error)
      } finally {
        this.token = ''
        this.username = ''
        this.isLoggedIn = false
        
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_username')
        
        router.push('/login')
      }
    },
  },
})
