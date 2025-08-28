/**
 * Trading Dashboard - Modular Provider Version
 * Refactored to use the modular provider system for easy AI/Voice provider switching
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TradingChart } from './TradingChart';
import { ProviderSelector } from './ProviderSelector';
import { marketDataService } from '../services/marketDataService';
import { useProvider } from '../hooks/useProvider';
import { AudioChunk } from '../providers/types';
import './TradingDashboardSimple.css';

interface StockData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  label: string;
  description: string;
  volume?: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const TradingDashboardModular: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'charts' | 'voice'>('charts');
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState('00:00');
  const [inputText, setInputText] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [stocksData, setStocksData] = useState<StockData[]>([]);
  const [isLoadingStocks, setIsLoadingStocks] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('TSLA');
  const [stockNews, setStockNews] = useState<any[]>([]);
  const [technicalLevels, setTechnicalLevels] = useState<any>({});
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  const [expandedNews, setExpandedNews] = useState<number | null>(null);
  
  // Audio processing refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Stock symbols to track
  const watchlist = ['TSLA', 'AAPL', 'NVDA', 'SPY'];
  
  // Modular Provider System - replaces hardcoded ElevenLabs hook
  const {
    isConnected,
    isConnecting,
    error: providerError,
    messages: providerMessages,
    startVoiceConversation,
    stopVoiceConversation,
    sendMessage,
    sendAudio,
    currentProvider,
    providerCapabilities,
    allowProviderSwitching,
    showProviderSelector
  } = useProvider({
    autoConnect: true,
    defaultProvider: 'elevenlabs', // Can be changed to 'openai', 'claude', etc.
    eventHandlers: {
      onConnectionChange: (connected) => {
        if (!connected) {
          setIsRecording(false);
          setIsListening(false);
          stopVoiceRecording();
        }
      }
    }
  });

  // Convert provider messages to component format
  const messages: Message[] = providerMessages.map(msg => ({
    id: msg.id,
    role: msg.role as 'user' | 'assistant',
    content: msg.content,
    timestamp: new Date(msg.timestamp).toLocaleTimeString()
  }));

  // Convert Float32 PCM to Int16 PCM and create AudioChunk
  const convertFloat32ToAudioChunk = (float32Array: Float32Array): AudioChunk => {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    
    // Convert to base64
    const bytes = new Uint8Array(int16Array.buffer);
    const binaryString = String.fromCharCode(...bytes);
    const base64 = btoa(binaryString);
    
    return {
      data: base64,
      format: 'pcm',
      sampleRate: 16000,
      channels: 1
    };
  };

  // Start voice recording - now provider-agnostic
  const startVoiceRecording = useCallback(async () => {
    if (!isConnected) {
      console.warn('Not connected to provider');
      return;
    }

    if (!providerCapabilities?.speechToText) {
      console.warn('Current provider does not support speech-to-text');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      streamRef.current = stream;
      
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000
      });
      
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;
      
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      
      processor.onaudioprocess = (event) => {
        if (isRecording) {
          const inputData = event.inputBuffer.getChannelData(0);
          
          // Calculate audio level for visualization
          const sum = inputData.reduce((acc, val) => acc + Math.abs(val), 0);
          const average = sum / inputData.length;
          setAudioLevel(Math.min(1, average * 10));
          
          // Send audio to current provider
          const audioChunk = convertFloat32ToAudioChunk(inputData);
          sendAudio(audioChunk).catch(console.error);
        }
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      setIsRecording(true);
      setIsListening(true);
      
      // Start recording timer
      let seconds = 0;
      recordingTimerRef.current = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        setRecordingTime(`${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`);
      }, 1000);
      
    } catch (error) {
      console.error('Error starting voice recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  }, [isConnected, isRecording, sendAudio, providerCapabilities?.speechToText]);

  // Stop voice recording
  const stopVoiceRecording = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    
    setIsRecording(false);
    setIsListening(false);
    setRecordingTime('00:00');
    setAudioLevel(0);
  }, []);

  // Voice conversation controls - provider-agnostic
  const handleStartVoiceChat = async () => {
    try {
      await startVoiceConversation();
      await startVoiceRecording();
    } catch (error) {
      console.error('Error starting voice chat:', error);
    }
  };

  const handleStopVoiceChat = async () => {
    stopVoiceRecording();
    try {
      await stopVoiceConversation();
    } catch (error) {
      console.error('Error stopping voice chat:', error);
    }
  };

  // Send text message - provider-agnostic
  const handleSendText = async () => {
    if (!inputText.trim()) return;
    
    try {
      await sendMessage(inputText);
      setInputText('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  // Load stock data
  useEffect(() => {
    const loadStockData = async () => {
      setIsLoadingStocks(true);
      try {
        const promises = watchlist.map(async (symbol) => {
          try {
            const data = await marketDataService.getStockPrice(symbol);
            return {
              symbol,
              price: data.price || data.last || 0,
              change: data.change || data.change_abs || 0,
              changePercent: data.change_percent || data.change_pct || 0,
              label: data.symbol || symbol,
              description: `${symbol} Stock`,
              volume: data.volume
            };
          } catch (error) {
            console.error(`Error fetching data for ${symbol}:`, error);
            return {
              symbol,
              price: 0,
              change: 0,
              changePercent: 0,
              label: symbol,
              description: `${symbol} - Error loading`,
              volume: 0
            };
          }
        });
        
        const results = await Promise.all(promises);
        setStocksData(results);
      } finally {
        setIsLoadingStocks(false);
      }
    };

    loadStockData();
    const interval = setInterval(loadStockData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Load news for selected symbol
  useEffect(() => {
    const loadNews = async () => {
      setIsLoadingNews(true);
      try {
        const news = await marketDataService.getStockNews(selectedSymbol);
        setStockNews(Array.isArray(news) ? news.slice(0, 5) : []);
      } catch (error) {
        console.error('Error loading news:', error);
        setStockNews([]);
      } finally {
        setIsLoadingNews(false);
      }
    };

    if (selectedSymbol) {
      loadNews();
    }
  }, [selectedSymbol]);

  // Provider status indicator
  const getProviderStatus = () => {
    if (providerError) return '🔴 Error';
    if (isConnecting) return '🟡 Connecting...';
    if (isConnected) return '🟢 Connected';
    return '⚫ Disconnected';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Provider Info */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">G'sves AI Market Analysis</h1>
            <p className="text-sm text-gray-600 mt-1">
              Provider: {currentProvider?.config.name || 'None'} • {getProviderStatus()}
            </p>
          </div>
          
          {/* Provider Selector - shown based on configuration */}
          {showProviderSelector && (
            <div className="max-w-xs">
              <ProviderSelector compact={true} />
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Provider Error Display */}
        {providerError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-red-500">⚠️</span>
              <span className="text-red-700 font-medium">Provider Error</span>
            </div>
            <p className="text-red-600 text-sm mt-1">{providerError}</p>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
          
          {/* Left Panel - Market Insights */}
          <div className="xl:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Market Insights</h2>
              
              {isLoadingStocks ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-16 bg-gray-200 rounded-lg"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {stocksData.map((stock) => (
                    <div 
                      key={stock.symbol}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedSymbol === stock.symbol 
                          ? 'border-blue-500 bg-blue-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedSymbol(stock.symbol)}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium text-gray-900">{stock.symbol}</div>
                          <div className="text-sm text-gray-500">${stock.price.toFixed(2)}</div>
                        </div>
                        <div className="text-right">
                          <div className={`text-sm font-medium ${
                            stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                          </div>
                          <div className="text-xs text-gray-500">
                            {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Provider Capabilities Display */}
              {providerCapabilities && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">AI Capabilities</h3>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className={`flex items-center gap-1 ${providerCapabilities.voiceConversation ? 'text-green-600' : 'text-gray-400'}`}>
                      <span>🎤</span> Voice
                    </div>
                    <div className={`flex items-center gap-1 ${providerCapabilities.textChat ? 'text-green-600' : 'text-gray-400'}`}>
                      <span>💬</span> Chat
                    </div>
                    <div className={`flex items-center gap-1 ${providerCapabilities.streaming ? 'text-green-600' : 'text-gray-400'}`}>
                      <span>⚡</span> Stream
                    </div>
                    <div className={`flex items-center gap-1 ${providerCapabilities.tools ? 'text-green-600' : 'text-gray-400'}`}>
                      <span>🛠️</span> Tools
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Center Panel - Interactive Charts & Voice */}
          <div className="xl:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              
              {/* Tab Navigation */}
              <div className="border-b border-gray-200">
                <nav className="flex">
                  <button
                    onClick={() => setActiveTab('charts')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 ${
                      activeTab === 'charts'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Interactive Charts
                  </button>
                  <button
                    onClick={() => setActiveTab('voice')}
                    className={`px-6 py-3 text-sm font-medium border-b-2 ${
                      activeTab === 'voice'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    Voice + Manual Control
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {activeTab === 'charts' && (
                  <div>
                    <div className="mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">
                        {selectedSymbol} Price Chart
                      </h3>
                      <p className="text-sm text-gray-600">
                        Real-time candlestick chart with technical levels
                      </p>
                    </div>
                    <div className="h-80">
                      <TradingChart symbol={selectedSymbol} />
                    </div>
                  </div>
                )}

                {activeTab === 'voice' && (
                  <div>
                    <div className="mb-6">
                      <h3 className="text-lg font-semibold text-gray-800 mb-2">
                        AI Voice Assistant
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Current Provider: <span className="font-medium">{currentProvider?.config.name || 'None'}</span>
                      </p>

                      {/* Voice Controls */}
                      <div className="flex items-center gap-4 mb-6">
                        <div className="relative">
                          <button
                            onClick={isListening ? handleStopVoiceChat : handleStartVoiceChat}
                            disabled={isConnecting || (!isConnected && !providerCapabilities?.voiceConversation)}
                            className={`
                              w-16 h-16 rounded-full flex items-center justify-center text-white font-semibold
                              transition-all duration-200 shadow-lg hover:shadow-xl
                              ${isListening 
                                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                                : isConnected && providerCapabilities?.voiceConversation
                                  ? 'bg-blue-500 hover:bg-blue-600'
                                  : 'bg-gray-400 cursor-not-allowed'
                              }
                            `}
                          >
                            {isConnecting ? (
                              <span className="animate-spin">⟳</span>
                            ) : isListening ? (
                              <span>⏹</span>
                            ) : (
                              <span>🎤</span>
                            )}
                          </button>

                          {/* Audio Level Visualization */}
                          {isListening && (
                            <div className="absolute inset-0 rounded-full animate-pulse">
                              <div 
                                className="absolute inset-0 rounded-full border-4 border-red-300"
                                style={{
                                  transform: `scale(${1 + audioLevel * 0.5})`,
                                  opacity: audioLevel
                                }}
                              />
                            </div>
                          )}
                        </div>

                        <div>
                          <div className="font-medium text-gray-800">
                            {isListening ? 'Stop Voice Chat' : 'Start Voice Chat'}
                          </div>
                          {isListening && (
                            <div className="text-sm text-gray-600">
                              Recording: {recordingTime}
                            </div>
                          )}
                          {!isConnected && (
                            <div className="text-sm text-red-600">
                              Not connected to provider
                            </div>
                          )}
                          {!providerCapabilities?.voiceConversation && isConnected && (
                            <div className="text-sm text-orange-600">
                              Current provider doesn't support voice
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Text Input Fallback */}
                      <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Or type your message:
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
                            placeholder="Ask about market trends, stock analysis..."
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={!isConnected}
                          />
                          <button
                            onClick={handleSendText}
                            disabled={!inputText.trim() || !isConnected}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                          >
                            Send
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Conversation History */}
                    <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                      <h4 className="font-medium text-gray-800 mb-3">Conversation History</h4>
                      {messages.length === 0 ? (
                        <p className="text-gray-500 text-sm">No messages yet. Start a conversation!</p>
                      ) : (
                        <div className="space-y-3">
                          {messages.map((message) => (
                            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                message.role === 'user' 
                                  ? 'bg-blue-600 text-white' 
                                  : 'bg-white text-gray-800'
                              }`}>
                                <div className="text-sm">{message.content}</div>
                                <div className={`text-xs mt-1 ${
                                  message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                                }`}>
                                  {message.timestamp}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel - Chart Analysis & News */}
          <div className="xl:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-4">Chart Analysis</h2>
              
              {/* News Section */}
              <div>
                <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide mb-3">
                  Latest News - {selectedSymbol}
                </h3>
                
                {isLoadingNews ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-20 bg-gray-200 rounded-lg"></div>
                      </div>
                    ))}
                  </div>
                ) : stockNews.length > 0 ? (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {stockNews.map((article, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-start justify-between">
                          <h4 className="text-sm font-medium text-gray-900 leading-tight">
                            {article.title}
                          </h4>
                          <button
                            onClick={() => setExpandedNews(expandedNews === index ? null : index)}
                            className="ml-2 text-gray-400 hover:text-gray-600 flex-shrink-0"
                          >
                            {expandedNews === index ? '▼' : '▶'}
                          </button>
                        </div>
                        
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`text-xs px-2 py-1 rounded ${
                            article.source === 'CNBC' 
                              ? 'bg-blue-100 text-blue-700' 
                              : 'bg-green-100 text-green-700'
                          }`}>
                            {article.source}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(article.published_at).toLocaleDateString()}
                          </span>
                        </div>

                        {expandedNews === index && (
                          <div className="mt-3 pt-3 border-t border-gray-100">
                            <p className="text-sm text-gray-600 leading-relaxed">
                              {article.summary}
                            </p>
                            {article.url && (
                              <a
                                href={article.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 mt-2 text-sm text-blue-600 hover:text-blue-700"
                              >
                                Read Full Article →
                              </a>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">No news available for {selectedSymbol}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};