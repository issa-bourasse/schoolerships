/**
 * Dashboard Page
 * 
 * Real-time overview of the AI scholarship hunting system
 * Shows live statistics, AI thinking, and recent discoveries
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Search,
  Target,
  Globe,
  Brain,
  Zap,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import { useScholarshipStatistics, useRealtimeScholarships } from '../hooks/useScholarships'
import { searchSessionAPI } from '../services/api'
import toast from 'react-hot-toast'

const Dashboard = () => {
  const [isSearching, setIsSearching] = useState(false)
  const [aiThoughts, setAiThoughts] = useState([])
  
  // Get statistics and real-time updates
  const { data: stats, isLoading: statsLoading } = useScholarshipStatistics()
  const { realtimeStats, recentScholarships, isConnected } = useRealtimeScholarships()

  // Combine static and real-time stats
  const currentStats = { ...stats, ...realtimeStats }

  // Handle AI thoughts from WebSocket
  useEffect(() => {
    // This would be connected to WebSocket AI thinking events
    // For now, we'll simulate some thoughts
    const simulateAiThoughts = () => {
      const thoughts = [
        { id: 1, type: 'planning', content: 'Analyzing university websites for new scholarship opportunities...', timestamp: new Date(), confidence: 0.85 },
        { id: 2, type: 'discovery', content: 'Found potential scholarship page at cambridge.ac.uk', timestamp: new Date(Date.now() - 30000), confidence: 0.92 },
        { id: 3, type: 'analysis', content: 'Verifying Tunisia eligibility for 3 new scholarships', timestamp: new Date(Date.now() - 60000), confidence: 0.78 },
      ]
      setAiThoughts(thoughts)
    }

    simulateAiThoughts()
  }, [])

  const handleStartSearch = async () => {
    try {
      setIsSearching(true)
      const response = await searchSessionAPI.startSearch({
        session_name: `Search Session ${new Date().toLocaleString()}`,
        target_scholarships: 10000
      })
      
      if (response.data.success) {
        toast.success('AI scholarship search started!')
      }
    } catch (error) {
      toast.error('Failed to start search')
    } finally {
      setIsSearching(false)
    }
  }

  const StatCard = ({ title, value, icon: Icon, color = 'primary', change, description }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600 mt-1`}>
            {typeof value === 'number' ? value.toLocaleString() : value || '0'}
          </p>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <div className={`p-3 bg-${color}-100 rounded-lg`}>
          <Icon className={`w-6 h-6 text-${color}-600`} />
        </div>
      </div>
      {change && (
        <div className="flex items-center mt-4">
          <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
          <span className="text-sm text-success-600 font-medium">+{change}</span>
          <span className="text-sm text-gray-500 ml-1">today</span>
        </div>
      )}
    </motion.div>
  )

  const AIThoughtCard = ({ thought }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg"
    >
      <div className={`p-2 rounded-lg ${
        thought.type === 'planning' ? 'bg-blue-100' :
        thought.type === 'discovery' ? 'bg-green-100' :
        'bg-purple-100'
      }`}>
        <Brain className={`w-4 h-4 ${
          thought.type === 'planning' ? 'text-blue-600' :
          thought.type === 'discovery' ? 'text-green-600' :
          'text-purple-600'
        }`} />
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-900">{thought.content}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-500">
            {new Date(thought.timestamp).toLocaleTimeString()}
          </span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-xs text-gray-500">
              {Math.round(thought.confidence * 100)}% confident
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  )

  const RecentScholarshipCard = ({ scholarship }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
    >
      <h4 className="font-medium text-gray-900 text-sm">{scholarship.name}</h4>
      <p className="text-xs text-gray-600 mt-1">{scholarship.provider}</p>
      <div className="flex items-center justify-between mt-2">
        <span className={`badge ${scholarship.tunisia_eligible ? 'badge-success' : 'badge-gray'}`}>
          {scholarship.tunisia_eligible ? 'Tunisia Eligible' : 'Not Eligible'}
        </span>
        <span className="text-xs text-gray-500">
          {Math.round(scholarship.relevance_score * 100)}% match
        </span>
      </div>
    </motion.div>
  )

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner w-8 h-8"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Scholarship Hunter</h1>
          <p className="text-gray-600 mt-1">
            Autonomous scholarship discovery for Tunisia students
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
            isConnected ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-success-500 animate-pulse' : 'bg-danger-500'
            }`}></div>
            <span className="text-sm font-medium">
              {isConnected ? 'Live Connected' : 'Disconnected'}
            </span>
          </div>
          
          <button
            onClick={handleStartSearch}
            disabled={isSearching}
            className="btn-primary"
          >
            {isSearching ? (
              <>
                <div className="loading-spinner w-4 h-4 mr-2"></div>
                Starting...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start AI Search
              </>
            )}
          </button>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Scholarships"
          value={currentStats?.total_scholarships}
          icon={Search}
          color="primary"
          change={currentStats?.scholarships_today}
          description="Discovered worldwide"
        />
        <StatCard
          title="Tunisia Eligible"
          value={currentStats?.tunisia_scholarships}
          icon={Target}
          color="success"
          description="Available for Tunisia students"
        />
        <StatCard
          title="Fully Funded"
          value={currentStats?.fully_funded_scholarships}
          icon={CheckCircle}
          color="warning"
          description="100% funding coverage"
        />
        <StatCard
          title="Websites Searched"
          value={currentStats?.websites_discovered}
          icon={Globe}
          color="purple"
          description="AI-discovered sources"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AI Thinking Panel */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-primary-600" />
                  <h3 className="text-lg font-semibold text-gray-900">AI Agent Thinking</h3>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">Active</span>
                </div>
              </div>
            </div>
            <div className="card-body">
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {aiThoughts.map((thought) => (
                  <AIThoughtCard key={thought.id} thought={thought} />
                ))}
                {aiThoughts.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Brain className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>AI agents are initializing...</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Recent Discoveries */}
        <div className="space-y-6">
          {/* Recent Scholarships */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-warning-600" />
                <h3 className="text-lg font-semibold text-gray-900">Recent Discoveries</h3>
              </div>
            </div>
            <div className="card-body">
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {recentScholarships.map((scholarship, index) => (
                  <RecentScholarshipCard key={index} scholarship={scholarship} />
                ))}
                {recentScholarships.length === 0 && (
                  <div className="text-center py-4 text-gray-500">
                    <Search className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">No recent discoveries</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            </div>
            <div className="card-body space-y-3">
              <button className="w-full btn-outline text-left">
                <Search className="w-4 h-4 mr-2" />
                Browse All Scholarships
              </button>
              <button className="w-full btn-outline text-left">
                <Target className="w-4 h-4 mr-2" />
                View Search Sessions
              </button>
              <button className="w-full btn-outline text-left">
                <Brain className="w-4 h-4 mr-2" />
                Monitor AI Agents
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">System Performance</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {currentStats?.success_rate ? `${Math.round(currentStats.success_rate)}%` : '0%'}
              </div>
              <div className="text-sm text-gray-600">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success-600">
                {currentStats?.average_relevance_score ? 
                  `${Math.round(currentStats.average_relevance_score * 100)}%` : '0%'}
              </div>
              <div className="text-sm text-gray-600">Avg Relevance</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-warning-600">
                {currentStats?.websites_scraped_today || '0'}
              </div>
              <div className="text-sm text-gray-600">Sites Today</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {currentStats?.ai_agents_active || '0'}
              </div>
              <div className="text-sm text-gray-600">Active Agents</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
