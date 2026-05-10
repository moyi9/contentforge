import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectApi, type Project } from '../services/api'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)

  async function fetchProjects() {
    loading.value = true
    try {
      projects.value = await projectApi.list()
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: string) {
    loading.value = true
    try {
      currentProject.value = await projectApi.get(id)
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: Partial<Project>) {
    const project = await projectApi.create(data)
    projects.value.push(project)
    return project
  }

  async function deleteProject(id: string) {
    await projectApi.delete(id)
    projects.value = projects.value.filter(p => p.id !== id)
  }

  return {
    projects,
    currentProject,
    loading,
    fetchProjects,
    fetchProject,
    createProject,
    deleteProject,
  }
})
