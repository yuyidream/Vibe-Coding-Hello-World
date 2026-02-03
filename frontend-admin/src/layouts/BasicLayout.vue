<template>
  <a-layout class="layout-container">
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      theme="dark"
    >
      <div class="logo">
        <h2 v-if="!collapsed">Hello World</h2>
        <h2 v-else>HW</h2>
      </div>
      
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="/dashboard">
          <DashboardOutlined />
          <span>{{ t('menu.dashboard') }}</span>
        </a-menu-item>
        
        <a-menu-item key="/content">
          <EditOutlined />
          <span>{{ t('menu.content') }}</span>
        </a-menu-item>
        
        <a-menu-item key="/logs">
          <FileTextOutlined />
          <span>{{ t('menu.logs') }}</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    
    <a-layout>
      <a-layout-header class="header">
        <div class="header-left">
          <MenuUnfoldOutlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <MenuFoldOutlined
            v-else
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
        </div>
        
        <div class="header-right">
          <a-dropdown>
            <span class="user-info">
              <UserOutlined />
              {{ userStore.username }}
            </span>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="handleLogout">
                  <LogoutOutlined />
                  {{ t('common.logout') }}
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      
      <a-layout-content class="content">
        <RouterView />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  EditOutlined,
  FileTextOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)
const selectedKeys = ref<string[]>([route.path])

watch(
  () => route.path,
  (newPath) => {
    selectedKeys.value = [newPath]
  }
)

const handleMenuClick = ({ key }: { key: string }) => {
  router.push(key)
}

const handleLogout = () => {
  userStore.logout()
}
</script>

<style scoped lang="scss">
.layout-container {
  min-height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  
  h2 {
    margin: 0;
    color: white;
  }
}

.header {
  background: white;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  .trigger {
    font-size: 18px;
    cursor: pointer;
    transition: color 0.3s;
    
    &:hover {
      color: #1890ff;
    }
  }
}

.header-right {
  .user-info {
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 4px;
    transition: background-color 0.3s;
    
    &:hover {
      background-color: #f0f0f0;
    }
  }
}

.content {
  margin: 24px;
  padding: 24px;
  background: white;
  border-radius: 8px;
  min-height: calc(100vh - 112px);
}
</style>
