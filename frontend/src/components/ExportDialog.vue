<template>
  <el-dialog v-model="visible" title="Export Article" width="400px">
    <el-form>
      <el-form-item label="Format">
        <el-radio-group v-model="format">
          <el-radio value="markdown">Markdown</el-radio>
          <el-radio value="plain_text">Plain Text</el-radio>
          <el-radio value="rich_text">Rich Text (HTML)</el-radio>
          <el-radio value="pdf">PDF</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="Include Review Notes">
        <el-switch v-model="includeReview" />
      </el-form-item>
      <el-form-item label="Include Images">
        <el-switch v-model="includeImages" />
      </el-form-item>
    </el-form>
    <div v-if="preview" class="preview">
      <h4>Preview</h4>
      <pre>{{ previewContent }}</pre>
    </div>
    <template #footer>
      <el-button @click="visible = false">Cancel</el-button>
      <el-button type="primary" @click="doExport" :loading="loading">
        <el-icon><Download /></el-icon> Download
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const props = defineProps<{ articleId: string }>()
const emit = defineEmits<{ done: [result: any] }>()

const visible = defineModel<boolean>('modelValue')
const format = ref('markdown')
const includeReview = ref(false)
const includeImages = ref(true)
const loading = ref(false)
const preview = ref(false)

const previewContent = computed(() => {
  return `Exporting as ${format.value}...`
})

async function doExport() {
  loading.value = true
  try {
    const res = await api.post(`/articles/${props.articleId}/export`, {
      format: format.value,
      include_review_notes: includeReview.value,
      include_image_suggestions: includeImages.value
    })
    ElMessage.success(`Exported as ${format.value}`)
    emit('done', res.data)
    visible.value = false
  } catch (e: any) {
    ElMessage.error(e?.message || 'Export failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.preview {
  margin-top: 12px;
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
}
.preview pre {
  white-space: pre-wrap;
  font-size: 12px;
  color: #666;
}
</style>
