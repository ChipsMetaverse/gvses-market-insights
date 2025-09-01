/**
 * Provider Factory
 * Creates and manages different AI/Voice providers
 */

import { 
  BaseProvider, 
  ProviderConfig, 
  ProviderFactory as IProviderFactory,
  ProviderCapabilities
} from './types';
import { ElevenLabsProvider } from './ElevenLabsProvider';
import { OpenAIProvider } from './OpenAIProvider';
import { OpenAIRealtimeProvider } from './OpenAIRealtimeProvider';

// Provider registry type
type ProviderConstructor = new (config: ProviderConfig) => BaseProvider;

export class ProviderFactory implements IProviderFactory {
  private static instance: ProviderFactory;
  private providerRegistry = new Map<string, ProviderConstructor>();
  private providerConfigs = new Map<string, ProviderConfig>();

  private constructor() {
    this.registerDefaultProviders();
  }

  static getInstance(): ProviderFactory {
    if (!ProviderFactory.instance) {
      ProviderFactory.instance = new ProviderFactory();
    }
    return ProviderFactory.instance;
  }

  private registerDefaultProviders(): void {
    // Register built-in providers
    this.registerProvider('elevenlabs', ElevenLabsProvider);
    this.registerProvider('openai', OpenAIProvider);
    this.registerProvider('openai-realtime', OpenAIRealtimeProvider);

    // Register default configurations
    this.registerProviderConfig({
      type: 'elevenlabs',
      name: 'ElevenLabs Voice AI',
      capabilities: ElevenLabsProvider.getDefaultCapabilities(),
      settings: {
        audioFormat: 'pcm',
        sampleRate: 16000,
        channels: 1
      }
    });

    this.registerProviderConfig({
      type: 'openai',
      name: 'OpenAI GPT',
      capabilities: OpenAIProvider.getDefaultCapabilities(),
      settings: {
        temperature: 0.7,
        maxTokens: 1000
      }
    });

    this.registerProviderConfig({
      type: 'openai-realtime',
      name: 'OpenAI Realtime Voice',
      capabilities: OpenAIRealtimeProvider.getDefaultCapabilities(),
      settings: {
        audioFormat: 'pcm',
        sampleRate: 24000,
        channels: 1,
        voice: 'alloy'
      }
    });
  }

  registerProvider(type: string, providerClass: ProviderConstructor): void {
    this.providerRegistry.set(type, providerClass);
  }

  registerProviderConfig(config: ProviderConfig): void {
    this.providerConfigs.set(config.type, config);
  }

  async createProvider<T extends BaseProvider>(config: ProviderConfig): Promise<T> {
    const ProviderClass = this.providerRegistry.get(config.type);
    
    if (!ProviderClass) {
      throw new Error(`Provider type '${config.type}' is not registered`);
    }

    // Merge with default config if available
    const defaultConfig = this.providerConfigs.get(config.type);
    const mergedConfig = defaultConfig ? this.mergeConfigs(defaultConfig, config) : config;

    try {
      const provider = new ProviderClass(mergedConfig) as T;
      await provider.initialize(mergedConfig);
      return provider;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create provider';
      throw new Error(`Failed to create ${config.type} provider: ${errorMessage}`);
    }
  }

  getSupportedProviders(): ProviderConfig[] {
    return Array.from(this.providerConfigs.values());
  }

  isProviderSupported(type: string): boolean {
    return this.providerRegistry.has(type);
  }

  getProviderCapabilities(type: string): ProviderCapabilities | null {
    const config = this.providerConfigs.get(type);
    return config?.capabilities || null;
  }

  // Configuration helpers
  createElevenLabsConfig(apiKey: string, agentId: string, apiUrl?: string): ProviderConfig {
    return {
      type: 'elevenlabs',
      name: 'ElevenLabs Voice AI',
      apiKey,
      agentId,
      apiUrl: apiUrl || window.location.origin,
      capabilities: ElevenLabsProvider.getDefaultCapabilities(),
      settings: {
        audioFormat: 'pcm',
        sampleRate: 16000,
        channels: 1
      }
    };
  }

  createOpenAIConfig(apiKey: string, model?: string, voice?: string): ProviderConfig {
    return {
      type: 'openai',
      name: 'OpenAI GPT',
      apiKey,
      model: model || 'gpt-4',
      voice: voice || 'alloy',
      capabilities: OpenAIProvider.getDefaultCapabilities(),
      settings: {
        temperature: 0.7,
        maxTokens: 1000,
        streaming: true
      }
    };
  }

  createOpenAIRealtimeConfig(apiUrl?: string, model?: string, voice?: string): ProviderConfig {
    return {
      type: 'openai-realtime',
      name: 'OpenAI Realtime Voice',
      apiUrl: apiUrl || window.location.origin,
      model: model || 'gpt-4o-realtime-preview',
      voice: voice || 'alloy',
      capabilities: OpenAIRealtimeProvider.getDefaultCapabilities(),
      settings: {
        audioFormat: 'pcm',
        sampleRate: 24000,
        channels: 1,
        turnDetection: 'server_vad'
      }
    };
  }

  createClaudeConfig(apiKey: string, model?: string): ProviderConfig {
    return {
      type: 'claude',
      name: 'Anthropic Claude',
      apiKey,
      model: model || 'claude-3-sonnet',
      capabilities: {
        voiceConversation: false, // Claude doesn't support native voice
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
    };
  }

  // Configuration validation
  validateConfig(config: ProviderConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.type) {
      errors.push('Provider type is required');
    } else if (!this.isProviderSupported(config.type)) {
      errors.push(`Provider type '${config.type}' is not supported`);
    }

    if (!config.name) {
      errors.push('Provider name is required');
    }

    if (!config.capabilities) {
      errors.push('Provider capabilities are required');
    }

    // Type-specific validations
    switch (config.type) {
      case 'elevenlabs':
        if (!config.agentId) {
          errors.push('ElevenLabs agent ID is required');
        }
        break;
      
      case 'openai':
        if (!config.apiKey) {
          errors.push('OpenAI API key is required');
        }
        break;
      
      case 'openai-realtime':
        // OpenAI Realtime uses backend proxy, so no API key needed in frontend
        if (!config.apiUrl) {
          errors.push('OpenAI Realtime API URL is required');
        }
        break;
      
      case 'claude':
        if (!config.apiKey) {
          errors.push('Claude API key is required');
        }
        break;
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  // Utility methods
  private mergeConfigs(defaultConfig: ProviderConfig, userConfig: ProviderConfig): ProviderConfig {
    return {
      ...defaultConfig,
      ...userConfig,
      capabilities: {
        ...defaultConfig.capabilities,
        ...userConfig.capabilities
      },
      settings: {
        ...defaultConfig.settings,
        ...userConfig.settings
      }
    };
  }

  // Provider discovery and recommendations
  getRecommendedProvider(requirements: {
    voiceRequired?: boolean;
    streamingRequired?: boolean;
    toolsRequired?: boolean;
  }): ProviderConfig[] {
    const allProviders = this.getSupportedProviders();
    
    return allProviders.filter(config => {
      const caps = config.capabilities;
      
      if (requirements.voiceRequired && !caps.voiceConversation) {
        return false;
      }
      
      if (requirements.streamingRequired && !caps.streaming) {
        return false;
      }
      
      if (requirements.toolsRequired && !caps.tools) {
        return false;
      }
      
      return true;
    });
  }

  // Provider comparison
  compareProviders(type1: string, type2: string): {
    provider1: ProviderConfig | null;
    provider2: ProviderConfig | null;
    comparison: {
      voiceConversation: [boolean, boolean];
      textChat: [boolean, boolean];
      textToSpeech: [boolean, boolean];
      speechToText: [boolean, boolean];
      streaming: [boolean, boolean];
      tools: [boolean, boolean];
    };
  } {
    const provider1 = this.providerConfigs.get(type1) || null;
    const provider2 = this.providerConfigs.get(type2) || null;

    const comparison = {
      voiceConversation: [
        provider1?.capabilities.voiceConversation || false,
        provider2?.capabilities.voiceConversation || false
      ] as [boolean, boolean],
      textChat: [
        provider1?.capabilities.textChat || false,
        provider2?.capabilities.textChat || false
      ] as [boolean, boolean],
      textToSpeech: [
        provider1?.capabilities.textToSpeech || false,
        provider2?.capabilities.textToSpeech || false
      ] as [boolean, boolean],
      speechToText: [
        provider1?.capabilities.speechToText || false,
        provider2?.capabilities.speechToText || false
      ] as [boolean, boolean],
      streaming: [
        provider1?.capabilities.streaming || false,
        provider2?.capabilities.streaming || false
      ] as [boolean, boolean],
      tools: [
        provider1?.capabilities.tools || false,
        provider2?.capabilities.tools || false
      ] as [boolean, boolean],
    };

    return {
      provider1,
      provider2,
      comparison
    };
  }
}

// Export singleton instance
export const providerFactory = ProviderFactory.getInstance();