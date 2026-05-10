import { defineStore } from 'pinia'
import { ref } from 'vue'
import { taskApi, type TaskRequest } from '../services/api'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<any[]>([])
  const currentTask = ref<any>(null)
  const loading = ref(false)

  async function fetchTasks() {
    loading.value = true
    try {
      tasks.value = await taskApi.list()
    } finally {
      loading.value = false
    }
  }

  async function fetchTask(id: string) {
    loading.value = true
    try {
      currentTask.value = await taskApi.get(id)
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: TaskRequest) {
    const task = await taskApi.create(data)
    tasks.value.unshift(task)
    return task
  }

  async function pollTaskStatus(id: string) {
    const task = await taskApi.get(id)
    if (currentTask.value?.id === id) {
      currentTask.value = task
    }
    return task
  }

  return {
    tasks,
    currentTask,
    loading,
    fetchTasks,
    fetchTask,
    createTask,
    pollTaskStatus,
  }
})
