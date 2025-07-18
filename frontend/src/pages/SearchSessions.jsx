/**
 * Search Sessions Page
 * 
 * Monitor AI search sessions and progress
 * Start new searches and view historical data
 */

import React from 'react'
import { motion } from 'framer-motion'
import {
  Play,
  Pause,
  RotateCcw,
  Clock,
  Target,
  TrendingUp,
  Brain,
  Globe
} from 'lucide-react'

const SearchSessions = () => {
  // Mock data for now
  const sessions = [
    {
      id: 1,
      name: 'AI Scholarship Discovery Session',
      status: 'running',
      started_at: '2025-07-18T06:00:00Z',
      target_scholarships: 10000,
      scholarships_found: 200,
      websites_searched: 25,
      progress_percentage: 2,
      ai_model_used: 'deepseek-chat'
    }
  ]

  const SessionCard = ({ session }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{session.name}</h3>
            <p className="text-sm text-gray-600">Started {new Date(session.started_at).toLocaleString()}</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`badge ${
              session.status === 'running' ? 'badge-success' :
              session.status === 'completed' ? 'badge-primary' :
              'badge-gray'
            }`}>
              {session.status}
            </span>
            {session.status === 'running' && (
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
            )}
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {session.scholarships_found.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Found</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">
              {session.target_scholarships.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Target</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-warning-600">
              {session.websites_searched}
            </div>
            <div className="text-sm text-gray-600">Websites</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {session.progress_percentage}%
            </div>
            <div className="text-sm text-gray-600">Progress</div>
          </div>
        </div>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Progress</span>
            <span className="text-sm font-medium">{session.progress_percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${session.progress_percentage}%` }}
            ></div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Brain className="w-4 h-4" />
            <span>AI Model: {session.ai_model_used}</span>
          </div>
          <div className="flex space-x-2">
            {session.status === 'running' ? (
              <button className="btn-secondary btn-sm">
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </button>
            ) : (
              <button className="btn-primary btn-sm">
                <Play className="w-4 h-4 mr-1" />
                Resume
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Search Sessions</h1>
          <p className="text-gray-600 mt-1">
            Monitor AI-powered scholarship discovery sessions
          </p>
        </div>
        
        <button className="btn-primary">
          <Play className="w-4 h-4 mr-2" />
          Start New Search
        </button>
      </div>

      {/* Active Sessions */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Active Sessions</h2>
        {sessions.filter(s => s.status === 'running').map(session => (
          <SessionCard key={session.id} session={session} />
        ))}
      </div>

      {/* Recent Sessions */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Recent Sessions</h2>
        {sessions.filter(s => s.status !== 'running').map(session => (
          <SessionCard key={session.id} session={session} />
        ))}
      </div>

      {/* Empty State */}
      {sessions.length === 0 && (
        <div className="text-center py-12">
          <Target className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No search sessions</h3>
          <p className="text-gray-600 mb-4">Start your first AI-powered scholarship search.</p>
          <button className="btn-primary">
            <Play className="w-4 h-4 mr-2" />
            Start Search Session
          </button>
        </div>
      )}
    </div>
  )
}

export default SearchSessions
