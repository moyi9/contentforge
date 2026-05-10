<template>
  <div class="trace-page">
    <h2>Agent Trace</h2>
    <el-card v-if="task" style="margin-top: 20px;">
      <div class="trace-header">
        <h3>{{ task.topic }}</h3>
        <el-tag :type="task.state === 'done' ? 'success' : 'warning'">{{ task.state }}</el-tag>
      </div>

      <h4 style="margin: 20px 0 12px">Agent Timeline</h4>
      <div class="trace-timeline">
        <div v-for="agent in agents" :key="agent.name" class="trace-item">
          <div class="trace-dot" :class="agent.color"></div>
          <div class="trace-content">
            <div class="trace-agent-name">{{ agent.name }}</div>
            <div class="trace-duration">{{ agent.duration }}</div>
            <div class="trace-status">{{ agent.status }}</div>
          </div>
        </div>
      </div>

      <div class="trace-summary">
        <h4>Summary</h4>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="Total Agents">{{ agents.length }}</el-descriptions-item>
          <el-descriptions-item label="Status">{{ task.state }}</el-descriptions-item>
          <el-descriptions-item label="Progress">{{ Math.round(task.progress || 0) }}%</el-descriptions-item>
          <el-descriptions-item label="Current Agent">{{ task.current_agent }}</el-descriptions-item>
          <el-descriptions-item label="Total Time">{{ totalDuration }}</el-descriptions-item>
          <el-descriptions-item label="Created">{{ formatDate(task.created_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <el-card v-else style="text-align: center; padding: 40px; margin-top: 20px;">
      <p>Loading trace data...</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const taskId = route.params.id as string
const task = ref<any>(null)

const agents = computed(() => [
  { name: 'Planner Agent', duration: '1.2s', status: 'Completed', color: 'blue' },
  { name: 'Writer Agent', duration: '3.5s', status: 'Completed', color: 'green' },
  { name: 'Reviewer Agent', duration: '2.1s', status: 'Completed', color: task.value?.state === 'done' ? 'green' : 'yellow' },
  { name: 'Exporter Agent', duration: '0.4s', status: task.value?.state === 'done' ? 'Completed' : 'Pending', color: task.value?.state === 'done' ? 'green' : 'gray' },
])

const totalDuration = computed(() => {
  const vals = agents.value.map(a => parseFloat(a.duration)).filter(Boolean)
  return `${vals.reduce((a, b) => a + b, 0).toFixed(1)}s`
})

onMounted(async () => {
  try {
    const res = await api.get(`/tasks/${taskId}`)
    task.value = res.data
  } catch {}
})

function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN')
}
</script>

<style scoped>
.trace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.trace-timeline {
  border-left: 2px solid #e0e0e0;
  padding-left: 20px;
  margin: 16px 0;
}
.trace-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  position: relative;
}
.trace-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-left: -26px;
  margin-top: 4px;
  flex-shrink: 0;
}
.trace-dot.blue { background: #409eff; }
.trace-dot.green { background: #67c23a; }
.trace-dot.yellow { background: #e6a23c; }
.trace-dot.gray { background: #c0c4cc; }
.trace-content {
  flex: 1;
}
.trace-agent-name {
  font-weight: 600;
  font-size: 14px;
}
.trace-duration {
  font-size: 12px;
  color: #999;
}
.trace-status {
  font-size: 12px;
  color: #67c23a;
}
.trace-summary {
  margin-top: 20px;
}
</style>
