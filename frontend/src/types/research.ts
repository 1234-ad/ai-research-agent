export interface ResearchRequest {
  id: number
  topic: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  task_id?: string
  created_at: string
  updated_at?: string
  completed_at?: string
  results?: ResearchResults
  error_message?: string
}

export interface ResearchRequestDetail extends ResearchRequest {
  logs: WorkflowLog[]
  articles: Article[]
}

export interface ResearchRequestList {
  items: ResearchRequest[]
  total: number
  page: number
  size: number
  pages: number
}

export interface WorkflowLog {
  id: number
  step: 'input_parsing' | 'data_gathering' | 'processing' | 'result_persistence' | 'return_results'
  status: string
  message?: string
  details?: Record<string, any>
  started_at: string
  completed_at?: string
  duration_ms?: number
}

export interface Article {
  id: number
  title: string
  url?: string
  source: string
  content?: string
  summary?: string
  keywords?: string[]
  published_at?: string
  extracted_at: string
  relevance_score: number
}

export interface ResearchResults {
  topic: string
  summary: string
  top_articles: Article[]
  keywords: string[]
  sources: string[]
  total_articles_found: number
  processing_time_ms: number
  completed_at: string
}

export interface CreateResearchRequest {
  topic: string
}

export interface WebSocketMessage {
  type: string
  data: Record<string, any>
}

export interface ProgressUpdate {
  step: string
  status: string
  message: string
  progress: number
  details?: Record<string, any>
}