<template>
  <div class="projects-page">
    <div class="page-header">
      <h2>Projects</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon> New Project
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="project in projectStore.projects" :key="project.id">
        <el-card shadow="hover" class="project-card" @click="openProject(project.id)">
          <template #header>
            <div class="card-header">
              <span class="project-name">{{ project.name }}</span>
              <el-tag size="small" type="info">{{ project.writing_style || 'no style' }}</el-tag>
            </div>
          </template>
          <p class="project-desc">{{ project.description || 'No description' }}</p>
          <div class="project-meta">
            <small>Created: {{ formatDate(project.created_at) }}</small>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="New Project" width="500px">
      <el-form :model="newProject" label-width="120px">
        <el-form-item label="Name" required>
          <el-input v-model="newProject.name" placeholder="My Project" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newProject.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="Writing Style">
          <el-input v-model="newProject.writing_style" placeholder="technical, concise, etc." />
        </el-form-item>
        <el-form-item label="Knowledge Path">
          <el-input v-model="newProject.knowledge_base_path" placeholder="./vault/path" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="createProject">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/project'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const projectStore = useProjectStore()

const showCreateDialog = ref(false)
const newProject = ref({
  name: '',
  description: '',
  writing_style: '',
  knowledge_base_path: ''
})

onMounted(() => {
  projectStore.fetchProjects()
})

function openProject(id: string) {
  router.push(`/projects/${id}`)
}

async function createProject() {
  if (!newProject.value.name) {
    ElMessage.warning('Project name is required')
    return
  }
  try {
    await projectStore.createProject(newProject.value)
    showCreateDialog.value = false
    newProject.value = { name: '', description: '', writing_style: '', knowledge_base_path: '' }
    ElMessage.success('Project created')
  } catch (e: any) {
    ElMessage.error(e?.message || 'Failed to create project')
  }
}

function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.project-card {
  margin-bottom: 20px;
  cursor: pointer;
}
.project-card:hover {
  transform: translateY(-2px);
  transition: all 0.2s;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.project-name {
  font-weight: 600;
  font-size: 16px;
}
.project-desc {
  color: #666;
  font-size: 14px;
  margin: 8px 0;
}
.project-meta {
  color: #999;
}
</style>
