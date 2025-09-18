/**
 * Clean Provider Selector Component
 * Simple, functional UI for switching between AI/Voice providers
 */

import React, { useState } from 'react';
import { useProvider } from '../hooks/useProvider';

interface ProviderSelectorCleanProps {
  className?: string;
  compact?: boolean;
}

export function ProviderSelectorClean({ 
  className = '', 
  compact = false 
}: ProviderSelectorCleanProps) {
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

  const [showPanel, setShowPanel] = useState(!compact);
  const [apiKey, setApiKey] = useState('');
  const [showApiKeyFor, setShowApiKeyFor] = useState<string | null>(null);

  if (!allowProviderSwitching) {
    return null;
  }

  const handleProviderSwitch = async (type: string) => {
    try {
      switch (type) {
        case 'elevenlabs':
          await switchToElevenLabs('agent_4901k2tkkq54f4mvgpndm3pgzm7g');
          break;
        case 'openai':
          if (!apiKey) {
            setShowApiKeyFor('openai');
            return;
          }
          await switchToOpenAI(apiKey);
          setApiKey('');
          setShowApiKeyFor(null);
          break;
        case 'openai-realtime':
          await switchToOpenAIRealtime();
          break;
        case 'claude':
          if (!apiKey) {
            setShowApiKeyFor('claude');
            return;
          }
          await switchToClaude(apiKey);
          setApiKey('');
          setShowApiKeyFor(null);
          break;
      }
      if (compact) setShowPanel(false);
    } catch (err) {
      console.error('Provider switch failed:', err);
    }
  };

  const getStatusColor = () => {
    if (isConnecting) return '#FFA500'; // Orange
    if (isConnected) return '#22C55E';  // Green
    if (error) return '#EF4444';        // Red
    return '#9CA3AF';                   // Gray
  };

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...';
    if (isConnected) return 'Connected';
    if (error) return 'Error';
    return 'Disconnected';
  };

  const providers = [
    { type: 'elevenlabs', name: 'ElevenLabs', icon: '🎤' },
    { type: 'openai', name: 'OpenAI GPT', icon: '💬' },
    { type: 'openai-realtime', name: 'OpenAI Voice', icon: '🎙️' },
    { type: 'claude', name: 'Claude', icon: '🤖' }
  ];

  // Compact mode - just show a button
  if (compact && !showPanel) {
    return (
      <button
        onClick={() => setShowPanel(true)}
        className={className}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          backgroundColor: 'white',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          fontSize: '14px',
          cursor: 'pointer',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#F9FAFB';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'white';
        }}
      >
        <div 
          style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            backgroundColor: getStatusColor() 
          }} 
        />
        <span style={{ fontWeight: '500' }}>
          {currentProvider?.config.name || 'Select Provider'}
        </span>
        <span style={{ color: '#6B7280' }}>▼</span>
      </button>
    );
  }

  // Main panel
  return (
    <div 
      className={className}
      style={{
        backgroundColor: 'white',
        border: '1px solid #E5E7EB',
        borderRadius: '12px',
        padding: '16px',
        width: '320px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}
    >
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '16px'
      }}>
        <h3 style={{ 
          margin: 0, 
          fontSize: '16px', 
          fontWeight: '600',
          color: '#111827'
        }}>
          AI Provider
        </h3>
        {compact && (
          <button
            onClick={() => setShowPanel(false)}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '18px',
              cursor: 'pointer',
              padding: '4px',
              color: '#6B7280'
            }}
          >
            ×
          </button>
        )}
      </div>

      {/* Current Status */}
      <div style={{
        backgroundColor: '#F9FAFB',
        borderRadius: '8px',
        padding: '12px',
        marginBottom: '16px'
      }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: '500', color: '#111827' }}>
              {currentProvider?.config.name || 'No Provider'}
            </div>
            <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
              {currentProvider?.config.type || 'Not connected'}
            </div>
          </div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 8px',
            backgroundColor: getStatusColor() + '20',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: '500',
            color: getStatusColor()
          }}>
            <div style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: getStatusColor()
            }} />
            {getStatusText()}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          backgroundColor: '#FEE2E2',
          border: '1px solid #FECACA',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '16px',
          fontSize: '13px',
          color: '#991B1B'
        }}>
          {error}
        </div>
      )}

      {/* API Key Input */}
      {showApiKeyFor && (
        <div style={{
          backgroundColor: '#EFF6FF',
          border: '1px solid #BFDBFE',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '16px'
        }}>
          <div style={{ fontSize: '13px', color: '#1E40AF', marginBottom: '8px' }}>
            Enter {showApiKeyFor.toUpperCase()} API Key:
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
              style={{
                flex: 1,
                padding: '6px 10px',
                border: '1px solid #93C5FD',
                borderRadius: '6px',
                fontSize: '13px',
                outline: 'none'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#3B82F6';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#93C5FD';
              }}
            />
            <button
              onClick={() => handleProviderSwitch(showApiKeyFor)}
              style={{
                padding: '6px 12px',
                backgroundColor: '#3B82F6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Connect
            </button>
            <button
              onClick={() => {
                setShowApiKeyFor(null);
                setApiKey('');
              }}
              style={{
                padding: '6px 12px',
                backgroundColor: '#E5E7EB',
                color: '#4B5563',
                border: 'none',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Provider List */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ 
          fontSize: '12px', 
          fontWeight: '600', 
          color: '#6B7280',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          marginBottom: '10px'
        }}>
          Available Providers
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {providers.map(provider => {
            const isActive = currentProvider?.config.type === provider.type;
            const needsKey = (provider.type === 'openai' || provider.type === 'claude') && !isActive;
            
            return (
              <div
                key={provider.type}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px',
                  backgroundColor: isActive ? '#F0F9FF' : 'white',
                  border: `1px solid ${isActive ? '#93C5FD' : '#E5E7EB'}`,
                  borderRadius: '8px',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '18px' }}>{provider.icon}</span>
                  <div>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: '500',
                      color: isActive ? '#1E40AF' : '#111827'
                    }}>
                      {provider.name}
                    </div>
                    {needsKey && (
                      <div style={{ fontSize: '11px', color: '#EA580C' }}>
                        API Key Required
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => !isActive && handleProviderSwitch(provider.type)}
                  disabled={isActive || isConnecting}
                  style={{
                    padding: '4px 12px',
                    backgroundColor: isActive ? '#86EFAC' : '#3B82F6',
                    color: isActive ? '#14532D' : 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: '500',
                    cursor: isActive || isConnecting ? 'default' : 'pointer',
                    opacity: isConnecting ? 0.5 : 1
                  }}
                >
                  {isActive ? 'Active' : 'Switch'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Links */}
      <div style={{
        display: 'flex',
        gap: '8px',
        paddingTop: '12px',
        borderTop: '1px solid #E5E7EB'
      }}>
        <a
          href="https://elevenlabs.io/app/conversational-ai"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            flex: 1,
            padding: '6px',
            backgroundColor: '#F3E8FF',
            color: '#6B21A8',
            textAlign: 'center',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '500',
            textDecoration: 'none'
          }}
        >
          Get ElevenLabs
        </a>
        <a
          href="https://platform.openai.com/api-keys"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            flex: 1,
            padding: '6px',
            backgroundColor: '#DCFCE7',
            color: '#14532D',
            textAlign: 'center',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '500',
            textDecoration: 'none'
          }}
        >
          Get OpenAI Key
        </a>
      </div>
    </div>
  );
}