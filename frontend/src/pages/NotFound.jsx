/**
 * 404 Not Found Page
 */

import React from 'react'
import { Link } from 'react-router-dom'
import { Home, Search } from 'lucide-react'

const NotFound = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl font-bold text-gray-300 mb-4">404</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Page Not Found</h1>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="flex items-center justify-center space-x-4">
          <Link to="/" className="btn-primary">
            <Home className="w-4 h-4 mr-2" />
            Go Home
          </Link>
          <Link to="/scholarships" className="btn-outline">
            <Search className="w-4 h-4 mr-2" />
            Browse Scholarships
          </Link>
        </div>
      </div>
    </div>
  )
}

export default NotFound
