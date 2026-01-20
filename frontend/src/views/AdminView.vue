<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>管理后台</h1>
      <button @click="handleLogout" class="logout-button">退出登录</button>
    </header>

    <div class="admin-content">
      <!-- 配置编辑区域 -->
      <section class="config-section">
        <h2>网站配置</h2>
        <form @submit.prevent="handleUpdateConfig" class="config-form">
          <div class="form-group">
            <label for="mainTitle">主标题</label>
            <input
              id="mainTitle"
              v-model="config.main_title"
              type="text"
              placeholder="请输入主标题"
              required
              :disabled="isLoading"
            />
          </div>
          <div class="form-group">
            <label for="subtitle">副标题</label>
            <input
              id="subtitle"
              v-model="config.sub_title"
              type="text"
              placeholder="请输入副标题"
              required
              :disabled="isLoading"
            />
          </div>
          <button type="submit" class="save-button" :disabled="isLoading">
            {{ isLoading ? '保存中...' : '保存更改' }}
          </button>
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
        </form>
      </section>

      <!-- 访问日志区域 -->
      <section class="logs-section">
        <h2>访问日志（最近 {{ logs.length }} 条）</h2>
        <button @click="loadLogs" class="refresh-button" :disabled="isLoadingLogs">
          {{ isLoadingLogs ? '刷新中...' : '刷新日志' }}
        </button>
        <div class="logs-table-container">
          <table class="logs-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>IP 地址</th>
                <th>访问时间</th>
                <th>User Agent</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id">
                <td>{{ log.id }}</td>
                <td>{{ log.ip_address }}</td>
                <td>{{ formatTime(log.access_time) }}</td>
                <td class="user-agent">{{ log.user_agent }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="logs.length === 0" class="no-logs">暂无访问日志</div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAdminConfig, updateConfig, getAccessLogs, adminLogout } from '@/api/service'
import type { Config, AccessLog } from '@/api/types'

const router = useRouter()
const config = ref<Config>({
  main_title: '',
  sub_title: ''
})
const logs = ref<AccessLog[]>([])
const isLoading = ref(false)
const isLoadingLogs = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// 加载配置
const loadConfig = async () => {
  try {
    const data = await getAdminConfig()
    config.value = data
  } catch (error: any) {
    console.error('加载配置失败:', error)
    if (error.response?.status === 401) {
      router.push('/admin/login')
    }
  }
}

// 加载日志
const loadLogs = async () => {
  isLoadingLogs.value = true
  try {
    const data = await getAccessLogs(100)
    logs.value = data
  } catch (error: any) {
    console.error('加载日志失败:', error)
  } finally {
    isLoadingLogs.value = false
  }
}

// 更新配置
const handleUpdateConfig = async () => {
  isLoading.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    await updateConfig({
      main_title: config.value.main_title,
      sub_title: config.value.sub_title
    })
    successMessage.value = '配置更新成功！'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || '更新失败，请重试'
  } finally {
    isLoading.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await adminLogout()
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    localStorage.removeItem('admin_token')
    router.push('/admin/login')
  }
}

// 格式化时间
const formatTime = (timeStr: string): string => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 页面加载时初始化
onMounted(() => {
  loadConfig()
  loadLogs()
})
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.admin-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.admin-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.logout-button {
  padding: 10px 20px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.admin-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.config-section,
.logs-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.config-section h2,
.logs-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.config-form {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #555;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.save-button,
.refresh-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s;
}

.save-button:hover:not(:disabled),
.refresh-button:hover:not(:disabled) {
  opacity: 0.9;
}

.save-button:disabled,
.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-button {
  margin-bottom: 20px;
}

.success-message {
  margin-top: 15px;
  padding: 12px;
  background-color: #d4edda;
  color: #155724;
  border-radius: 6px;
  font-size: 14px;
}

.error-message {
  margin-top: 15px;
  padding: 12px;
  background-color: #fee;
  color: #c33;
  border-radius: 6px;
  font-size: 14px;
}

.logs-table-container {
  overflow-x: auto;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th,
.logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.logs-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.logs-table td {
  color: #666;
}

.logs-table .user-agent {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-logs {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
}
</style>
