import { createRouter, createWebHistory } from 'vue-router'
import ProjectsView from '../views/Projects.vue'
import KnowledgeBaseView from '../views/KnowledgeBase.vue'
import TaskCreateView from '../views/TaskCreate.vue'
import TaskProgressView from '../views/TaskProgress.vue'
import ArticleEditorView from '../views/ArticleEditor.vue'
import TaskTraceView from '../views/TaskTrace.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/projects' },
    { path: '/projects', name: 'projects', component: ProjectsView },
    { path: '/projects/:id', name: 'knowledge-base', component: KnowledgeBaseView },
    { path: '/tasks/new', name: 'task-create', component: TaskCreateView },
    { path: '/tasks/:id', name: 'task-progress', component: TaskProgressView },
    { path: '/articles/:id', name: 'article-editor', component: ArticleEditorView },
    { path: '/tasks/:id/trace', name: 'task-trace', component: TaskTraceView },
  ]
})

export default router
