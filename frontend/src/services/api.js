import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    
    // Handle common error cases
    if (error.response?.status === 413) {
      throw new Error('File too large. Please choose a smaller file.')
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Invalid request')
    } else if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.')
    } else if (!error.response) {
      throw new Error('Network error. Please check your connection.')
    }
    
    throw error
  }
)

export const apiService = {
  // Upload file and start transcription
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 1 minute for upload
    })
    
    return response.data
  },

  // Get transcription status
  async getTranscriptionStatus(jobId) {
    const response = await api.get(`/status/${jobId}`)
    return response.data
  },

  // Get transcription preview
  async getTranscriptionPreview(jobId, lines = 10) {
    const response = await api.get(`/preview/${jobId}`, {
      params: { lines }
    })
    return response.data
  },

  // Download transcription in specified format
  async downloadTranscription(jobId, format) {
    const response = await api.get(`/download/${jobId}/${format}`, {
      responseType: 'blob',
      timeout: 60000, // 1 minute for download
    })
    
    // Extract filename from Content-Disposition header
    const contentDisposition = response.headers['content-disposition']
    let filename = `transcription.${format}`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    return {
      blob: response.data,
      filename: filename,
      contentType: response.headers['content-type']
    }
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/')
    return response.data
  }
}

export default apiService
