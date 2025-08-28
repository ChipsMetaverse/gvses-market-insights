/**
 * Provider Manager
 * Manages active providers and handles switching between them
 */

import { 
  BaseProvider, 
  ProviderConfig, 
  ProviderManager as IProviderManager,
  VoiceProvider,
  ChatProvider,
  Message,
  AudioChunk,
  ConnectionState,
  ProviderEventHandlers
} from './types';
import { providerFactory } from './ProviderFactory';

export class ProviderManager implements IProviderManager {
  private static instance: ProviderManager;
  private currentProvider: BaseProvider | null = null;
  private eventHandlers: ProviderEventHandlers = {};
  private availableProviders: ProviderConfig[] = [];
  private isInitialized: boolean = false;

  private constructor() {
    this.loadAvailableProviders();
  }

  static getInstance(): ProviderManager {
    if (!ProviderManager.instance) {
      ProviderManager.instance = new ProviderManager();
    }
    return ProviderManager.instance;
  }

  async initialize(defaultConfig?: ProviderConfig): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      if (defaultConfig) {
        await this.switchProvider(defaultConfig);
      }
      this.isInitialized = true;
    } catch (error) {
      console.error('Failed to initialize provider manager:', error);
      throw error;
    }
  }

  getCurrentProvider(): BaseProvider | null {
    return this.currentProvider;
  }

  getCurrentProviderAs<T extends BaseProvider>(): T | null {
    return this.currentProvider as T | null;
  }

  async switchProvider(config: ProviderConfig): Promise<void> {
    // Validate configuration
    const validation = providerFactory.validateConfig(config);
    if (!validation.valid) {
      throw new Error(`Invalid provider config: ${validation.errors.join(', ')}`);
    }

    // Disconnect current provider
    if (this.currentProvider) {
      await this.disconnectCurrentProvider();
    }

    try {
      // Create new provider
      const newProvider = await providerFactory.createProvider(config);
      
      // Set up event handlers
      this.setupProviderEvents(newProvider);
      
      // Connect new provider
      await newProvider.connect();
      
      this.currentProvider = newProvider;
      
      console.log(`Switched to provider: ${config.type} (${config.name})`);
      
      // Emit provider switch event
      this.emitEvent('providerSwitched', {
        previous: this.currentProvider?.config || null,
        current: config,
        timestamp: new Date().toISOString()
      });
      
    } catch (error) {
      console.error(`Failed to switch to provider ${config.type}:`, error);
      throw error;
    }
  }

  getAvailableProviders(): ProviderConfig[] {
    return [...this.availableProviders];
  }

  registerProvider(provider: ProviderConfig): void {
    const existingIndex = this.availableProviders.findIndex(p => p.type === provider.type);
    if (existingIndex >= 0) {
      this.availableProviders[existingIndex] = provider;
    } else {
      this.availableProviders.push(provider);
    }
  }

  // Event handling
  setEventHandlers(handlers: ProviderEventHandlers): void {
    this.eventHandlers = handlers;
  }

  updateEventHandlers(handlers: Partial<ProviderEventHandlers>): void {
    this.eventHandlers = { ...this.eventHandlers, ...handlers };
  }

  // High-level provider operations
  async sendMessage(message: string, context?: string[]): Promise<Message | void> {
    if (!this.currentProvider) {
      throw new Error('No active provider');
    }

    const chatProvider = this.currentProvider as ChatProvider;
    if (chatProvider.sendMessage && this.hasCapability('textChat')) {
      return await chatProvider.sendMessage(message, context);
    }

    // Fallback for voice providers
    const voiceProvider = this.currentProvider as VoiceProvider;
    if (voiceProvider.sendMessage && this.hasCapability('voiceConversation')) {
      await voiceProvider.sendMessage(message);
      return;
    }

    throw new Error('Current provider does not support messaging');
  }

  async *streamMessage(message: string, context?: string[]): AsyncGenerator<string> {
    if (!this.currentProvider) {
      throw new Error('No active provider');
    }

    const chatProvider = this.currentProvider as ChatProvider;
    if (chatProvider.streamMessage && this.hasCapability('streaming')) {
      yield* chatProvider.streamMessage(message, context);
      return;
    }

    throw new Error('Current provider does not support streaming');
  }

  async startVoiceConversation(): Promise<void> {
    if (!this.currentProvider) {
      throw new Error('No active provider');
    }

    if (!this.hasCapability('voiceConversation')) {
      throw new Error('Current provider does not support voice conversation');
    }

    const voiceProvider = this.currentProvider as VoiceProvider;
    await voiceProvider.startConversation();
  }

  async stopVoiceConversation(): Promise<void> {
    if (!this.currentProvider) {
      return;
    }

    if (!this.hasCapability('voiceConversation')) {
      return;
    }

    const voiceProvider = this.currentProvider as VoiceProvider;
    await voiceProvider.stopConversation();
  }

  async sendAudio(audioChunk: AudioChunk): Promise<void> {
    if (!this.currentProvider) {
      throw new Error('No active provider');
    }

    if (!this.hasCapability('speechToText')) {
      throw new Error('Current provider does not support speech-to-text');
    }

    const voiceProvider = this.currentProvider as VoiceProvider;
    await voiceProvider.sendAudio(audioChunk);
  }

  // Provider capability checks
  hasCapability(capability: keyof typeof this.currentProvider.capabilities): boolean {
    if (!this.currentProvider) {
      return false;
    }
    return this.currentProvider.capabilities[capability] || false;
  }

  getProviderCapabilities() {
    return this.currentProvider?.capabilities || null;
  }

  // Connection management
  async connect(): Promise<void> {
    if (this.currentProvider) {
      await this.currentProvider.connect();
    }
  }

  async disconnect(): Promise<void> {
    if (this.currentProvider) {
      await this.currentProvider.disconnect();
    }
  }

  getConnectionState(): ConnectionState | null {
    return this.currentProvider?.connectionState || null;
  }

  // Provider information
  getCurrentProviderInfo() {
    if (!this.currentProvider) {
      return null;
    }

    if (typeof this.currentProvider.getProviderInfo === 'function') {
      return this.currentProvider.getProviderInfo();
    }

    return {
      type: this.currentProvider.config.type,
      name: this.currentProvider.config.name,
      capabilities: this.currentProvider.capabilities,
      connectionState: this.currentProvider.connectionState
    };
  }

  // Provider switching helpers
  async switchToElevenLabs(agentId: string, apiUrl?: string): Promise<void> {
    const config = providerFactory.createElevenLabsConfig('', agentId, apiUrl);
    await this.switchProvider(config);
  }

  async switchToOpenAI(apiKey: string, model?: string): Promise<void> {
    const config = providerFactory.createOpenAIConfig(apiKey, model);
    await this.switchProvider(config);
  }

  async switchToClaude(apiKey: string, model?: string): Promise<void> {
    const config = providerFactory.createClaudeConfig(apiKey, model);
    await this.switchProvider(config);
  }

  // Provider recommendations
  getRecommendedProvider(requirements: {
    voiceRequired?: boolean;
    streamingRequired?: boolean;
    toolsRequired?: boolean;
  }): ProviderConfig[] {
    return providerFactory.getRecommendedProvider(requirements);
  }

  // Cleanup
  async destroy(): Promise<void> {
    await this.disconnectCurrentProvider();
    this.eventHandlers = {};
    this.availableProviders = [];
    this.isInitialized = false;
  }

  // Private methods
  private async disconnectCurrentProvider(): Promise<void> {
    if (this.currentProvider) {
      try {
        await this.currentProvider.destroy();
      } catch (error) {
        console.error('Error disconnecting provider:', error);
      }
      this.currentProvider = null;
    }
  }

  private setupProviderEvents(provider: BaseProvider): void {
    // Forward provider events to manager event handlers
    provider.on('message', (message: Message) => {
      this.emitEvent('message', message);
    });

    provider.on('audio', (audio: AudioChunk) => {
      this.emitEvent('audio', audio);
    });

    provider.on('transcript', (transcript: string) => {
      this.emitEvent('transcript', transcript);
    });

    provider.on('connection', (data: { state: ConnectionState }) => {
      this.emitEvent('connectionChange', data.state);
    });

    provider.on('error', (data: { error: string }) => {
      this.emitEvent('error', data.error);
    });
  }

  private emitEvent(eventType: string, data: any): void {
    switch (eventType) {
      case 'message':
        this.eventHandlers.onMessage?.(data);
        break;
      case 'audio':
        this.eventHandlers.onAudio?.(data);
        break;
      case 'transcript':
        this.eventHandlers.onTranscript?.(data);
        break;
      case 'connectionChange':
        this.eventHandlers.onConnectionChange?.(data);
        break;
      case 'error':
        this.eventHandlers.onError?.(data);
        break;
    }
  }

  private loadAvailableProviders(): void {
    this.availableProviders = providerFactory.getSupportedProviders();
  }
}

// Export singleton instance
export const providerManager = ProviderManager.getInstance();