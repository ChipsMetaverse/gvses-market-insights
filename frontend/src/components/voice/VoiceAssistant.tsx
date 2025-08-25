import React, { useState, useEffect } from 'react';
import { AudioVisualizer } from '../ui/AudioVisualizer';
import { ChatHistory } from '../ui/ChatHistory';
import { useAgentConversation } from '../../hooks/useAgentConversation';
// import { useSupabase } from '../../hooks/useSupabase'; // Will be used for direct DB operations
import '../../styles/VoiceAssistant.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const VoiceAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [inputText, setInputText] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected'>('disconnected');
  
  // const { supabase } = useSupabase(); // Will be used for direct DB operations
  const { isConnected, isStreamingAudio, audioLevel, messages: convMessages, startConversation, stopConversation, sendUserMessage } = useAgentConversation();

  useEffect(() => {
    // Generate session ID
    const newSessionId = crypto.randomUUID();
    setSessionId(newSessionId);
    setMessages([]);
  }, []);

  // Mirror conversation state into local UI state
  useEffect(() => {
    setConnectionStatus(isConnected ? 'connected' : 'disconnected');
    // Map conversation messages to local format for ChatHistory
    const mapped = convMessages.map(m => ({ role: m.role, content: m.content, timestamp: m.timestamp }));
    setMessages(mapped);
  }, [isConnected, convMessages]);

  const handleConnect = async () => {
    try {
      await startConversation();
      setIsListening(true);
    } catch (e) {
      console.error('Failed to start conversation:', e);
      setIsListening(false);
      alert('Microphone permission or connection failed.');
    }
  };

  const handleDisconnect = async () => {
    await stopConversation();
    setIsListening(false);
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !isConnected) return;
    
    const userMessage: Message = {
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);
    sendUserMessage(inputText);
    
    setInputText('');
  };

  const clearHistory = () => {
    setMessages([]);
    // Generate new session ID
    const newSessionId = crypto.randomUUID();
    setSessionId(newSessionId);
  };

  return (
    <div className="voice-assistant">
      <div className="assistant-container">
        <div className="status-bar">
          <span className={`status-indicator ${connectionStatus}`}>
            {connectionStatus === 'connected' ? '🟢' : connectionStatus === 'connecting' ? '🟡' : '🔴'}
            {' '}{connectionStatus}
          </span>
          {sessionId && (
            <span className="session-info">Session: {sessionId.slice(0, 8)}...</span>
          )}
        </div>

        <AudioVisualizer 
          isActive={isStreamingAudio} 
          audioLevel={audioLevel}
        />
        
        <div className="controls">
          <div className="voice-controls">
            <button
              className="connect-button"
              onClick={handleConnect}
              disabled={isConnected}
            >
              Start Voice Chat
            </button>
            <button
              className="disconnect-button"
              onClick={handleDisconnect}
              disabled={!isConnected}
            >
              Stop Voice Chat
            </button>
          </div>
          
          <form onSubmit={handleTextSubmit} className="text-input-form">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Or type your message..."
              disabled={isProcessing || !isConnected}
              className="text-input"
            />
            <button 
              type="submit" 
              disabled={isProcessing || !inputText.trim() || !isConnected}
              className="send-button"
            >
              Send
            </button>
          </form>

          <button onClick={clearHistory} className="clear-button">
            Clear History
          </button>
        </div>
        
        {isProcessing && (
          <div className="processing-indicator">
            <div className="spinner"></div>
            Processing...
          </div>
        )}
        
        <ChatHistory messages={messages} />
      </div>
    </div>
  );
};
