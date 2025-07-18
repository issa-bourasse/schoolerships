/**
 * Analytics Page
 * 
 * Performance insights and data visualization
 * Charts and metrics for system monitoring
 */

import React from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  TrendingUp,
  Globe,
  Target,
  Clock,
  Award
} from 'lucide-react'

const Analytics = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-1">
          Performance insights and system metrics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Discovery Rate</p>
              <p className="text-2xl font-bold text-primary-600 mt-1">15.2/hr</p>
              <p className="text-xs text-gray-500 mt-1">Scholarships per hour</p>
            </div>
            <div className="p-3 bg-primary-100 rounded-lg">
              <Target className="w-6 h-6 text-primary-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-sm text-success-600 font-medium">+12%</span>
            <span className="text-sm text-gray-500 ml-1">vs last week</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-success-600 mt-1">87.3%</p>
              <p className="text-xs text-gray-500 mt-1">Successful extractions</p>
            </div>
            <div className="p-3 bg-success-100 rounded-lg">
              <Award className="w-6 h-6 text-success-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-sm text-success-600 font-medium">+5%</span>
            <span className="text-sm text-gray-500 ml-1">vs last week</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Websites Crawled</p>
              <p className="text-2xl font-bold text-warning-600 mt-1">1,247</p>
              <p className="text-xs text-gray-500 mt-1">Total discovered</p>
            </div>
            <div className="p-3 bg-warning-100 rounded-lg">
              <Globe className="w-6 h-6 text-warning-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-sm text-success-600 font-medium">+23</span>
            <span className="text-sm text-gray-500 ml-1">today</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-purple-600 mt-1">1.2s</p>
              <p className="text-xs text-gray-500 mt-1">AI processing time</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <TrendingUp className="w-4 h-4 text-success-500 mr-1" />
            <span className="text-sm text-success-600 font-medium">-0.3s</span>
            <span className="text-sm text-gray-500 ml-1">improvement</span>
          </div>
        </motion.div>
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Discovery Trends</h3>
          </div>
          <div className="card-body">
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Chart visualization coming soon</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Geographic Distribution</h3>
          </div>
          <div className="card-body">
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <div className="text-center">
                <Globe className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Map visualization coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Performers */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Top Performing Websites</h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {[
              { domain: 'scholarshipportal.com', scholarships: 45, success_rate: 92 },
              { domain: 'cambridge.ac.uk', scholarships: 23, success_rate: 89 },
              { domain: 'mit.edu', scholarships: 18, success_rate: 95 },
              { domain: 'ox.ac.uk', scholarships: 16, success_rate: 87 },
              { domain: 'ethz.ch', scholarships: 12, success_rate: 91 }
            ].map((site, index) => (
              <div key={site.domain} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="text-sm font-medium text-gray-500">#{index + 1}</div>
                  <div>
                    <div className="font-medium text-gray-900">{site.domain}</div>
                    <div className="text-sm text-gray-600">{site.scholarships} scholarships found</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-success-600">{site.success_rate}%</div>
                  <div className="text-xs text-gray-500">success rate</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics
