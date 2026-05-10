<template>
  <div class="task-create-page">
    <h2>New Content Task</h2>
    <el-card style="max-width: 700px; margin-top: 20px;">
      <el-form :model="form" label-width="140px">

        <el-form-item label="Project" required>
          <el-select v-model="form.project_id" placeholder="Select project" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="Topic" required>
          <el-input v-model="form.topic" placeholder="What do you want to write about?" />
        </el-form-item>

        <el-form-item label="Platforms" required>
          <el-checkbox-group v-model="form.platforms">
            <el-checkbox value="公众号" label="公众号" />
            <el-checkbox value="小红书" label="小红书" />
            <el-checkbox value="知乎" label="知乎" />
            <el-checkbox value="技术博客" label="技术博客" />
            <el-checkbox value="Twitter" label="Twitter" />
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="Content Type" required>
          <el-select v-model="form.content_type" style="width: 100%">
            <el-option label="Technical Article" value="technical" />
            <el-option label="Marketing Copy" value="marketing" />
            <el-option label="Industry Analysis" value="analysis" />
            <el-option label="Social Media Post" value="social" />
            <el-option label="Tutorial/Guide" value="tutorial" />
          </el-select>
        </el-form-item>

        <el-form-item label="Target Audience">
          <el-input v-model="form.target_audience" placeholder="e.g., developers, women aged 25-35" />
        </el-form-item>

        <el-form-item label="Word Count">
          <el-input-number v-model="form.word_count" :min="100" :max="5000" :step="100" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" @click="createTask" :loading="loading">
            <el-icon><MagicStick /></el-icon> Start Creating
          </el-button>
        </el-form-item>

      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '../stores/project'
import { taskApi } from '../services/api'

const router = useRouter()
const projectStore = useProjectStore()
const projects = ref<any[]>([])
const loading = ref(false)

const form = ref({
  project_id: '',
  topic: '',
  platforms: [] as string[],
  content_type: 'technical',
  target_audience: '',
  word_count: 1000,
})

onMounted(async () => {
  await projectStore.fetchProjects()
  projects.value = projectStore.projects
})

async function createTask() {
  if (!form.value.project_id || !form.value.topic || form.value.platforms.length === 0) {
    ElMessage.warning('Please fill in project, topic, and at least one platform')
    return
  }
  loading.value = true
  try {
    const task = await taskApi.create({ ...form.value })
    ElMessage.success('Task created!')
    router.push(`/tasks/${task.task_id || task.id}`)
  } catch (e: any) {
    ElMessage.error(e?.message || 'Failed to create task')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.task-create-page {
  max-width: 700px;
}
</style>
