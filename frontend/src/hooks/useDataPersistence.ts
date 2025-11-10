/**
 * useDataPersistence Hook
 * Handles persisting chat messages and market data to Supabase
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { getApiUrl } from '../utils/apiConfig';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  provider?: string;
  model?: string;
  metadata?: any;
}

interface PersistenceConfig {
  autoSave?: boolean;
  saveInterval?: number; // milliseconds
  maxBatchSize?: number;
}

const DEFAULT_CONFIG: PersistenceConfig = {
  autoSave: true,
  saveInterval: 2000, // 2 seconds
  maxBatchSize: 10
};

export function useDataPersistence(config: PersistenceConfig = DEFAULT_CONFIG) {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  
  const pendingMessages = useRef<Message[]>([]);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const apiUrl = getApiUrl();
  
  // Create a new conversation
  const createConversation = useCallback(async (userId?: string, metadata?: any) => {
    try {
      const response = await fetch(`${apiUrl}/api/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, metadata })
      });
      
      if (!response.ok) throw new Error('Failed to create conversation');
      
      const data = await response.json();
      setConversationId(data.conversation_id);
      setConversationHistory([]);
      console.log('[DataPersistence] Created conversation:', data.conversation_id);
      return data.conversation_id;
    } catch (err) {
      console.error('[DataPersistence] Error creating conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to create conversation');
      return null;
    }
  }, [apiUrl]);
  
  // Save a single message immediately
  const saveMessage = useCallback(async (message: Message) => {
    if (!conversationId) {
      console.warn('[DataPersistence] No conversation ID, creating new conversation');
      const newConvId = await createConversation();
      if (!newConvId) return false;
    }
    
    try {
      const response = await fetch(`${apiUrl}/api/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          role: message.role,
          content: message.content,
          provider: message.provider,
          model: message.model,
          metadata: message.metadata
        })
      });
      
      if (!response.ok) throw new Error('Failed to save message');
      
      console.log('[DataPersistence] Saved message:', message.id);
      return true;
    } catch (err) {
      console.error('[DataPersistence] Error saving message:', err);
      setError(err instanceof Error ? err.message : 'Failed to save message');
      return false;
    }
  }, [conversationId, apiUrl, createConversation]);
  
  // Queue a message for batch saving
  const queueMessage = useCallback((message: Message) => {
    pendingMessages.current.push(message);
    
    // Add to local history immediately
    setConversationHistory(prev => [...prev, message]);
    
    if (config.autoSave) {
      // Clear existing timeout
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
      
      // Set new timeout or trigger immediate save if batch is full
      if (pendingMessages.current.length >= (config.maxBatchSize || DEFAULT_CONFIG.maxBatchSize!)) {
        flushMessages();
      } else {
        saveTimeoutRef.current = setTimeout(() => {
          flushMessages();
        }, config.saveInterval || DEFAULT_CONFIG.saveInterval);
      }
    }
  }, [config]);
  
  // Flush all pending messages
  const flushMessages = useCallback(async () => {
    if (pendingMessages.current.length === 0) return;
    
    setIsSaving(true);
    const messagesToSave = [...pendingMessages.current];
    pendingMessages.current = [];
    
    try {
      // Save all messages in parallel
      const savePromises = messagesToSave.map(msg => saveMessage(msg));
      await Promise.all(savePromises);
      console.log(`[DataPersistence] Flushed ${messagesToSave.length} messages`);
    } catch (err) {
      console.error('[DataPersistence] Error flushing messages:', err);
      // Put failed messages back in queue
      pendingMessages.current = [...messagesToSave, ...pendingMessages.current];
    } finally {
      setIsSaving(false);
    }
  }, [saveMessage]);
  
  // Load conversation history
  const loadConversationHistory = useCallback(async (convId: string, limit: number = 50) => {
    try {
      const response = await fetch(
        `${apiUrl}/api/conversations/${convId}/messages?limit=${limit}`
      );
      
      if (!response.ok) throw new Error('Failed to load conversation history');
      
      const data = await response.json();
      setConversationHistory(data.messages || []);
      console.log(`[DataPersistence] Loaded ${data.messages?.length || 0} messages`);
      return data.messages || [];
    } catch (err) {
      console.error('[DataPersistence] Error loading history:', err);
      setError(err instanceof Error ? err.message : 'Failed to load history');
      return [];
    }
  }, [apiUrl]);
  
  // Get recent conversations
  const getRecentConversations = useCallback(async (userId?: string, days: number = 7) => {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      params.append('days', days.toString());
      
      const response = await fetch(`${apiUrl}/api/conversations/recent?${params}`);
      
      if (!response.ok) throw new Error('Failed to get recent conversations');
      
      const data = await response.json();
      console.log(`[DataPersistence] Found ${data.conversations?.length || 0} recent conversations`);
      return data.conversations || [];
    } catch (err) {
      console.error('[DataPersistence] Error getting recent conversations:', err);
      setError(err instanceof Error ? err.message : 'Failed to get recent conversations');
      return [];
    }
  }, [apiUrl]);
  
  // Cache market data
  const cacheMarketData = useCallback(async (symbol: string, timeframe: string, candles: any[], source: string = 'alpaca') => {
    try {
      const response = await fetch(`${apiUrl}/api/market-data/cache`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol,
          timeframe,
          candles,
          source
        })
      });
      
      if (!response.ok) throw new Error('Failed to cache market data');
      
      const data = await response.json();
      console.log(`[DataPersistence] Cached ${data.candles_saved} candles for ${symbol}`);
      return true;
    } catch (err) {
      console.error('[DataPersistence] Error caching market data:', err);
      return false;
    }
  }, [apiUrl]);
  
  // Cache news articles
  const cacheNews = useCallback(async (articles: any[], symbol?: string) => {
    try {
      const response = await fetch(`${apiUrl}/api/news/cache`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          articles,
          symbol
        })
      });
      
      if (!response.ok) throw new Error('Failed to cache news');
      
      const data = await response.json();
      console.log(`[DataPersistence] Cached ${data.articles_saved} news articles`);
      return true;
    } catch (err) {
      console.error('[DataPersistence] Error caching news:', err);
      return false;
    }
  }, [apiUrl]);
  
  // End conversation
  const endConversation = useCallback(async () => {
    if (!conversationId) return;
    
    // Flush any pending messages first
    await flushMessages();
    
    try {
      const response = await fetch(`${apiUrl}/api/conversations/${conversationId}/end`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Failed to end conversation');
      
      console.log('[DataPersistence] Ended conversation:', conversationId);
      setConversationId(null);
      setConversationHistory([]);
    } catch (err) {
      console.error('[DataPersistence] Error ending conversation:', err);
      setError(err instanceof Error ? err.message : 'Failed to end conversation');
    }
  }, [conversationId, apiUrl, flushMessages]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
      // Flush any remaining messages
      flushMessages();
    };
  }, [flushMessages]);
  
  return {
    // State
    conversationId,
    conversationHistory,
    isSaving,
    error,
    
    // Actions
    createConversation,
    saveMessage,
    queueMessage,
    flushMessages,
    loadConversationHistory,
    getRecentConversations,
    endConversation,
    cacheMarketData,
    cacheNews,
    
    // Utilities
    clearError: () => setError(null)
  };
}