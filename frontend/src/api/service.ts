import apiClient from './config'
import type {
  Config,
  LoginRequest,
  LoginResponse,
  UpdateConfigRequest,
  AccessLog
} from './types'

// ==================== 公开 API ====================

/**
 * 健康检查
 */
export const healthCheck = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

/**
 * 获取配置（公开接口）
 */
export const getConfig = async (): Promise<Config> => {
  const response = await apiClient.get<{ success: boolean; data: Config }>('/config')
  return response.data.data
}

/**
 * 记录访问日志
 */
export const recordAccessLog = async (): Promise<void> => {
  await apiClient.post('/log')
}

// ==================== 管理员 API ====================

/**
 * 管理员登录
 */
export const adminLogin = async (password: string): Promise<LoginResponse> => {
  const response = await apiClient.post<{ success: boolean; data: LoginResponse }>('/admin/login', {
    password
  })
  return response.data.data
}

/**
 * 管理员登出
 */
export const adminLogout = async (): Promise<void> => {
  await apiClient.post('/admin/logout')
}

/**
 * 获取配置（需要认证）
 */
export const getAdminConfig = async (): Promise<Config> => {
  const response = await apiClient.get<{ success: boolean; data: Config }>('/admin/config')
  return response.data.data
}

/**
 * 更新配置
 */
export const updateConfig = async (data: UpdateConfigRequest): Promise<Config> => {
  const response = await apiClient.put<{ success: boolean; data: Config }>('/admin/config', data)
  return response.data.data
}

/**
 * 获取访问日志
 */
export const getAccessLogs = async (limit: number = 100): Promise<AccessLog[]> => {
  const response = await apiClient.get<{ success: boolean; data: AccessLog[] }>('/admin/logs', {
    params: { limit }
  })
  return response.data.data
}
