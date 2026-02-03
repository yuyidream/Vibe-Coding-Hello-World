<template>
  <div class="content-management">
    <a-page-header :title="t('content.title')" />
    
    <a-card :loading="loading">
      <a-form
        :model="formState"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 14 }"
        @finish="handleSave"
      >
        <a-form-item :label="t('content.mainTitle')" name="main_title" :rules="[{ required: true, message: '请输入主标题' }]">
          <a-input
            v-model:value="formState.main_title"
            :placeholder="t('content.mainTitlePlaceholder')"
            size="large"
          />
        </a-form-item>
        
        <a-form-item :label="t('content.subTitle')" name="sub_title">
          <a-input
            v-model:value="formState.sub_title"
            :placeholder="t('content.subTitlePlaceholder')"
            size="large"
          />
        </a-form-item>
        
        <a-form-item :wrapper-col="{ span: 14, offset: 4 }">
          <a-space>
            <a-button type="primary" html-type="submit" :loading="saving" size="large">
              {{ t('common.save') }}
            </a-button>
            
            <a-button @click="loadData" size="large">
              {{ t('common.reset') }}
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { getConfig, updateConfig } from '@/api/admin'

const { t } = useI18n()

const loading = ref(false)
const saving = ref(false)

const formState = reactive({
  main_title: '',
  sub_title: '',
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await getConfig()
    formState.main_title = res.data.main_title
    formState.sub_title = res.data.sub_title
  } catch (error) {
    console.error('加载配置失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    await updateConfig({
      main_title: formState.main_title,
      sub_title: formState.sub_title,
    })
    message.success(t('content.saveSuccess'))
  } catch (error) {
    console.error('保存失败:', error)
    message.error(t('content.saveFailed'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.content-management {
  :deep(.ant-card) {
    margin-top: 24px;
  }
}
</style>
