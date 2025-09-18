/**
 * Redesigned Provider Selector Component
 * Clean, modern UI for switching between AI/Voice providers
 */

import React, { useState } from 'react';
import { useProvider } from '../hooks/useProvider';

interface ProviderSelectorRedesignedProps {
  className?: string;
  compact?: boolean;
}

export function ProviderSelectorRedesigned({ 
  className = '', 
  compact = false 
}: ProviderSelectorRedesignedProps) {
  const {
    currentProvider,
    availableProviders,
    switchToElevenLabs,
    switchToOpenAI,
    switchToOpenAIRealtime,
    switchToClaude,
    isConnected,
    isConnecting,
    error,
    allowProviderSwitching
  } = useProvider();

  const [showApiKeyInput, setShowApiKeyInput] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<{ [key: string]: string }>({});
  const [isExpanded, setIsExpanded] = useState(!compact);

  if (!allowProviderSwitching) {
    return null;
  }

  const handleProviderSwitch = async (providerType: string) => {
    try {
      switch (providerType) {
        case 'elevenlabs':
          await switchToElevenLabs('agent_4901k2tkkq54f4mvgpndm3pgzm7g');
          setIsExpanded(false);
          break;
        
        case 'openai':
          if (!apiKeys.openai) {
            setShowApiKeyInput('openai');
            return;
          }
          await switchToOpenAI(apiKeys.openai);
          setIsExpanded(false);
          break;
        
        case 'openai-realtime':
          await switchToOpenAIRealtime();
          setIsExpanded(false);
          break;
        
        case 'claude':
          if (!apiKeys.claude) {
            setShowApiKeyInput('claude');
            return;
          }
          await switchToClaude(apiKeys.claude);
          setIsExpanded(false);
          break;
      }
    } catch (error) {
      console.error('Failed to switch provider:', error);
    }
  };

  const handleApiKeySubmit = async (providerType: string) => {
    const apiKey = apiKeys[providerType];
    if (!apiKey) return;

    try {
      switch (providerType) {
        case 'openai':
          await switchToOpenAI(apiKey);
          break;
        case 'claude':
          await switchToClaude(apiKey);
          break;
      }
      setShowApiKeyInput(null);
      setIsExpanded(false);
    } catch (error) {
      console.error('Failed to set up provider:', error);
    }
  };

  const getProviderIcon = (type: string) => {
    switch (type) {
      case 'elevenlabs': return (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      );
      case 'openai': return (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      );
      case 'openai-realtime': return (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 15c1.66 0 3-1.34 3-3V6c0-1.66-1.34-3-3-3S9 4.34 9 6v6c0 1.66 1.34 3 3 3zm5-3c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-2.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
      );
      case 'claude': return (
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
        </svg>
      );
      default: return null;
    }
  };

  const getProviderDisplayName = (type: string) => {
    switch (type) {
      case 'elevenlabs': return 'ElevenLabs';
      case 'openai': return 'OpenAI GPT';
      case 'openai-realtime': return 'OpenAI Realtime';
      case 'claude': return 'Claude';
      default: return type;
    }
  };

  const getConnectionStatusBadge = () => {
    if (isConnecting) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <svg className="animate-spin -ml-0.5 mr-1.5 h-3 w-3 text-yellow-800" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Connecting
        </span>
      );
    }
    if (isConnected) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <svg className="-ml-0.5 mr-1.5 h-3 w-3 text-green-800" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          Connected
        </span>
      );
    }
    if (error) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
          <svg className="-ml-0.5 mr-1.5 h-3 w-3 text-red-800" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          Error
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        Disconnected
      </span>
    );
  };

  if (compact && !isExpanded) {
    return (
      <div className={`inline-flex items-center ${className}`}>
        <button
          onClick={() => setIsExpanded(true)}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            {currentProvider && getProviderIcon(currentProvider.config.type)}
            <span className="font-medium">
              {currentProvider ? getProviderDisplayName(currentProvider.config.type) : 'Select Provider'}
            </span>
          </div>
          {getConnectionStatusBadge()}
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">AI Provider</h3>
          {compact && (
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Current Provider Status */}
      {currentProvider && (
        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-gray-600">
                {getProviderIcon(currentProvider.config.type)}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {getProviderDisplayName(currentProvider.config.type)}
                </p>
                <p className="text-xs text-gray-500">Currently Active</p>
              </div>
            </div>
            {getConnectionStatusBadge()}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mx-4 mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* API Key Input */}
      {showApiKeyInput && (
        <div className="px-4 py-3 bg-blue-50 border-b border-blue-200">
          <p className="text-sm text-blue-800 mb-2">
            Enter your {showApiKeyInput.toUpperCase()} API key:
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              placeholder="API Key"
              value={apiKeys[showApiKeyInput] || ''}
              onChange={(e) => setApiKeys(prev => ({
                ...prev,
                [showApiKeyInput]: e.target.value
              }))}
              className="flex-1 px-3 py-2 text-sm border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleApiKeySubmit(showApiKeyInput)}
              disabled={!apiKeys[showApiKeyInput]}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Connect
            </button>
            <button
              onClick={() => setShowApiKeyInput(null)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Available Providers */}
      <div className="p-4">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Available Providers</p>
        <div className="space-y-2">
          {availableProviders.map((provider) => {
            const isActive = currentProvider?.config.type === provider.type;
            const needsApiKey = !provider.available && provider.type !== 'openai-realtime';
            
            return (
              <div
                key={provider.type}
                className={`flex items-center justify-between p-3 rounded-lg border ${
                  isActive 
                    ? 'bg-blue-50 border-blue-200' 
                    : 'bg-white border-gray-200 hover:bg-gray-50'
                } transition-colors`}
              >
                <div className="flex items-center gap-3">
                  <div className={isActive ? 'text-blue-600' : 'text-gray-600'}>
                    {getProviderIcon(provider.type)}
                  </div>
                  <div>
                    <p className={`text-sm font-medium ${isActive ? 'text-blue-900' : 'text-gray-900'}`}>
                      {getProviderDisplayName(provider.type)}
                    </p>
                    {needsApiKey && (
                      <p className="text-xs text-orange-600">API Key Required</p>
                    )}
                  </div>
                </div>
                
                {!isActive && (
                  <button
                    onClick={() => handleProviderSwitch(provider.type)}
                    disabled={isConnecting}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                      needsApiKey
                        ? 'text-orange-700 bg-orange-100 hover:bg-orange-200'
                        : 'text-blue-700 bg-blue-100 hover:bg-blue-200'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {needsApiKey ? 'Setup' : 'Switch'}
                  </button>
                )}
                {isActive && (
                  <span className="px-3 py-1.5 text-xs font-medium text-green-700 bg-green-100 rounded-md">
                    Active
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Links */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex gap-2">
          <button
            onClick={() => window.open('https://elevenlabs.io/app/conversational-ai', '_blank')}
            className="flex-1 px-3 py-2 text-xs font-medium text-purple-700 bg-purple-100 rounded-md hover:bg-purple-200 transition-colors"
          >
            Get ElevenLabs
          </button>
          <button
            onClick={() => window.open('https://platform.openai.com/api-keys', '_blank')}
            className="flex-1 px-3 py-2 text-xs font-medium text-green-700 bg-green-100 rounded-md hover:bg-green-200 transition-colors"
          >
            Get OpenAI Key
          </button>
        </div>
      </div>
    </div>
  );
}