/**
 * Layout Component
 * 
 * Main application layout with navigation and sidebar
 * Responsive design with mobile support
 */

import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home,
  Search,
  Bot,
  BarChart3,
  Settings,
  Menu,
  X,
  Zap,
  Globe,
  Target,
  Brain,
  Wifi,
  WifiOff
} from 'lucide-react'
import { useDashboardWebSocket } from '../hooks/useWebSocket'
import { useScholarshipStatistics } from '../hooks/useScholarships'

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  
  // Real-time connection status
  const { isConnected } = useDashboardWebSocket()
  
  // Get live statistics
  const { data: stats } = useScholarshipStatistics()

  const navigation = [
    {
      name: 'Dashboard',
      href: '/',
      icon: Home,
      description: 'Real-time overview'
    },
    {
      name: 'Scholarships',
      href: '/scholarships',
      icon: Search,
      description: 'Browse all scholarships',
      badge: stats?.total_scholarships
    },
    {
      name: 'Live AI Hunter',
      href: '/live-hunter',
      icon: Zap,
      description: 'Watch AI hunt live',
      highlight: true
    },
    {
      name: 'Search Sessions',
      href: '/search-sessions',
      icon: Target,
      description: 'AI search progress'
    },
    {
      name: 'AI Agents',
      href: '/ai-agents',
      icon: Bot,
      description: 'Agent monitoring'
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      description: 'Performance insights'
    }
  ]

  const isCurrentPath = (path) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex flex-col h-full">
          {/* Logo and header */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">AI Hunter</h1>
                <p className="text-xs text-gray-500">Scholarship Discovery</p>
              </div>
            </div>
            
            {/* Mobile close button */}
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Connection status */}
          <div className="px-6 py-3 border-b border-gray-100">
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <>
                  <Wifi className="w-4 h-4 text-success-500" />
                  <span className="text-sm text-success-600 font-medium">Live Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-danger-500" />
                  <span className="text-sm text-danger-600 font-medium">Disconnected</span>
                </>
              )}
            </div>
          </div>

          {/* Quick stats */}
          {stats && (
            <div className="px-6 py-4 border-b border-gray-100">
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center">
                  <div className="text-lg font-bold text-primary-600">
                    {stats.total_scholarships?.toLocaleString() || '0'}
                  </div>
                  <div className="text-xs text-gray-500">Total Found</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-success-600">
                    {stats.tunisia_scholarships?.toLocaleString() || '0'}
                  </div>
                  <div className="text-xs text-gray-500">Tunisia Eligible</div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = isCurrentPath(item.href)
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`flex-shrink-0 w-5 h-5 mr-3 ${
                    isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span>{item.name}</span>
                      {item.badge && (
                        <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-800 rounded-full">
                          {item.badge.toLocaleString()}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <Zap className="w-4 h-4" />
              <span>Powered by AI</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
              <Globe className="w-4 h-4" />
              <span>Global Search</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 bg-white border-b border-gray-200 lg:px-6">
          {/* Mobile menu button */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Page title */}
          <div className="flex-1 lg:flex-none">
            <h2 className="text-lg font-semibold text-gray-900">
              {navigation.find(item => isCurrentPath(item.href))?.name || 'Dashboard'}
            </h2>
          </div>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Live indicator */}
            {isConnected && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600 hidden sm:inline">Live</span>
              </div>
            )}

            {/* Settings button */}
            <button className="p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-lg">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1">
          <div className="p-4 lg:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
