import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LiveAIHunter = () => {
  const [isHunting, setIsHunting] = useState(false);
  const [currentWebsite, setCurrentWebsite] = useState('');
  const [browserContent, setBrowserContent] = useState('');
  const [aiThoughts, setAiThoughts] = useState([]);
  const [foundScholarships, setFoundScholarships] = useState([]);
  const [huntingStats, setHuntingStats] = useState({
    websitesVisited: 0,
    scholarshipsFound: 0,
    tunisiaEligible: 0,
    timeElapsed: 0
  });
  const [currentAction, setCurrentAction] = useState('');
  const [browserHistory, setBrowserHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const timerRef = useRef(null);
  const wsRef = useRef(null);

  // Simulate browser navigation
  const simulateBrowserNavigation = (url, content) => {
    setCurrentWebsite(url);
    setBrowserContent(content);
    setBrowserHistory(prev => [...prev.slice(-4), { url, timestamp: new Date() }]);
    setIsLoading(true);
    
    // Simulate loading time
    setTimeout(() => setIsLoading(false), 1500);
  };

  // Add AI thought
  const addAIThought = (thought, type = 'thinking') => {
    setAiThoughts(prev => [...prev.slice(-10), {
      id: Date.now(),
      thought,
      type,
      timestamp: new Date()
    }]);
  };

  // Start AI hunting
  const startHunting = async () => {
    setIsHunting(true);
    setHuntingStats({ websitesVisited: 0, scholarshipsFound: 0, tunisiaEligible: 0, timeElapsed: 0 });
    setFoundScholarships([]);
    setAiThoughts([]);
    setBrowserHistory([]);
    
    // Start timer
    timerRef.current = setInterval(() => {
      setHuntingStats(prev => ({ ...prev, timeElapsed: prev.timeElapsed + 1 }));
    }, 1000);

    // Connect to WebSocket for real-time updates
    wsRef.current = new WebSocket('ws://localhost:8000/ws/ai-hunter/');

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    // Start the AI hunting process
    try {
      const response = await fetch('http://localhost:8000/api/ai-agent/start-live-hunt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_countries: ['Tunisia'],
          fields: ['Computer Science', 'AI', 'Machine Learning', 'Web Development'],
          live_mode: true
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to start hunting');
      }
    } catch (error) {
      console.error('Error starting hunt:', error);
      addAIThought('❌ Error starting hunt: ' + error.message, 'error');
    }
  };

  // Stop hunting
  const stopHunting = () => {
    setIsHunting(false);
    setCurrentAction('Hunt stopped by user');
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'ai_thought':
        addAIThought(data.message, 'thinking');
        break;
      case 'website_visit':
        setCurrentAction(`Visiting ${data.url}`);
        simulateBrowserNavigation(data.url, data.content || 'Loading website content...');
        setHuntingStats(prev => ({ ...prev, websitesVisited: prev.websitesVisited + 1 }));
        break;
      case 'scholarship_found':
        const scholarship = data.scholarship;
        setFoundScholarships(prev => [...prev, scholarship]);
        setHuntingStats(prev => ({
          ...prev,
          scholarshipsFound: prev.scholarshipsFound + 1,
          tunisiaEligible: scholarship.tunisia_eligible ? prev.tunisiaEligible + 1 : prev.tunisiaEligible
        }));
        addAIThought(`🎉 Found scholarship: ${scholarship.name}`, 'success');
        break;
      case 'ai_decision':
        addAIThought(`🤔 Decision: ${data.message}`, 'decision');
        break;
      case 'error':
        addAIThought(`❌ Error: ${data.message}`, 'error');
        break;
      case 'status':
        setCurrentAction(data.message);
        break;
    }
  };

  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">🤖 Live AI Scholarship Hunter</h1>
        <p className="text-gray-400">Watch the AI hunt for scholarships in real-time</p>
      </div>

      {/* Control Panel */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {!isHunting ? (
              <button
                onClick={startHunting}
                className="bg-green-600 hover:bg-green-700 px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                🚀 Start AI Hunt
              </button>
            ) : (
              <button
                onClick={stopHunting}
                className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded-lg font-semibold transition-colors"
              >
                ⏹️ Stop Hunt
              </button>
            )}
            
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isHunting ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
              <span className="text-sm">{isHunting ? 'Hunting Active' : 'Idle'}</span>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center space-x-6 text-sm">
            <div>⏱️ {formatTime(huntingStats.timeElapsed)}</div>
            <div>🌐 {huntingStats.websitesVisited} sites</div>
            <div>🎓 {huntingStats.scholarshipsFound} found</div>
            <div>🇹🇳 {huntingStats.tunisiaEligible} Tunisia eligible</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Browser Simulation */}
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <div className="bg-gray-700 px-4 py-2 flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <div className="flex-1 bg-gray-600 rounded px-3 py-1 text-sm">
              {currentWebsite || 'about:blank'}
            </div>
            {isLoading && <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>}
          </div>
          
          <div className="h-96 p-4 overflow-y-auto bg-white text-black">
            {browserContent ? (
              <div className="space-y-2">
                <div className="text-lg font-bold text-blue-600">
                  {currentWebsite.includes('cambridge') && '🎓 University of Cambridge'}
                  {currentWebsite.includes('mit') && '🏛️ Massachusetts Institute of Technology'}
                  {currentWebsite.includes('stanford') && '🌟 Stanford University'}
                  {currentWebsite.includes('scholarshipportal') && '📚 ScholarshipPortal.com'}
                  {currentWebsite.includes('fulbright') && '🇺🇸 Fulbright Commission'}
                  {!currentWebsite.includes('cambridge') && !currentWebsite.includes('mit') && 
                   !currentWebsite.includes('stanford') && !currentWebsite.includes('scholarshipportal') && 
                   !currentWebsite.includes('fulbright') && '🌐 Scholarship Website'}
                </div>
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {browserContent}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <div className="text-4xl mb-2">🌐</div>
                  <div>Waiting for AI to start browsing...</div>
                </div>
              </div>
            )}
          </div>

          {/* Browser History */}
          <div className="bg-gray-700 px-4 py-2">
            <div className="text-xs text-gray-400 mb-1">Recent Sites:</div>
            <div className="flex space-x-2 overflow-x-auto">
              {browserHistory.map((site, index) => (
                <div key={index} className="text-xs bg-gray-600 px-2 py-1 rounded whitespace-nowrap">
                  {site.url.split('/')[2] || site.url}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Thoughts & Actions */}
        <div className="space-y-6">
          {/* Current Action */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">🎯 Current Action</h3>
            <div className="text-blue-400">
              {currentAction || 'Waiting to start...'}
            </div>
          </div>

          {/* AI Thoughts Stream */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-2">🧠 AI Thoughts</h3>
            <div className="h-64 overflow-y-auto space-y-2">
              <AnimatePresence>
                {aiThoughts.map((thought) => (
                  <motion.div
                    key={thought.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`text-sm p-2 rounded ${
                      thought.type === 'error' ? 'bg-red-900/50 text-red-300' :
                      thought.type === 'success' ? 'bg-green-900/50 text-green-300' :
                      thought.type === 'decision' ? 'bg-blue-900/50 text-blue-300' :
                      'bg-gray-700 text-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <span>{thought.thought}</span>
                      <span className="text-xs text-gray-500 ml-2">
                        {thought.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {aiThoughts.length === 0 && (
                <div className="text-gray-500 text-center py-8">
                  AI thoughts will appear here when hunting starts...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Found Scholarships */}
      <div className="mt-6 bg-gray-800 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">🎓 Scholarships Found ({foundScholarships.length})</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {foundScholarships.map((scholarship, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gray-700 rounded-lg p-4"
              >
                <h4 className="font-semibold text-sm mb-2">{scholarship.name}</h4>
                <div className="text-xs text-gray-400 space-y-1">
                  <div>🏛️ {scholarship.provider}</div>
                  <div>🌍 {scholarship.country}</div>
                  <div className={`${scholarship.tunisia_eligible ? 'text-green-400' : 'text-red-400'}`}>
                    🇹🇳 {scholarship.tunisia_eligible ? 'Tunisia Eligible' : 'Not Eligible'}
                  </div>
                  <div>🤖 AI Score: {Math.round(scholarship.ai_relevance_score * 100)}%</div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
        {foundScholarships.length === 0 && (
          <div className="text-gray-500 text-center py-8">
            Found scholarships will appear here...
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveAIHunter;
