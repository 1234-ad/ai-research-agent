import axios from 'axios'
import type { 
  ResearchRequest, 
  ResearchRequestDetail, 
  ResearchRequestList,
  CreateResearchRequest 
} from '@/types/research'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response.data)
    }
    return Promise.reject(error)
  }
)

export const researchApi = {
  // Create a new research request
  createResearch: async (data: CreateResearchRequest): Promise<ResearchRequest> => {
    const response = await api.post('/api/research', data)
    return response.data
  },

  // Get all research requests
  getResearchRequests: async (params?: {
    page?: number
    size?: number
    status?: string
  }): Promise<ResearchRequestList> => {
    const response = await api.get('/api/research', { params })
    return response.data
  },

  // Get a specific research request
  getResearchRequest: async (id: number): Promise<ResearchRequestDetail> => {
    const response = await api.get(`/api/research/${id}`)
    return response.data
  },

  // Get workflow logs for a research request
  getResearchLogs: async (id: number) => {
    const response = await api.get(`/api/research/${id}/logs`)
    return response.data
  },

  // Delete a research request
  deleteResearchRequest: async (id: number): Promise<void> => {
    await api.delete(`/api/research/${id}`)
  },
}

export const healthApi = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

export default api