<template>
  <div class="knowledge-page">
    <div class="page-header">
      <h2>Knowledge Base</h2>
      <div>
        <el-button @click="showUploadDialog = true" type="primary">
          <el-icon><Upload /></el-icon> Upload Document
        </el-button>
        <el-button @click="configGitSync">
          <el-icon><Connection /></el-icon> Git Sync
        </el-button>
      </div>
    </div>

    <el-alert
      title="Upload .md or .txt files to build your project's knowledge base. Agent will use these for style reference and content generation."
      type="info" show-icon :closable="false" style="margin-bottom: 16px" />

    <div v-if="docs.length === 0" style="text-align: center; padding: 60px; color: #999;">
      <el-icon :size="48"><Document /></el-icon>
      <p>No documents yet. Upload your first document to get started.</p>
    </div>

    <el-table :data="docs" v-else style="width: 100%">
      <el-table-column prop="title" label="Title" />
      <el-table-column prop="doc_type" label="Type" width="140">
        <template #default="{ row }">
          <el-tag :type="docTypeTag(row.doc_type)" size="small">{{ row.doc_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="source_path" label="Source" />
      <el-table-column prop="indexed_at" label="Indexed At" width="180">
        <template #default="{ row }">{{ formatDate(row.indexed_at) }}</template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showUploadDialog" title="Upload Document" width="500px">
      <el-form :model="newDoc" label-width="100px">
        <el-form-item label="Title" required>
          <el-input v-model="newDoc.title" />
        </el-form-item>
        <el-form-item label="Type" required>
          <el-select v-model="newDoc.doc_type">
            <el-option label="Style Guide" value="style_guide" />
            <el-option label="Reference" value="reference" />
            <el-option label="Rule" value="rule" />
            <el-option label="Template" value="template" />
            <el-option label="Past Work" value="past_work" />
          </el-select>
        </el-form-item>
        <el-form-item label="Content" required>
          <el-input v-model="newDoc.content" type="textarea" :rows="8" placeholder="Paste or type markdown content..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">Cancel</el-button>
        <el-button type="primary" @click="uploadDoc">Upload</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Upload, Connection, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const route = useRoute()
const projectId = route.params.id as string
const docs = ref<any[]>([])
const showUploadDialog = ref(false)
const newDoc = ref({ title: '', doc_type: 'reference', content: '' })

onMounted(async () => {
  try {
    const res = await api.get(`/knowledge/${projectId}`)
    docs.value = res.data || []
  } catch { /* empty */ }
})

async function uploadDoc() {
  if (!newDoc.value.title || !newDoc.value.content) {
    ElMessage.warning('Title and content are required')
    return
  }
  try {
    await api.post('/knowledge/upload', {
      project_id: projectId,
      title: newDoc.value.title,
      content: newDoc.value.content,
      doc_type: newDoc.value.doc_type,
      source_path: 'manual_upload'
    })
    ElMessage.success('Document uploaded and indexed')
    showUploadDialog.value = false
    newDoc.value = { title: '', doc_type: 'reference', content: '' }
    // Refresh
    const res = await api.get(`/knowledge/${projectId}`)
    docs.value = res.data || []
  } catch (e: any) {
    ElMessage.error(e?.message || 'Upload failed')
  }
}

function configGitSync() {
  ElMessage.info('Git sync configuration coming soon')
}

function docTypeTag(type: string) {
  const tags: Record<string, string> = {
    style_guide: 'warning', reference: 'primary',
    rule: 'danger', template: 'success', past_work: 'info'
  }
  return tags[type] || 'info'
}

function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN')
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
