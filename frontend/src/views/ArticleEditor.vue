<template>
  <div class="editor-page">
    <div class="editor-layout">
      <!-- Left: Article Editor -->
      <div class="editor-panel">
        <div class="editor-header">
          <h2>{{ article.title || 'Loading...' }}</h2>
          <div class="editor-actions">
            <el-button @click="showExportDialog = true" type="primary">
              <el-icon><Download /></el-icon> Export
            </el-button>
          </div>
        </div>

        <div v-if="loading" style="text-align: center; padding: 60px">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p>Loading article...</p>
        </div>

        <div v-else class="sections">
          <div v-for="(section, idx) in article.sections" :key="idx" class="section-block"
               :class="{ 'has-issues': getIssuesForSection(idx).length > 0 }">
            <div class="section-header">
              <h3>{{ section.heading }}</h3>
              <el-tag v-if="section.rag_ref" type="info" size="small">RAG</el-tag>
            </div>
            <div class="section-content">
              <p>{{ section.content }}</p>
            </div>
            <!-- Chat revision -->
            <div class="section-chat">
              <el-input v-model="chatInputs[idx]" placeholder="Ask Agent to revise this section..." size="small">
                <template #append>
                  <el-button @click="reviseSection(idx)" :icon="Promotion" />
                </template>
              </el-input>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Review Panel -->
      <div class="review-panel" v-if="review">
        <h3>Review Results</h3>
        <div class="score-display">
          <div class="overall-score">
            <span class="score-value" :class="scoreClass(review.overall_score)">{{ review.overall_score }}</span>
            <span class="score-label">Overall</span>
          </div>
          <div class="dimension-scores">
            <div v-for="(val, key) in review.dimensions" :key="key" class="dimension">
              <span class="dim-name">{{ key }}</span>
              <el-progress :percentage="val" :stroke-width="8" :status="val >= 80 ? 'success' : val >= 60 ? '' : 'exception'" />
            </div>
          </div>
        </div>

        <div v-if="review.issues.length > 0" class="issues">
          <h4>Issues ({{ review.issues.length }})</h4>
          <div v-for="(issue, i) in review.issues" :key="i" class="issue-item"
               :class="'severity-' + issue.severity">
            <el-tag :type="issue.severity === 'error' ? 'danger' : issue.severity === 'warning' ? 'warning' : 'info'" size="small">
              {{ issue.dimension }}
            </el-tag>
            <p>{{ issue.suggestion }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Dialog -->
    <el-dialog v-model="showExportDialog" title="Export Article" width="400px">
      <el-form>
        <el-form-item label="Format">
          <el-radio-group v-model="exportFormat">
            <el-radio value="markdown">Markdown</el-radio>
            <el-radio value="plain_text">Plain Text</el-radio>
            <el-radio value="rich_text">Rich Text (HTML)</el-radio>
            <el-radio value="pdf">PDF</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">Cancel</el-button>
        <el-button type="primary" @click="doExport" :loading="exporting">
          <el-icon><Download /></el-icon> Download
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Download, Loading, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const route = useRoute()
const articleId = route.params.id as string

const article = ref<any>({ sections: [] })
const review = ref<any>(null)
const loading = ref(true)
const showExportDialog = ref(false)
const exportFormat = ref('markdown')
const exporting = ref(false)
const chatInputs = ref<Record<number, string>>({})

onMounted(async () => {
  try {
    const res = await api.get(`/articles/${articleId}`)
    article.value = res.data
    loading.value = false
  } catch (e: any) {
    ElMessage.error('Failed to load article')
    loading.value = false
  }
  // Stub review data for display
  review.value = {
    overall_score: 85,
    dimensions: { '合规性': 95, '原创度': 78, '可读性': 88, '风格一致性': 82, '平台适配性': 80 },
    issues: [
      { section_index: 0, text: 'could be more concise', severity: 'warning', dimension: '可读性', suggestion: 'Consider shortening the introduction.' },
      { section_index: 1, text: 'missing examples', severity: 'info', dimension: '原创度', suggestion: 'Add concrete examples to increase originality.' }
    ]
  }
})

function getIssuesForSection(idx: number) {
  return review.value?.issues?.filter((i: any) => i.section_index === idx) || []
}

async function reviseSection(idx: number) {
  const msg = chatInputs.value[idx]
  if (!msg) return
  ElMessage.success(`Revision requested: "${msg}"`)
  chatInputs.value[idx] = ''
}

function doExport() {
  exporting.value = true
  api.post(`/articles/${articleId}/export`, { format: exportFormat.value })
    .then(res => {
      ElMessage.success('Article exported!')
      showExportDialog.value = false
    })
    .catch(() => ElMessage.error('Export failed'))
    .finally(() => { exporting.value = false })
}

function scoreClass(score: number) {
  return score >= 80 ? 'score-good' : score >= 60 ? 'score-ok' : 'score-bad'
}
</script>

<style scoped>
.editor-layout {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}
.editor-panel {
  flex: 1;
  min-width: 0;
}
.review-panel {
  width: 350px;
  flex-shrink: 0;
}
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.editor-actions {
  display: flex;
  gap: 8px;
}
.section-block {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  position: relative;
}
.section-block.has-issues {
  border-left: 3px solid #e6a23c;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.section-content p {
  line-height: 1.8;
  color: #333;
}
.section-chat {
  margin-top: 12px;
}
.score-display {
  text-align: center;
  margin-bottom: 20px;
}
.overall-score {
  margin-bottom: 16px;
}
.score-value {
  font-size: 48px;
  font-weight: bold;
  display: block;
}
.score-good { color: #67c23a; }
.score-ok { color: #e6a23c; }
.score-bad { color: #f56c6c; }
.score-label {
  font-size: 14px;
  color: #999;
}
.dimension-scores {
  text-align: left;
}
.dimension {
  margin-bottom: 12px;
}
.dim-name {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  display: block;
}
.issues {
  border-top: 1px solid #eee;
  padding-top: 16px;
}
.issue-item {
  padding: 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  background: #fafafa;
}
.issue-item p {
  font-size: 13px;
  margin-top: 4px;
  color: #666;
}
</style>
