<template>
  <div class="progress-page">
    <h2>Task Progress</h2>

    <el-card v-if="task" style="margin-top: 20px;">
      <div class="task-header">
        <h3>{{ task.topic }}</h3>
        <el-tag :type="stateTag(task.state)" size="large">{{ task.state }}</el-tag>
      </div>

      <!-- Agent Pipeline -->
      <div class="pipeline">
        <div v-for="(step, i) in pipeline" :key="step.name" class="pipeline-step"
             :class="{ active: step.isActive, done: step.isDone, pending: step.isPending }">
          <div class="step-icon">{{ step.isDone ? '✓' : step.isActive ? '◉' : i + 1 }}</div>
          <div class="step-label">{{ step.name }}</div>
        </div>
      </div>

      <el-progress :percentage="Math.round(task.progress || 0)" :status="progressStatus" style="margin: 20px 0" />

      <p style="color: #666; text-align: center;">
        Current: <strong>{{ task.current_agent || 'starting...' }}</strong>
      </p>

      <div v-if="task.state === 'done'" style="text-align: center; margin-top: 20px">
        <el-button type="primary" @click="viewArticle" size="large">
          View Article
        </el-button>
        <el-button @click="viewTrace" size="large">
          View Trace
        </el-button>
      </div>
    </el-card>

    <el-card v-else-if="loading" style="text-align: center; padding: 40px">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <p>Loading task...</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id as string

const task = ref<any>(null)
const loading = ref(true)
let eventSource: EventSource | null = null

const pipeline = computed(() => {
  const states = ['pending', 'planning', 'writing', 'reviewing', 'exporting', 'done']
  const names = ['Planner', 'Writer', 'Reviewer', 'Exporter', 'Done']
  const currentIdx = states.indexOf(task.value?.state || 'pending')
  
  return names.map((name, i) => ({
    name,
    isActive: i === currentIdx,
    isDone: i < currentIdx,
    isPending: i > currentIdx
  }))
})

const progressStatus = computed(() => {
  if (!task.value) return ''
  const p = task.value.progress || 0
  return p >= 100 ? 'success' : p > 0 ? '' : ''
})

onMounted(async () => {
  // Initial fetch
  try {
    const res = await api.get(`/tasks/${taskId}`)
    task.value = res.data
    loading.value = false
  } catch {
    loading.value = false
    return
  }
  
  // SSE stream for real-time updates
  try {
    eventSource = new EventSource(`/api/tasks/${taskId}/stream`)
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        task.value = data
      } catch {}
    }
    eventSource.onerror = () => {
      // Fallback: poll every 3s
      if (eventSource) eventSource.close()
      pollInterval = window.setInterval(pollTask, 3000)
    }
  } catch {
    // SSE not supported, use polling
    pollInterval = window.setInterval(pollTask, 3000)
  }
})

let pollInterval: number | undefined

async function pollTask() {
  try {
    const res = await api.get(`/tasks/${taskId}`)
    task.value = res.data
    if (res.data.state === 'done' || res.data.state === 'failed') {
      clearInterval(pollInterval)
    }
  } catch {}
}

function viewArticle() {
  if (task.value?.result?.id) {
    router.push(`/articles/${task.value.result.id}`)
  } else {
    router.push(`/articles/${taskId}`)
  }
}

function viewTrace() {
  router.push(`/tasks/${taskId}/trace`)
}

onUnmounted(() => {
  if (eventSource) eventSource.close()
  if (pollInterval) clearInterval(pollInterval)
})

function stateTag(state: string) {
  const tags: Record<string, string> = {
    pending: 'info', planning: 'warning', writing: '',
    reviewing: '', exporting: 'success', done: 'success', failed: 'danger'
  }
  return tags[state] || 'info'
}
</script>

<style scoped>
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.pipeline {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 20px 0;
}
.pipeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 0.4;
  transition: all 0.3s;
}
.pipeline-step.active {
  opacity: 1;
  color: #409eff;
}
.pipeline-step.done {
  opacity: 0.8;
  color: #67c23a;
}
.step-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}
.pipeline-step.active .step-icon {
  background: #409eff;
  color: white;
  border-color: #409eff;
}
.pipeline-step.done .step-icon {
  background: #67c23a;
  color: white;
  border-color: #67c23a;
}
.step-label {
  font-size: 13px;
  font-weight: 500;
}
</style>
