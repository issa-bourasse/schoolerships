/**
 * AI Agents Page
 * 
 * Monitor AI agent status and performance
 * View agent thinking and decision-making
 */

import React from 'react'
import { motion } from 'framer-motion'
import {
  Brain,
  Zap,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp
} from 'lucide-react'

const AIAgents = () => {
  // Mock data for now
  const agents = [
    {
      id: 1,
      name: 'Master Scholarship Hunter',
      type: 'master',
      status: 'active',
      current_task: 'Discovering new scholarship opportunities',
      last_activity: '2025-07-18T06:20:00Z',
      tasks_completed: 156,
      success_rate: 87.3,
      ai_model: 'deepseek-chat'
    }
  ]

  const thoughts = [
    {
      id: 1,
      agent: 'Master Scholarship Hunter',
      type: 'planning',
      content: 'Analyzing university websites in Europe for new scholarship opportunities',
      timestamp: '2025-07-18T06:20:00Z',
      confidence: 0.85
    },
    {
      id: 2,
      agent: 'Master Scholarship Hunter',
      type: 'discovery',
      content: 'Found 3 new fully-funded programs at ETH Zurich eligible for Tunisia students',
      timestamp: '2025-07-18T06:19:30Z',
      confidence: 0.92
    },
    {
      id: 3,
      agent: 'Master Scholarship Hunter',
      type: 'analysis',
      content: 'Verifying application deadlines and requirements for discovered scholarships',
      timestamp: '2025-07-18T06:19:00Z',
      confidence: 0.78
    }
  ]

  const AgentCard = ({ agent }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <Brain className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
              <p className="text-sm text-gray-600">{agent.type} agent</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`badge ${
              agent.status === 'active' ? 'badge-success' : 'badge-gray'
            }`}>
              {agent.status}
            </span>
            {agent.status === 'active' && (
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
            )}
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            <strong>Current Task:</strong> {agent.current_task}
          </p>
          <p className="text-sm text-gray-600">
            <strong>Last Activity:</strong> {new Date(agent.last_activity).toLocaleString()}
          </p>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <div className="text-xl font-bold text-primary-600">
              {agent.tasks_completed}
            </div>
            <div className="text-xs text-gray-600">Tasks Completed</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-success-600">
              {agent.success_rate}%
            </div>
            <div className="text-xs text-gray-600">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-warning-600">
              {agent.ai_model}
            </div>
            <div className="text-xs text-gray-600">AI Model</div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Activity className="w-4 h-4" />
            <span>Performance: Excellent</span>
          </div>
          <button className="btn-outline btn-sm">
            View Details
          </button>
        </div>
      </div>
    </motion.div>
  )

  const ThoughtCard = ({ thought }) => (
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
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-gray-900">{thought.agent}</span>
          <span className="text-xs text-gray-500">
            {new Date(thought.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <p className="text-sm text-gray-700 mb-2">{thought.content}</p>
        <div className="flex items-center justify-between">
          <span className={`badge badge-${
            thought.type === 'planning' ? 'primary' :
            thought.type === 'discovery' ? 'success' :
            'warning'
          }`}>
            {thought.type}
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Agents</h1>
          <p className="text-gray-600 mt-1">
            Monitor autonomous AI agents and their decision-making
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">{agents.length} Active</span>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {agents.map(agent => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      {/* AI Thinking Stream */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center space-x-2">
            <Brain className="w-5 h-5 text-primary-600" />
            <h3 className="text-lg font-semibold text-gray-900">AI Thinking Stream</h3>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
        <div className="card-body">
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {thoughts.map(thought => (
              <ThoughtCard key={thought.id} thought={thought} />
            ))}
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-primary-600 mb-2">156</div>
            <div className="text-sm text-gray-600">Total Tasks</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-success-600 mb-2">87.3%</div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-warning-600 mb-2">1.2s</div>
            <div className="text-sm text-gray-600">Avg Response</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-purple-600 mb-2">24/7</div>
            <div className="text-sm text-gray-600">Uptime</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIAgents
