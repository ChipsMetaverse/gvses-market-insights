/**
 * Provider Test Component
 * Demonstrates the modular provider system functionality
 */

import React, { useState } from 'react';
import { useProvider } from '../hooks/useProvider';
import { ProviderSelector } from './ProviderSelector';

export function ProviderTest() {
  const [testMessage, setTestMessage] = useState('');
  const [streamingText, setStreamingText] = useState('');
  
  const {
    currentProvider,
    isConnected,
    isConnecting,
    error,
    messages,
    sendMessage,
    streamMessage,
    startVoiceConversation,
    stopVoiceConversation,
    providerCapabilities,
    providerInfo,
    clearMessages
  } = useProvider({
    autoConnect: true,
    eventHandlers: {
      onMessage: (message) => {
        console.log('New message:', message);
      },
      onConnectionChange: (state) => {
        console.log('Connection state changed:', state);
      },
      onError: (error) => {
        console.error('Provider error:', error);
      }
    }
  });

  const handleSendMessage = async () => {
    if (!testMessage.trim()) return;
    
    try {
      await sendMessage(testMessage);
      setTestMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleStreamMessage = async () => {
    if (!testMessage.trim()) return;
    
    setStreamingText('');
    try {
      for await (const chunk of streamMessage(testMessage)) {
        setStreamingText(prev => prev + chunk);
      }
      setTestMessage('');
    } catch (error) {
      console.error('Error streaming message:', error);
    }
  };

  const handleStartVoice = async () => {
    try {
      await startVoiceConversation();
      console.log('Voice conversation started');
    } catch (error) {
      console.error('Error starting voice:', error);
    }
  };

  const handleStopVoice = async () => {
    try {
      await stopVoiceConversation();
      console.log('Voice conversation stopped');
    } catch (error) {
      console.error('Error stopping voice:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          🔧 Provider System Test Interface
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Provider Selector */}
          <div>
            <h2 className="text-lg font-semibold mb-3">Provider Selection</h2>
            <ProviderSelector showCapabilities={true} />
          </div>
          
          {/* Provider Status */}
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Provider Status</h2>
            
            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Current Provider:</span>
                <span className="text-sm font-medium">
                  {currentProvider?.config.name || 'None'}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Type:</span>
                <span className="text-sm font-medium">
                  {currentProvider?.config.type || 'N/A'}
                </span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Status:</span>
                <span className={`text-sm font-medium ${
                  error ? 'text-red-600' : 
                  isConnecting ? 'text-yellow-600' : 
                  isConnected ? 'text-green-600' : 'text-gray-600'
                }`}>
                  {error ? 'Error' : 
                   isConnecting ? 'Connecting...' : 
                   isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              
              {error && (
                <div className="pt-2 border-t border-gray-200">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
            </div>

            {/* Capabilities */}
            {providerCapabilities && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium mb-2">Capabilities</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className={`flex items-center gap-2 ${
                    providerCapabilities.voiceConversation ? 'text-green-600' : 'text-gray-400'
                  }`}>
                    <span>{providerCapabilities.voiceConversation ? '✅' : '❌'}</span>
                    Voice
                  </div>
                  <div className={`flex items-center gap-2 ${
                    providerCapabilities.textChat ? 'text-green-600' : 'text-gray-400'
                  }`}>
                    <span>{providerCapabilities.textChat ? '✅' : '❌'}</span>
                    Chat
                  </div>
                  <div className={`flex items-center gap-2 ${
                    providerCapabilities.streaming ? 'text-green-600' : 'text-gray-400'
                  }`}>
                    <span>{providerCapabilities.streaming ? '✅' : '❌'}</span>
                    Streaming
                  </div>
                  <div className={`flex items-center gap-2 ${
                    providerCapabilities.tools ? 'text-green-600' : 'text-gray-400'
                  }`}>
                    <span>{providerCapabilities.tools ? '✅' : '❌'}</span>
                    Tools
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Test Controls */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Test Controls</h2>
        
        <div className="space-y-4">
          {/* Text Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Message
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Enter a test message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!isConnected}
              />
              <button
                onClick={handleSendMessage}
                disabled={!testMessage.trim() || !isConnected || !providerCapabilities?.textChat}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Send
              </button>
              <button
                onClick={handleStreamMessage}
                disabled={!testMessage.trim() || !isConnected || !providerCapabilities?.streaming}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Stream
              </button>
            </div>
          </div>

          {/* Voice Controls */}
          <div className="flex gap-2">
            <button
              onClick={handleStartVoice}
              disabled={!isConnected || !providerCapabilities?.voiceConversation}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Start Voice
            </button>
            <button
              onClick={handleStopVoice}
              disabled={!isConnected || !providerCapabilities?.voiceConversation}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Stop Voice
            </button>
            <button
              onClick={clearMessages}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Clear Messages
            </button>
          </div>
        </div>

        {/* Streaming Text Display */}
        {streamingText && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="text-sm font-medium text-green-800 mb-2">Streaming Response:</h3>
            <div className="text-sm text-green-700 whitespace-pre-wrap">{streamingText}</div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Messages</h2>
          <span className="text-sm text-gray-500">
            {messages.length} messages
          </span>
        </div>
        
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No messages yet. Send a test message to see provider responses!
            </p>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}>
                <div className={`max-w-2xl px-4 py-2 rounded-lg ${
                  message.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <div className="text-sm mb-1">
                    <strong>{message.role === 'user' ? 'You' : currentProvider?.config.name}:</strong>
                  </div>
                  <div className="text-sm">{message.content}</div>
                  <div className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Debug Info */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold mb-4">Debug Information</h2>
        <pre className="text-xs bg-gray-50 p-4 rounded overflow-auto max-h-64">
          {JSON.stringify({
            providerInfo,
            providerCapabilities,
            messagesCount: messages.length,
            isConnected,
            isConnecting,
            error
          }, null, 2)}
        </pre>
      </div>
    </div>
  );
}