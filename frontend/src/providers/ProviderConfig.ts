/**
 * Provider Configuration System
 * Centralized configuration for easy provider switching
 */

import { ProviderConfig } from './types';

export interface ProviderEnvironmentConfig {
  development: ProviderConfig;
  production: ProviderConfig;
  testing?: ProviderConfig;
}

export interface AppProviderConfig {
  defaultProvider: string;
  providers: {
    [key: string]: ProviderEnvironmentConfig | ProviderConfig;
  };
  features: {
    allowProviderSwitching: boolean;
    showProviderSelector: boolean;
    enableVoiceByDefault: boolean;
    fallbackProvider?: string;
  };
}

export class ProviderConfigManager {
  private static instance: ProviderConfigManager;
  private config: AppProviderConfig;
  private currentEnvironment: 'development' | 'production' | 'testing';

  private constructor() {
    this.currentEnvironment = this.detectEnvironment();
    this.config = this.loadDefaultConfig();
  }

  static getInstance(): ProviderConfigManager {
    if (!ProviderConfigManager.instance) {
      ProviderConfigManager.instance = new ProviderConfigManager();
    }
    return ProviderConfigManager.instance;
  }

  // Environment detection
  private detectEnvironment(): 'development' | 'production' | 'testing' {
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      
      if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.includes('dev')) {
        return 'development';
      }
      
      if (hostname.includes('test') || hostname.includes('staging')) {
        return 'testing';
      }
    }
    
    return import.meta.env.MODE === 'development' ? 'development' : 'production';
  }

  // Default configuration
  private loadDefaultConfig(): AppProviderConfig {
    return {
      defaultProvider: 'elevenlabs',
      providers: {
        elevenlabs: {
          development: {
            type: 'elevenlabs',
            name: 'ElevenLabs Voice AI (Dev)',
            agentId: import.meta.env.VITE_ELEVENLABS_AGENT_ID || 'agent_4901k2tkkq54f4mvgpndm3pgzm7g',
            apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
            capabilities: {
              voiceConversation: true,
              textChat: true,
              textToSpeech: true,
              speechToText: true,
              streaming: true,
              tools: true
            },
            settings: {
              audioFormat: 'pcm',
              sampleRate: 16000,
              channels: 1
            }
          },
          production: {
            type: 'elevenlabs',
            name: 'ElevenLabs Voice AI',
            agentId: import.meta.env.VITE_ELEVENLABS_AGENT_ID || 'agent_4901k2tkkq54f4mvgpndm3pgzm7g',
            apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
            capabilities: {
              voiceConversation: true,
              textChat: true,
              textToSpeech: true,
              speechToText: true,
              streaming: true,
              tools: true
            },
            settings: {
              audioFormat: 'pcm',
              sampleRate: 16000,
              channels: 1
            }
          }
        },
        openai: {
          development: {
            type: 'openai',
            name: 'OpenAI GPT (Dev)',
            apiKey: import.meta.env.VITE_OPENAI_API_KEY || '',
            model: 'gpt-4',
            voice: 'alloy',
            apiUrl: 'https://api.openai.com/v1',
            capabilities: {
              voiceConversation: true,
              textChat: true,
              textToSpeech: true,
              speechToText: true,
              streaming: true,
              tools: true
            },
            settings: {
              temperature: 0.7,
              maxTokens: 1000
            }
          },
          production: {
            type: 'openai',
            name: 'OpenAI GPT',
            apiKey: import.meta.env.VITE_OPENAI_API_KEY || '',
            model: 'gpt-4',
            voice: 'alloy',
            apiUrl: 'https://api.openai.com/v1',
            capabilities: {
              voiceConversation: true,
              textChat: true,
              textToSpeech: true,
              speechToText: true,
              streaming: true,
              tools: true
            },
            settings: {
              temperature: 0.5,
              maxTokens: 1000
            }
          }
        },
        claude: {
          development: {
            type: 'claude',
            name: 'Anthropic Claude (Dev)',
            apiKey: import.meta.env.VITE_ANTHROPIC_API_KEY || '',
            model: 'claude-3-sonnet',
            apiUrl: 'https://api.anthropic.com',
            capabilities: {
              voiceConversation: false,
              textChat: true,
              textToSpeech: false,
              speechToText: false,
              streaming: true,
              tools: true
            },
            settings: {
              temperature: 0.7,
              maxTokens: 4000
            }
          },
          production: {
            type: 'claude',
            name: 'Anthropic Claude',
            apiKey: import.meta.env.VITE_ANTHROPIC_API_KEY || '',
            model: 'claude-3-sonnet',
            apiUrl: 'https://api.anthropic.com',
            capabilities: {
              voiceConversation: false,
              textChat: true,
              textToSpeech: false,
              speechToText: false,
              streaming: true,
              tools: true
            },
            settings: {
              temperature: 0.5,
              maxTokens: 4000
            }
          }
        }
      },
      features: {
        allowProviderSwitching: true,
        showProviderSelector: this.currentEnvironment === 'development',
        enableVoiceByDefault: true,
        fallbackProvider: 'claude'
      }
    };
  }

  // Configuration getters
  getConfig(): AppProviderConfig {
    return this.config;
  }

  getProviderConfig(providerType: string): ProviderConfig | null {
    const providerData = this.config.providers[providerType];
    if (!providerData) {
      return null;
    }

    // If it's an environment-based config
    if (this.isEnvironmentConfig(providerData)) {
      return providerData[this.currentEnvironment] || providerData.development;
    }

    // If it's a direct config
    return providerData as ProviderConfig;
  }

  getDefaultProviderConfig(): ProviderConfig | null {
    return this.getProviderConfig(this.config.defaultProvider);
  }

  getAllProviderConfigs(): { [key: string]: ProviderConfig } {
    const configs: { [key: string]: ProviderConfig } = {};
    
    for (const [providerType, providerData] of Object.entries(this.config.providers)) {
      const config = this.getProviderConfig(providerType);
      if (config) {
        configs[providerType] = config;
      }
    }
    
    return configs;
  }

  getAvailableProviders(): Array<{ type: string; name: string; available: boolean }> {
    return Object.keys(this.config.providers).map(type => {
      const config = this.getProviderConfig(type);
      const available = this.isProviderAvailable(config);
      
      return {
        type,
        name: config?.name || type,
        available
      };
    });
  }

  // Configuration updates
  updateConfig(updates: Partial<AppProviderConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  updateProviderConfig(providerType: string, config: ProviderConfig): void {
    this.config.providers[providerType] = config;
  }

  setDefaultProvider(providerType: string): void {
    if (this.config.providers[providerType]) {
      this.config.defaultProvider = providerType;
    } else {
      throw new Error(`Provider type '${providerType}' is not configured`);
    }
  }

  // Feature flags
  isProviderSwitchingAllowed(): boolean {
    return this.config.features.allowProviderSwitching;
  }

  shouldShowProviderSelector(): boolean {
    return this.config.features.showProviderSelector;
  }

  isVoiceEnabledByDefault(): boolean {
    return this.config.features.enableVoiceByDefault;
  }

  getFallbackProvider(): string | undefined {
    return this.config.features.fallbackProvider;
  }

  // Provider availability
  isProviderAvailable(config: ProviderConfig | null): boolean {
    if (!config) {
      return false;
    }

    switch (config.type) {
      case 'elevenlabs':
        return !!config.agentId;
      
      case 'openai':
      case 'claude':
        return !!config.apiKey;
      
      default:
        return true;
    }
  }

  getFirstAvailableProvider(): ProviderConfig | null {
    const availableProviders = this.getAvailableProviders().filter(p => p.available);
    
    if (availableProviders.length === 0) {
      return null;
    }

    const firstAvailable = availableProviders[0];
    return this.getProviderConfig(firstAvailable.type);
  }

  // Environment management
  getCurrentEnvironment(): string {
    return this.currentEnvironment;
  }

  setEnvironment(env: 'development' | 'production' | 'testing'): void {
    this.currentEnvironment = env;
  }

  // Configuration presets
  static createDevelopmentConfig(): AppProviderConfig {
    const manager = new ProviderConfigManager();
    const config = manager.getConfig();
    
    return {
      ...config,
      features: {
        ...config.features,
        allowProviderSwitching: true,
        showProviderSelector: true,
        enableVoiceByDefault: false // More conservative for dev
      }
    };
  }

  static createProductionConfig(): AppProviderConfig {
    const manager = new ProviderConfigManager();
    const config = manager.getConfig();
    
    return {
      ...config,
      features: {
        ...config.features,
        allowProviderSwitching: false,
        showProviderSelector: false,
        enableVoiceByDefault: true
      }
    };
  }

  // Utility methods
  private isEnvironmentConfig(providerData: any): providerData is ProviderEnvironmentConfig {
    return providerData.development !== undefined || providerData.production !== undefined;
  }

  // Configuration validation
  validateConfiguration(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!this.config.defaultProvider) {
      errors.push('Default provider is not set');
    } else if (!this.config.providers[this.config.defaultProvider]) {
      errors.push(`Default provider '${this.config.defaultProvider}' is not configured`);
    }

    const defaultConfig = this.getDefaultProviderConfig();
    if (!defaultConfig) {
      errors.push('Default provider configuration is invalid');
    } else if (!this.isProviderAvailable(defaultConfig)) {
      errors.push('Default provider is not available (missing credentials)');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  // Export/Import configuration
  exportConfiguration(): string {
    return JSON.stringify(this.config, null, 2);
  }

  importConfiguration(configJson: string): void {
    try {
      const newConfig = JSON.parse(configJson);
      this.config = { ...this.loadDefaultConfig(), ...newConfig };
    } catch (error) {
      throw new Error('Invalid configuration JSON');
    }
  }
}

// Export singleton instance
export const providerConfigManager = ProviderConfigManager.getInstance();