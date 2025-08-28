/**
 * Provider Selector Component
 * Allows users to switch between different AI/Voice providers
 */

import React, { useState } from 'react';
import { useProvider } from '../hooks/useProvider';
import { ProviderConfig } from '../providers/types';

interface ProviderSelectorProps {
  className?: string;
  showCapabilities?: boolean;
  compact?: boolean;
}

export function ProviderSelector({ 
  className = '', 
  showCapabilities = true, 
  compact = false 
}: ProviderSelectorProps) {
  const {
    currentProvider,
    availableProviders,
    switchProvider,
    switchToElevenLabs,
    switchToOpenAI,
    switchToClaude,
    isConnected,
    isConnecting,
    error,
    providerCapabilities,
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
          break;
        
        case 'openai':
          if (!apiKeys.openai) {
            setShowApiKeyInput('openai');
            return;
          }
          await switchToOpenAI(apiKeys.openai);
          break;
        
        case 'claude':
          if (!apiKeys.claude) {
            setShowApiKeyInput('claude');
            return;
          }
          await switchToClaude(apiKeys.claude);
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
    } catch (error) {
      console.error('Failed to set up provider:', error);
    }
  };

  const getConnectionStatus = () => {
    if (isConnecting) return '🟡';
    if (isConnected) return '🟢';
    if (error) return '🔴';
    return '⚫';
  };

  const getCapabilityIcon = (capability: string) => {
    if (!providerCapabilities) return '❓';
    
    switch (capability) {
      case 'voiceConversation':
        return providerCapabilities.voiceConversation ? '🎤' : '❌';
      case 'textChat':
        return providerCapabilities.textChat ? '💬' : '❌';
      case 'textToSpeech':
        return providerCapabilities.textToSpeech ? '🔊' : '❌';
      case 'speechToText':
        return providerCapabilities.speechToText ? '🎙️' : '❌';
      case 'streaming':
        return providerCapabilities.streaming ? '⚡' : '❌';
      case 'tools':
        return providerCapabilities.tools ? '🛠️' : '❌';
      default:
        return '❓';
    }
  };

  if (compact && !isExpanded) {
    return (
      <div className={`inline-flex items-center gap-2 ${className}`}>
        <button
          onClick={() => setIsExpanded(true)}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-white border rounded-lg hover:bg-gray-50"
        >
          <span>{getConnectionStatus()}</span>
          <span>{currentProvider?.config.name || 'No Provider'}</span>
          <span>⚙️</span>
        </button>
      </div>
    );
  }

  return (
    <div className={`bg-white border rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-700">AI Provider</h3>
        {compact && (
          <button
            onClick={() => setIsExpanded(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>

      {/* Current Provider Status */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span>{getConnectionStatus()}</span>
              <span className="font-medium">
                {currentProvider?.config.name || 'No Provider'}
              </span>
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {currentProvider?.config.type || 'Not connected'}
            </p>
          </div>
        </div>

        {showCapabilities && providerCapabilities && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs text-gray-600 mb-2">Capabilities:</p>
            <div className="flex flex-wrap gap-2">
              <span title="Voice Conversation">{getCapabilityIcon('voiceConversation')}</span>
              <span title="Text Chat">{getCapabilityIcon('textChat')}</span>
              <span title="Text-to-Speech">{getCapabilityIcon('textToSpeech')}</span>
              <span title="Speech-to-Text">{getCapabilityIcon('speechToText')}</span>
              <span title="Streaming">{getCapabilityIcon('streaming')}</span>
              <span title="Tools">{getCapabilityIcon('tools')}</span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* API Key Input Modal */}
      {showApiKeyInput && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 text-sm mb-3">
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
              className="flex-1 px-3 py-2 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleApiKeySubmit(showApiKeyInput)}
              disabled={!apiKeys[showApiKeyInput]}
              className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300"
            >
              Connect
            </button>
            <button
              onClick={() => setShowApiKeyInput(null)}
              className="px-3 py-2 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Available Providers */}
      <div className="space-y-2">
        <p className="text-sm text-gray-600 mb-3">Available Providers:</p>
        
        {availableProviders.map((provider) => (
          <div key={provider.type} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 flex items-center justify-center">
                {provider.type === 'elevenlabs' && '🎤'}
                {provider.type === 'openai' && '🤖'}
                {provider.type === 'claude' && '🧠'}
              </div>
              <div>
                <p className="text-sm font-medium">{provider.name}</p>
                <p className="text-xs text-gray-500 capitalize">{provider.type}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {!provider.available && (
                <span className="text-xs text-orange-600">API Key Required</span>
              )}
              
              <button
                onClick={() => handleProviderSwitch(provider.type)}
                disabled={
                  isConnecting || 
                  currentProvider?.config.type === provider.type
                }
                className={`px-3 py-1 text-xs rounded ${
                  currentProvider?.config.type === provider.type
                    ? 'bg-green-100 text-green-700'
                    : provider.available
                    ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {currentProvider?.config.type === provider.type ? 'Active' : 'Switch'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex gap-2">
          <button
            onClick={() => window.open('https://elevenlabs.io/app/conversational-ai', '_blank')}
            className="flex-1 px-3 py-2 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
          >
            Get ElevenLabs Agent
          </button>
          <button
            onClick={() => window.open('https://platform.openai.com/api-keys', '_blank')}
            className="flex-1 px-3 py-2 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
          >
            Get OpenAI Key
          </button>
        </div>
      </div>
    </div>
  );
}