/**
 * Base Provider Abstract Class
 * Common functionality shared by all providers
 */

import { 
  BaseProvider, 
  ProviderConfig, 
  ProviderCapabilities, 
  ConnectionState, 
  ProviderEvent 
} from './types';

export abstract class AbstractBaseProvider implements BaseProvider {
  protected _config: ProviderConfig;
  protected _capabilities: ProviderCapabilities;
  protected _connectionState: ConnectionState = 'disconnected';
  protected _eventHandlers: Map<string, Function[]> = new Map();
  protected _isInitialized: boolean = false;

  constructor(config: ProviderConfig) {
    this._config = config;
    this._capabilities = config.capabilities;
  }

  get config(): ProviderConfig {
    return this._config;
  }

  get capabilities(): ProviderCapabilities {
    return this._capabilities;
  }

  get connectionState(): ConnectionState {
    return this._connectionState;
  }

  get isInitialized(): boolean {
    return this._isInitialized;
  }

  // Abstract methods that must be implemented by subclasses
  abstract initialize(config: ProviderConfig): Promise<void>;
  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;

  // Event handling system
  on(event: string, handler: Function): void {
    if (!this._eventHandlers.has(event)) {
      this._eventHandlers.set(event, []);
    }
    this._eventHandlers.get(event)!.push(handler);
  }

  off(event: string, handler: Function): void {
    const handlers = this._eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  emit(event: string, data: any): void {
    const handlers = this._eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error);
        }
      });
    }
  }

  // Lifecycle management
  async destroy(): Promise<void> {
    await this.disconnect();
    this._eventHandlers.clear();
    this._isInitialized = false;
  }

  // Connection state management
  protected updateConnectionState(state: ConnectionState): void {
    if (this._connectionState !== state) {
      this._connectionState = state;
      this.emit('connection', { 
        state, 
        timestamp: new Date().toISOString() 
      });
    }
  }

  // Error handling
  protected handleError(error: string | Error): void {
    const errorMessage = error instanceof Error ? error.message : error;
    console.error(`Provider Error (${this._config.type}):`, errorMessage);
    this.updateConnectionState('error');
    this.emit('error', { 
      error: errorMessage, 
      timestamp: new Date().toISOString() 
    });
  }

  // Configuration validation
  protected validateConfig(config: ProviderConfig): void {
    if (!config.type) {
      throw new Error('Provider type is required');
    }
    if (!config.name) {
      throw new Error('Provider name is required');
    }
    if (!config.capabilities) {
      throw new Error('Provider capabilities are required');
    }
  }

  // Utility methods
  protected generateId(): string {
    return `${this._config.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  protected createMessage(role: 'user' | 'assistant' | 'system', content: string, metadata?: Record<string, any>) {
    return {
      id: this.generateId(),
      role,
      content,
      timestamp: new Date().toISOString(),
      metadata
    };
  }

  // Configuration updates
  async updateConfig(updates: Partial<ProviderConfig>): Promise<void> {
    const newConfig = { ...this._config, ...updates };
    this.validateConfig(newConfig);
    
    const wasConnected = this._connectionState === 'connected';
    
    if (wasConnected) {
      await this.disconnect();
    }
    
    this._config = newConfig;
    this._capabilities = newConfig.capabilities;
    
    if (wasConnected) {
      await this.connect();
    }
    
    this.emit('configUpdated', { config: newConfig });
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      return this._connectionState === 'connected' && this._isInitialized;
    } catch (error) {
      return false;
    }
  }

  // Provider info
  getProviderInfo() {
    return {
      type: this._config.type,
      name: this._config.name,
      capabilities: this._capabilities,
      connectionState: this._connectionState,
      isInitialized: this._isInitialized,
      config: {
        ...this._config,
        apiKey: this._config.apiKey ? '***' : undefined // Hide sensitive data
      }
    };
  }
}