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

export interface Task {
  id: string
  project_id: string
  topic: string
  platforms: string
  content_type: string
  target_audience: string
  word_count: number
  state: string
  current_agent: string
  progress: number
  created_at: string
}

export interface Section {
  heading: string
  content: string
  rag_ref: string | null
}

export interface Article {
  id: string
  task_id: string
  platform: string
  title: string
  sections: Section[]
  created_at: string
}

export interface ReviewIssue {
  section_index: number
  text: string
  severity: string
  dimension: string
  suggestion: string
}

export interface ReviewResult {
  article_id: string
  overall_score: number
  dimensions: Record<string, number>
  issues: ReviewIssue[]
  passed: boolean
}
