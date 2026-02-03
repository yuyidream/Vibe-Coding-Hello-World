import request from './index'

export interface LoginParams {
  password: string
}

export interface LoginResult {
  success: boolean
  message: string
  data: {
    token: string
    admin: {
      id: number
      username: string
    }
  }
}

export interface ConfigData {
  main_title: string
  sub_title: string
}

export interface ConfigResult {
  success: boolean
  data: ConfigData
}

export interface AccessLog {
  id: number
  ip_address: string
  access_time: string
  user_agent: string
}

export interface LogsResult {
  success: boolean
  data: AccessLog[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

// 登录
export function login(data: LoginParams) {
  return request.post<any, LoginResult>('/admin/login', data)
}

// 登出
export function logout() {
  return request.post('/admin/logout')
}

// 获取配置
export function getConfig() {
  return request.get<any, ConfigResult>('/admin/config')
}

// 更新配置
export function updateConfig(data: ConfigData) {
  return request.put('/admin/config', data)
}

// 获取访问日志
export function getLogs(page: number = 1, pageSize: number = 20) {
  return request.get<any, LogsResult>('/admin/logs', {
    params: { page, page_size: pageSize },
  })
}
