import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { message } from 'ant-design-vue'
import router from '@/router'

// API 基础 URL
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        message.error('登录已过期，请重新登录')
        localStorage.removeItem('admin_token')
        router.push('/login')
      } else if (status === 403) {
        message.error('没有权限访问')
      } else if (status === 500) {
        message.error(data?.detail || '服务器错误')
      } else {
        message.error(data?.detail || '请求失败')
      }
    } else {
      message.error('网络错误，请检查您的网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default service
