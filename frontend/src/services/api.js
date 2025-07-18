/**
 * API Service Layer
 * 
 * Centralized API communication for the scholarship hunter frontend
 * Handles all HTTP requests to the Django backend
 */

import axios from 'axios'
import toast from 'react-hot-toast'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
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
    if (error.response?.status === 500) {
      toast.error('Server error occurred. Please try again.')
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.')
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please check your connection.')
    } else if (!error.response) {
      toast.error('Network error. Please check your connection.')
    }
    
    return Promise.reject(error)
  }
)

// Scholarship API endpoints
export const scholarshipAPI = {
  // Get all scholarships with filtering and pagination
  getScholarships: (params = {}) => {
    return api.get('/scholarships/', { params })
  },
  
  // Get scholarship by ID
  getScholarship: (id) => {
    return api.get(`/scholarships/${id}/`)
  },
  
  // Get scholarship statistics
  getStatistics: () => {
    return api.get('/scholarships/statistics/')
  },
  
  // Get Tunisia-specific scholarships
  getTunisiaScholarships: (params = {}) => {
    return api.get('/scholarships/tunisia_scholarships/', { params })
  },
}

// Search Session API endpoints
export const searchSessionAPI = {
  // Get all search sessions
  getSessions: (params = {}) => {
    return api.get('/search-sessions/', { params })
  },
  
  // Get session by ID
  getSession: (id) => {
    return api.get(`/search-sessions/${id}/`)
  },
  
  // Start new search session
  startSearch: (data) => {
    return api.post('/search-sessions/start_search/', data)
  },
  
  // Stop search session
  stopSearch: (id) => {
    return api.post(`/search-sessions/${id}/stop_search/`)
  },
  
  // Get session progress
  getProgress: (id) => {
    return api.get(`/search-sessions/${id}/progress/`)
  },
}

// Website Target API endpoints
export const websiteAPI = {
  // Get all website targets
  getWebsites: (params = {}) => {
    return api.get('/website-targets/', { params })
  },
  
  // Get website performance stats
  getPerformanceStats: () => {
    return api.get('/website-targets/performance_stats/')
  },
}

// System API endpoints
export const systemAPI = {
  // Health check
  getHealth: () => {
    return axios.get('/health/')
  },
  
  // API info
  getInfo: () => {
    return axios.get('/api/info/')
  },
}

// Utility functions
export const apiUtils = {
  // Build query string from params object
  buildQueryString: (params) => {
    const searchParams = new URLSearchParams()
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v))
        } else {
          searchParams.append(key, value)
        }
      }
    })
    
    return searchParams.toString()
  },
  
  // Handle API errors consistently
  handleError: (error, customMessage = null) => {
    console.error('API Error:', error)
    
    if (customMessage) {
      toast.error(customMessage)
      return
    }
    
    if (error.response?.data?.error) {
      toast.error(error.response.data.error)
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail)
    } else if (error.message) {
      toast.error(error.message)
    } else {
      toast.error('An unexpected error occurred')
    }
  },
  
  // Format API response data
  formatResponse: (response) => {
    return {
      data: response.data,
      status: response.status,
      headers: response.headers,
    }
  },
}

// Export default api instance
export default api
