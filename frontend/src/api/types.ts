// 配置项接口
export interface Config {
  main_title: string
  sub_title: string
}

// 登录请求
export interface LoginRequest {
  password: string
}

// 登录响应
export interface LoginResponse {
  token: string
  admin?: any
}

// 更新配置请求
export interface UpdateConfigRequest {
  main_title?: string
  sub_title?: string
}

// 访问日志接口
export interface AccessLog {
  id: number
  ip_address: string
  access_time: string
  user_agent: string
}

// API 响应通用格式
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  detail?: string
}
