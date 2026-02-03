<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>{{ t('login.title') }}</h1>
        <p>{{ t('login.subtitle') }}</p>
      </div>
      
      <a-form
        :model="formState"
        :rules="rules"
        @finish="handleLogin"
        class="login-form"
      >
        <a-form-item name="password">
          <a-input-password
            v-model:value="formState.password"
            size="large"
            :placeholder="t('login.passwordPlaceholder')"
            @pressEnter="handleLogin"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>
        
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            {{ t('common.login') }}
          </a-button>
        </a-form-item>
      </a-form>
      
      <div class="locale-switch">
        <a-select
          v-model:value="locale"
          size="small"
          style="width: 120px"
          @change="handleLocaleChange"
        >
          <a-select-option value="zh-CN">中文</a-select-option>
          <a-select-option value="en-US">English</a-select-option>
        </a-select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { LockOutlined } from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'

const { t, locale } = useI18n()
const userStore = useUserStore()

const formState = reactive({
  password: '',
})

const rules = {
  password: [
    { required: true, message: t('login.passwordRequired'), trigger: 'blur' },
  ],
}

const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await userStore.login({ password: formState.password })
  } finally {
    loading.value = false
  }
}

const handleLocaleChange = (value: string) => {
  localStorage.setItem('locale', value)
  location.reload()
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
  
  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 8px;
  }
  
  p {
    font-size: 14px;
    color: #6b7280;
  }
}

.login-form {
  margin-top: 24px;
}

.locale-switch {
  margin-top: 16px;
  text-align: center;
}
</style>
