import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export interface Project {
  id: string
  name: string
  description: string
  writing_style: string
  forbidden_words: string
  template_config: string
  knowledge_base_path: string
  created_at: string
}

export interface TaskRequest {
  project_id: string
  topic: string
  platforms: string[]
  content_type: string
  target_audience: string
  word_count: number
}

export interface TaskStatus {
  task_id: string
  state: string
  current_agent: string
  progress: number
}

export interface Article {
  id: string
  title: string
  sections: Section[]
  platform: string
}

export interface Section {
  heading: string
  content: string
  rag_ref?: string
}

export const projectApi = {
  list: () => api.get<Project[]>('/projects').then(r => r.data),
  get: (id: string) => api.get<Project>(`/projects/${id}`).then(r => r.data),
  create: (data: Partial<Project>) => api.post<Project>('/projects', data).then(r => r.data),
  delete: (id: string) => api.delete(`/projects/${id}`).then(r => r.data),
}

export const taskApi = {
  list: () => api.get<any[]>('/tasks').then(r => r.data),
  get: (id: string) => api.get<any>(`/tasks/${id}`).then(r => r.data),
  create: (data: TaskRequest) => api.post<any>('/tasks', data).then(r => r.data),
}

export const articleApi = {
  get: (id: string) => api.get<any>(`/articles/${id}`).then(r => r.data),
  create: (data: any) => api.post<any>('/articles', data).then(r => r.data),
  export: (id: string, format: string) =>
    api.post<any>(`/articles/${id}/export`, { format }).then(r => r.data),
}

export default api
