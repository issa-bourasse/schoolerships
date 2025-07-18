/**
 * WebSocket Service
 * 
 * Real-time communication with the Django backend
 * Handles dashboard updates, AI thinking, and search progress
 */

import toast from 'react-hot-toast'

class WebSocketService {
  constructor() {
    this.connections = new Map()
    this.reconnectAttempts = new Map()
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.listeners = new Map()
  }

  /**
   * Connect to a WebSocket endpoint
   */
  connect(endpoint, options = {}) {
    const wsUrl = this.getWebSocketUrl(endpoint)
    const connectionId = endpoint
    
    // Close existing connection if any
    if (this.connections.has(connectionId)) {
      this.disconnect(connectionId)
    }

    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log(`WebSocket connected: ${endpoint}`)
        this.connections.set(connectionId, ws)
        this.reconnectAttempts.set(connectionId, 0)
        
        // Send initial message if provided
        if (options.initialMessage) {
          this.send(connectionId, options.initialMessage)
        }
        
        // Call onOpen callback
        if (options.onOpen) {
          options.onOpen()
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(connectionId, data, options)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        console.log(`WebSocket closed: ${endpoint}`, event.code, event.reason)
        this.connections.delete(connectionId)
        
        // Call onClose callback
        if (options.onClose) {
          options.onClose(event)
        }
        
        // Attempt reconnection if not intentional close
        if (event.code !== 1000 && event.code !== 1001) {
          this.attemptReconnect(endpoint, options)
        }
      }

      ws.onerror = (error) => {
        console.error(`WebSocket error: ${endpoint}`, error)
        
        // Call onError callback
        if (options.onError) {
          options.onError(error)
        }
      }

    } catch (error) {
      console.error(`Failed to create WebSocket connection: ${endpoint}`, error)
      toast.error('Failed to establish real-time connection')
    }
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(connectionId) {
    const ws = this.connections.get(connectionId)
    if (ws) {
      ws.close(1000, 'Intentional disconnect')
      this.connections.delete(connectionId)
      this.reconnectAttempts.delete(connectionId)
    }
  }

  /**
   * Send message through WebSocket
   */
  send(connectionId, message) {
    const ws = this.connections.get(connectionId)
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
      return true
    }
    return false
  }

  /**
   * Add event listener for specific message types
   */
  addEventListener(connectionId, eventType, callback) {
    const key = `${connectionId}:${eventType}`
    if (!this.listeners.has(key)) {
      this.listeners.set(key, [])
    }
    this.listeners.get(key).push(callback)
  }

  /**
   * Remove event listener
   */
  removeEventListener(connectionId, eventType, callback) {
    const key = `${connectionId}:${eventType}`
    const listeners = this.listeners.get(key)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(connectionId, data, options) {
    // Call general message handler
    if (options.onMessage) {
      options.onMessage(data)
    }

    // Call specific event listeners
    if (data.type) {
      const key = `${connectionId}:${data.type}`
      const listeners = this.listeners.get(key)
      if (listeners) {
        listeners.forEach(callback => {
          try {
            callback(data)
          } catch (error) {
            console.error('Error in WebSocket event listener:', error)
          }
        })
      }
    }

    // Handle common message types
    this.handleCommonMessages(data)
  }

  /**
   * Handle common message types across all connections
   */
  handleCommonMessages(data) {
    switch (data.type) {
      case 'scholarship_found':
        toast.success(`New scholarship found: ${data.data?.scholarship?.name || 'Unknown'}`)
        break
        
      case 'ai_thinking':
        // AI thinking messages are handled by specific components
        break
        
      case 'search_progress':
        // Progress updates are handled by specific components
        break
        
      case 'error_occurred':
        toast.error(data.message || 'An error occurred')
        break
        
      case 'search_completed':
        toast.success('Scholarship search completed!')
        break
        
      case 'search_stopped':
        toast.info('Scholarship search stopped')
        break
        
      default:
        // Unknown message type
        break
    }
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  attemptReconnect(endpoint, options) {
    const connectionId = endpoint
    const attempts = this.reconnectAttempts.get(connectionId) || 0
    
    if (attempts >= this.maxReconnectAttempts) {
      console.log(`Max reconnection attempts reached for ${endpoint}`)
      toast.error('Lost connection to server. Please refresh the page.')
      return
    }

    const delay = this.reconnectDelay * Math.pow(2, attempts) // Exponential backoff
    
    setTimeout(() => {
      console.log(`Attempting to reconnect to ${endpoint} (attempt ${attempts + 1})`)
      this.reconnectAttempts.set(connectionId, attempts + 1)
      this.connect(endpoint, options)
    }, delay)
  }

  /**
   * Get WebSocket URL for endpoint
   */
  getWebSocketUrl(endpoint) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/ws/${endpoint}/`
  }

  /**
   * Check if connection is open
   */
  isConnected(connectionId) {
    const ws = this.connections.get(connectionId)
    return ws && ws.readyState === WebSocket.OPEN
  }

  /**
   * Get connection status
   */
  getConnectionStatus(connectionId) {
    const ws = this.connections.get(connectionId)
    if (!ws) return 'disconnected'
    
    switch (ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting'
      case WebSocket.OPEN:
        return 'connected'
      case WebSocket.CLOSING:
        return 'closing'
      case WebSocket.CLOSED:
        return 'disconnected'
      default:
        return 'unknown'
    }
  }

  /**
   * Disconnect all connections
   */
  disconnectAll() {
    this.connections.forEach((ws, connectionId) => {
      this.disconnect(connectionId)
    })
    this.listeners.clear()
  }
}

// Create singleton instance
const websocketService = new WebSocketService()

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  websocketService.disconnectAll()
})

export default websocketService
