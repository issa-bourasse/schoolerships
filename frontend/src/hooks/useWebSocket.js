/**
 * WebSocket Hook
 * 
 * React hook for managing WebSocket connections
 * Provides real-time data updates and connection management
 */

import { useEffect, useRef, useCallback, useState } from 'react'
import websocketService from '../services/websocket'

export const useWebSocket = (endpoint, options = {}) => {
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [lastMessage, setLastMessage] = useState(null)
  const [error, setError] = useState(null)
  const optionsRef = useRef(options)
  
  // Update options ref when options change
  useEffect(() => {
    optionsRef.current = options
  }, [options])

  // Connect to WebSocket
  useEffect(() => {
    if (!endpoint) return

    const wsOptions = {
      onOpen: () => {
        setConnectionStatus('connected')
        setError(null)
        if (optionsRef.current.onOpen) {
          optionsRef.current.onOpen()
        }
      },
      
      onMessage: (data) => {
        setLastMessage(data)
        if (optionsRef.current.onMessage) {
          optionsRef.current.onMessage(data)
        }
      },
      
      onClose: (event) => {
        setConnectionStatus('disconnected')
        if (optionsRef.current.onClose) {
          optionsRef.current.onClose(event)
        }
      },
      
      onError: (error) => {
        setError(error)
        setConnectionStatus('error')
        if (optionsRef.current.onError) {
          optionsRef.current.onError(error)
        }
      },
      
      initialMessage: optionsRef.current.initialMessage,
    }

    websocketService.connect(endpoint, wsOptions)
    setConnectionStatus('connecting')

    // Cleanup on unmount
    return () => {
      websocketService.disconnect(endpoint)
    }
  }, [endpoint])

  // Send message function
  const sendMessage = useCallback((message) => {
    return websocketService.send(endpoint, message)
  }, [endpoint])

  // Add event listener function
  const addEventListener = useCallback((eventType, callback) => {
    websocketService.addEventListener(endpoint, eventType, callback)
    
    // Return cleanup function
    return () => {
      websocketService.removeEventListener(endpoint, eventType, callback)
    }
  }, [endpoint])

  return {
    connectionStatus,
    lastMessage,
    error,
    sendMessage,
    addEventListener,
    isConnected: connectionStatus === 'connected',
  }
}

export const useDashboardWebSocket = (options = {}) => {
  return useWebSocket('dashboard', options)
}

export const useSearchWebSocket = (sessionId, options = {}) => {
  return useWebSocket(sessionId ? `search/${sessionId}` : null, options)
}

export const useAIChatWebSocket = (options = {}) => {
  return useWebSocket('ai-chat', options)
}
