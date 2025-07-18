/**
 * Scholarship List Page
 * 
 * Browse and filter all available scholarships
 * Real-time updates and advanced filtering
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Search,
  Filter,
  MapPin,
  Calendar,
  DollarSign,
  ExternalLink,
  Star,
  Clock,
  CheckCircle
} from 'lucide-react'
import { useScholarships, useScholarshipFilters } from '../hooks/useScholarships'

const ScholarshipList = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  
  const {
    filters,
    appliedFilters,
    updateFilter,
    applyFilters,
    resetFilters,
    hasActiveFilters
  } = useScholarshipFilters({
    tunisia_eligible: true, // Default to Tunisia eligible
    funding_type: 'full'    // Default to fully funded
  })

  const { data: scholarships, isLoading, error } = useScholarships({
    ...appliedFilters,
    search: searchTerm,
    page_size: 20
  })

  const handleSearch = (e) => {
    e.preventDefault()
    // Search is handled automatically by the query
  }

  const ScholarshipCard = ({ scholarship }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card hover:shadow-medium transition-shadow duration-200"
    >
      <div className="card-body">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {scholarship.name}
            </h3>
            <p className="text-gray-600 mb-2">{scholarship.provider}</p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-1" />
                {scholarship.country}
              </div>
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {scholarship.days_until_deadline ? 
                  `${scholarship.days_until_deadline} days left` : 
                  'No deadline'
                }
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <span className={`badge ${
              scholarship.tunisia_eligible ? 'badge-success' : 'badge-gray'
            }`}>
              {scholarship.tunisia_eligible ? 'Tunisia Eligible' : 'Not Eligible'}
            </span>
            <div className="flex items-center">
              <Star className="w-4 h-4 text-warning-500 mr-1" />
              <span className="text-sm font-medium">
                {scholarship.overall_relevance_percentage}% match
              </span>
            </div>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            <strong>Field:</strong> {scholarship.field_of_study}
          </p>
          <p className="text-sm text-gray-600 mb-2">
            <strong>Level:</strong> {scholarship.academic_level}
          </p>
          <p className="text-sm text-gray-600">
            <strong>Funding:</strong> {scholarship.funding_coverage || 'Full funding'}
          </p>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <span className="badge badge-primary">
              AI: {scholarship.ai_relevance_percentage}%
            </span>
            <span className="badge badge-success">
              Web: {scholarship.web_dev_relevance_percentage}%
            </span>
            <span className="badge badge-warning">
              IT: {scholarship.it_relevance_percentage}%
            </span>
          </div>
          <a
            href={scholarship.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary btn-sm"
          >
            <ExternalLink className="w-4 h-4 mr-1" />
            Apply Now
          </a>
        </div>
      </div>
    </motion.div>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-danger-600">Failed to load scholarships</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Scholarships</h1>
          <p className="text-gray-600 mt-1">
            {scholarships?.count || 0} scholarships found
          </p>
        </div>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="btn-outline"
        >
          <Filter className="w-4 h-4 mr-2" />
          Filters
          {hasActiveFilters && (
            <span className="ml-2 w-2 h-2 bg-primary-500 rounded-full"></span>
          )}
        </button>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search scholarships..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="form-input pl-10 w-full"
        />
      </form>

      {/* Filters Panel */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="card"
        >
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="form-label">Country</label>
                <select
                  value={filters.country || ''}
                  onChange={(e) => updateFilter('country', e.target.value)}
                  className="form-input"
                >
                  <option value="">All Countries</option>
                  <option value="United Kingdom">United Kingdom</option>
                  <option value="United States">United States</option>
                  <option value="Germany">Germany</option>
                  <option value="France">France</option>
                  <option value="Canada">Canada</option>
                  <option value="Australia">Australia</option>
                </select>
              </div>
              
              <div>
                <label className="form-label">Academic Level</label>
                <select
                  value={filters.academic_level || ''}
                  onChange={(e) => updateFilter('academic_level', e.target.value)}
                  className="form-input"
                >
                  <option value="">All Levels</option>
                  <option value="bachelor">Bachelor's</option>
                  <option value="master">Master's</option>
                  <option value="phd">PhD</option>
                  <option value="any">Any Level</option>
                </select>
              </div>
              
              <div>
                <label className="form-label">Field of Study</label>
                <select
                  value={filters.field_of_study__icontains || ''}
                  onChange={(e) => updateFilter('field_of_study__icontains', e.target.value)}
                  className="form-input"
                >
                  <option value="">All Fields</option>
                  <option value="Computer Science">Computer Science</option>
                  <option value="Artificial Intelligence">AI</option>
                  <option value="Web Development">Web Development</option>
                  <option value="Information Technology">IT</option>
                  <option value="Cybersecurity">Cybersecurity</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.tunisia_eligible || false}
                    onChange={(e) => updateFilter('tunisia_eligible', e.target.checked)}
                    className="mr-2"
                  />
                  Tunisia Eligible Only
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.funding_type === 'full'}
                    onChange={(e) => updateFilter('funding_type', e.target.checked ? 'full' : '')}
                    className="mr-2"
                  />
                  Fully Funded Only
                </label>
              </div>
              
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={resetFilters}
                  className="btn-secondary btn-sm"
                >
                  Reset
                </button>
                <button
                  type="button"
                  onClick={applyFilters}
                  className="btn-primary btn-sm"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {scholarships?.results?.map((scholarship) => (
          <ScholarshipCard key={scholarship.id} scholarship={scholarship} />
        ))}
      </div>

      {/* Empty State */}
      {scholarships?.results?.length === 0 && (
        <div className="text-center py-12">
          <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No scholarships found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}

      {/* Pagination */}
      {scholarships?.next && (
        <div className="text-center">
          <button className="btn-outline">
            Load More Scholarships
          </button>
        </div>
      )}
    </div>
  )
}

export default ScholarshipList
