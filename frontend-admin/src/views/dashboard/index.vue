<template>
  <div class="dashboard">
    <a-page-header :title="t('menu.dashboard')" :sub-title="t('dashboard.welcome')">
      <template #extra>
        <a-button @click="handleRefresh">
          <ReloadOutlined />
          {{ t('common.refresh') }}
        </a-button>
      </template>
    </a-page-header>
    
    <div class="stats-cards">
      <a-card :loading="loading">
        <a-statistic
          :title="t('dashboard.totalVisits')"
          :value="totalVisits"
          :value-style="{ color: '#3f8600' }"
        >
          <template #prefix>
            <LineChartOutlined />
          </template>
        </a-statistic>
      </a-card>
      
      <a-card>
        <a-statistic
          :title="t('dashboard.todayVisits')"
          :value="todayVisits"
          :value-style="{ color: '#1890ff' }"
        >
          <template #prefix>
            <RiseOutlined />
          </template>
        </a-statistic>
      </a-card>
    </div>
    
    <a-card :title="t('dashboard.quickActions')" class="quick-actions">
      <a-space size="large">
        <a-button type="primary" size="large" @click="router.push('/content')">
          <EditOutlined />
          {{ t('dashboard.editContent') }}
        </a-button>
        
        <a-button size="large" @click="router.push('/logs')">
          <FileTextOutlined />
          {{ t('dashboard.viewLogs') }}
        </a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ReloadOutlined,
  LineChartOutlined,
  RiseOutlined,
  EditOutlined,
  FileTextOutlined,
} from '@ant-design/icons-vue'
import { getLogs } from '@/api/admin'

const { t } = useI18n()
const router = useRouter()

const loading = ref(false)
const totalVisits = ref(0)
const todayVisits = ref(0)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getLogs(1, 1000)
    totalVisits.value = res.pagination.total
    
    // 计算今日访问量
    const today = new Date().toDateString()
    todayVisits.value = res.data.filter(log => {
      const logDate = new Date(log.access_time).toDateString()
      return logDate === today
    }).length
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.dashboard {
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    margin-top: 24px;
  }
  
  .quick-actions {
    margin-top: 24px;
  }
}
</style>
