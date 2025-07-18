/**
 * Scholarships Hook
 * 
 * React hook for managing scholarship data
 * Provides data fetching, filtering, and real-time updates
 */

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from 'react-query'
import { scholarshipAPI, apiUtils } from '../services/api'
import { useDashboardWebSocket } from './useWebSocket'
import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'

// Query keys
const QUERY_KEYS = {
  scholarships: 'scholarships',
  scholarship: 'scholarship',
  statistics: 'scholarship-statistics',
  tunisiaScholarships: 'tunisia-scholarships',
}

// Get scholarships with filtering and pagination
export const useScholarships = (filters = {}, options = {}) => {
  return useQuery(
    [QUERY_KEYS.scholarships, filters],
    () => scholarshipAPI.getScholarships(filters),
    {
      select: (response) => response.data,
      staleTime: 2 * 60 * 1000, // 2 minutes
      cacheTime: 5 * 60 * 1000, // 5 minutes
      onError: (error) => {
        apiUtils.handleError(error, 'Failed to load scholarships')
      },
      ...options,
    }
  )
}

// Get infinite scholarships for pagination
export const useInfiniteScholarships = (filters = {}, options = {}) => {
  return useInfiniteQuery(
    [QUERY_KEYS.scholarships, 'infinite', filters],
    ({ pageParam = 1 }) => {
      const params = { ...filters, page: pageParam }
      return scholarshipAPI.getScholarships(params)
    },
    {
      select: (data) => ({
        pages: data.pages.map(page => page.data),
        pageParams: data.pageParams,
      }),
      getNextPageParam: (lastPage) => {
        if (lastPage.data.next) {
          const url = new URL(lastPage.data.next)
          return url.searchParams.get('page')
        }
        return undefined
      },
      staleTime: 2 * 60 * 1000,
      cacheTime: 5 * 60 * 1000,
      onError: (error) => {
        apiUtils.handleError(error, 'Failed to load scholarships')
      },
      ...options,
    }
  )
}

// Get single scholarship
export const useScholarship = (id, options = {}) => {
  return useQuery(
    [QUERY_KEYS.scholarship, id],
    () => scholarshipAPI.getScholarship(id),
    {
      select: (response) => response.data,
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      onError: (error) => {
        apiUtils.handleError(error, 'Failed to load scholarship details')
      },
      ...options,
    }
  )
}

// Get scholarship statistics
export const useScholarshipStatistics = (options = {}) => {
  return useQuery(
    [QUERY_KEYS.statistics],
    () => scholarshipAPI.getStatistics(),
    {
      select: (response) => response.data,
      staleTime: 1 * 60 * 1000, // 1 minute
      cacheTime: 5 * 60 * 1000,
      refetchInterval: 30 * 1000, // Refetch every 30 seconds
      onError: (error) => {
        apiUtils.handleError(error, 'Failed to load statistics')
      },
      ...options,
    }
  )
}

// Get Tunisia-specific scholarships
export const useTunisiaScholarships = (filters = {}, options = {}) => {
  return useQuery(
    [QUERY_KEYS.tunisiaScholarships, filters],
    () => scholarshipAPI.getTunisiaScholarships(filters),
    {
      select: (response) => response.data,
      staleTime: 2 * 60 * 1000,
      cacheTime: 5 * 60 * 1000,
      onError: (error) => {
        apiUtils.handleError(error, 'Failed to load Tunisia scholarships')
      },
      ...options,
    }
  )
}

// Real-time scholarship updates hook
export const useRealtimeScholarships = () => {
  const queryClient = useQueryClient()
  const [realtimeStats, setRealtimeStats] = useState(null)
  const [recentScholarships, setRecentScholarships] = useState([])

  const { addEventListener, isConnected } = useDashboardWebSocket({
    onMessage: (data) => {
      // Handle different types of real-time updates
      switch (data.type) {
        case 'scholarship_found':
          handleScholarshipFound(data.data)
          break
        case 'search_progress':
          handleSearchProgress(data.progress)
          break
        case 'status_update':
          handleStatusUpdate(data.status)
          break
        default:
          break
      }
    }
  })

  const handleScholarshipFound = (scholarshipData) => {
    // Add to recent scholarships
    setRecentScholarships(prev => [
      scholarshipData.scholarship,
      ...prev.slice(0, 9) // Keep only last 10
    ])

    // Invalidate scholarship queries to refetch data
    queryClient.invalidateQueries([QUERY_KEYS.scholarships])
    queryClient.invalidateQueries([QUERY_KEYS.statistics])
    queryClient.invalidateQueries([QUERY_KEYS.tunisiaScholarships])
  }

  const handleSearchProgress = (progressData) => {
    setRealtimeStats(prev => ({
      ...prev,
      ...progressData
    }))
  }

  const handleStatusUpdate = (statusData) => {
    setRealtimeStats(prev => ({
      ...prev,
      ...statusData
    }))
  }

  return {
    realtimeStats,
    recentScholarships,
    isConnected,
  }
}

// Scholarship filtering hook
export const useScholarshipFilters = (initialFilters = {}) => {
  const [filters, setFilters] = useState(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState(initialFilters)

  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const applyFilters = () => {
    setAppliedFilters(filters)
  }

  const resetFilters = () => {
    setFilters(initialFilters)
    setAppliedFilters(initialFilters)
  }

  const clearFilter = (key) => {
    const newFilters = { ...filters }
    delete newFilters[key]
    setFilters(newFilters)
  }

  const hasActiveFilters = Object.keys(appliedFilters).some(
    key => appliedFilters[key] !== undefined && appliedFilters[key] !== ''
  )

  return {
    filters,
    appliedFilters,
    updateFilter,
    applyFilters,
    resetFilters,
    clearFilter,
    hasActiveFilters,
  }
}

// Scholarship search hook
export const useScholarshipSearch = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)

  const searchScholarships = async (term, filters = {}) => {
    if (!term.trim()) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    try {
      const params = {
        search: term,
        ...filters
      }
      
      const response = await scholarshipAPI.getScholarships(params)
      setSearchResults(response.data.results || [])
    } catch (error) {
      apiUtils.handleError(error, 'Search failed')
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const clearSearch = () => {
    setSearchTerm('')
    setSearchResults([])
  }

  return {
    searchTerm,
    setSearchTerm,
    searchResults,
    isSearching,
    searchScholarships,
    clearSearch,
  }
}
