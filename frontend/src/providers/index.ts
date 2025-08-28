/**
 * Provider System - Main Export
 * Modular AI/Voice provider architecture for easy swapping
 */

// Types and interfaces
export * from './types';

// Base provider
export { AbstractBaseProvider } from './BaseProvider';

// Provider implementations
export { ElevenLabsProvider } from './ElevenLabsProvider';
export { OpenAIProvider } from './OpenAIProvider';

// Factory and management
export { providerFactory, ProviderFactory } from './ProviderFactory';
export { providerManager, ProviderManager } from './ProviderManager';
export { providerConfigManager, ProviderConfigManager } from './ProviderConfig';

// Configuration types
export type { 
  AppProviderConfig, 
  ProviderEnvironmentConfig 
} from './ProviderConfig';

// Convenience exports for common patterns
export const createProvider = async (config: import('./types').ProviderConfig) => {
  return await providerFactory.createProvider(config);
};

export const useProviderManager = () => {
  return providerManager;
};

export const getProviderConfig = (type: string) => {
  return providerConfigManager.getProviderConfig(type);
};

// Quick setup functions
export const setupElevenLabs = async (agentId: string, apiUrl?: string) => {
  const config = providerFactory.createElevenLabsConfig('', agentId, apiUrl);
  await providerManager.switchProvider(config);
  return providerManager.getCurrentProvider();
};

export const setupOpenAI = async (apiKey: string, model?: string) => {
  const config = providerFactory.createOpenAIConfig(apiKey, model);
  await providerManager.switchProvider(config);
  return providerManager.getCurrentProvider();
};

export const setupClaude = async (apiKey: string, model?: string) => {
  const config = providerFactory.createClaudeConfig(apiKey, model);
  await providerManager.switchProvider(config);
  return providerManager.getCurrentProvider();
};

// Provider comparison utilities
export const compareProviderCapabilities = (type1: string, type2: string) => {
  return providerFactory.compareProviders(type1, type2);
};

export const findBestProvider = (requirements: {
  voiceRequired?: boolean;
  streamingRequired?: boolean;
  toolsRequired?: boolean;
}) => {
  return providerFactory.getRecommendedProvider(requirements);
};

// Version and info
export const PROVIDER_SYSTEM_VERSION = '1.0.0';

export const getSystemInfo = () => {
  return {
    version: PROVIDER_SYSTEM_VERSION,
    availableProviders: providerFactory.getSupportedProviders(),
    currentProvider: providerManager.getCurrentProviderInfo(),
    environment: providerConfigManager.getCurrentEnvironment(),
    features: {
      providerSwitching: providerConfigManager.isProviderSwitchingAllowed(),
      providerSelector: providerConfigManager.shouldShowProviderSelector(),
      voiceDefault: providerConfigManager.isVoiceEnabledByDefault()
    }
  };
};