<template>
  <div class="home-container">
    <div class="content-wrapper">
      <div v-if="isLoading" class="loading">加载中...</div>
      <div v-else-if="errorMessage" class="error">
        {{ errorMessage }}
      </div>
      <div v-else class="content">
        <h1 class="main-title">{{ config.main_title }}</h1>
        <p class="subtitle">{{ config.sub_title }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getConfig, recordAccessLog } from '@/api/service'
import type { Config } from '@/api/types'

const config = ref<Config>({
  main_title: 'Hello World',
  sub_title: '欢迎来到我的网站'
})
const isLoading = ref(true)
const errorMessage = ref('')

// 加载配置
const loadConfig = async () => {
  try {
    const data = await getConfig()
    config.value = data
  } catch (error: any) {
    console.error('加载配置失败:', error)
    errorMessage.value = '加载失败，请刷新页面重试'
  } finally {
    isLoading.value = false
  }
}

// 页面加载时初始化
onMounted(() => {
  loadConfig()
  // 记录访问日志
  recordAccessLog().catch(err => {
    console.warn('记录访问日志失败:', err)
    // 日志记录失败不影响用户体验，只在控制台警告
  })
})
</script>

<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.content-wrapper {
  text-align: center;
  color: white;
  padding: 40px;
}

.loading,
.error {
  font-size: 18px;
  color: white;
}

.error {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
}

.content {
  animation: fadeIn 0.6s ease-in;
}

.main-title {
  font-size: 64px;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 24px;
  font-weight: 300;
  opacity: 0.9;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .main-title {
    font-size: 40px;
  }
  
  .subtitle {
    font-size: 18px;
  }
}
</style>
