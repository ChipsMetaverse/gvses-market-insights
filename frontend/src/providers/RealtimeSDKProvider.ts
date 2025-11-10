/**
 * Realtime SDK Provider Implementation
 * Phase 2: End-to-end voice evaluation using pure gpt-realtime + Agents SDK
 * Bypasses custom orchestrator for direct OpenAI Realtime with built-in tool calling
 */

import { AbstractBaseProvider } from './BaseProvider';
import {
  VoiceProvider,
  ProviderConfig,
  AudioChunk,
  ProviderCapabilities
} from './types';
import { agentOrchestratorService } from '../services/agentOrchestratorService';

export class RealtimeSDKProvider extends AbstractBaseProvider implements VoiceProvider {
  private websocket: WebSocket | null = null;
  private sessionId: string;
  private currentVoice: string;
  private conversationHistory: Array<{ role: string; content: string }> = [];
  private isRecording = false;

  constructor(config: ProviderConfig) {
    super(config);
    this.sessionId = this.generateSessionId();
    this.currentVoice = config.voice || 'alloy';
  }

  static getDefaultCapabilities(): ProviderCapabilities {
    return {
      voiceConversation: true,
      textChat: true,
      textToSpeech: true,
      speechToText: true,
      streaming: true,
      tools: true
    };
  }

  async initialize(config: ProviderConfig): Promise<void> {
    this.validateConfig(config);
    
    this._config = config;
    this._capabilities = config.capabilities || RealtimeSDKProvider.getDefaultCapabilities();
    
    this._isInitialized = true;
    this.emit('initialized', { provider: 'realtime-sdk' });
  }

  async connect(): Promise<void> {
    if (this._connectionState === 'connected' || this._connectionState === 'connecting') {
      return;
    }

    this.updateConnectionState('connecting');

    try {
      // Phase 2: Connect via backend relay to integrate with Agents SDK
      // Get ephemeral token from backend
      const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
      const workflowId = import.meta.env.VITE_WORKFLOW_ID || 'wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736';
      
      const tokenResponse = await fetch(`${apiUrl}/api/agent/realtime-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflowId,
          voice: this.currentVoice,
          session_id: this.sessionId
        })
      });

      if (!tokenResponse.ok) {
        throw new Error(`Failed to get realtime token: ${tokenResponse.statusText}`);
      }

      const { token, session_id } = await tokenResponse.json();
      this.sessionId = session_id;

      // Connect to backend WebSocket relay
      const wsUrl = apiUrl.replace('http', 'ws') + '/ws/realtime-sdk';
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('🔌 RealtimeSDK WebSocket connected to backend relay');
        
        // Send session.init to authenticate with backend
        this.sendMessage({
          type: 'session.init',
          token,
          session_id: this.sessionId,
          workflow_id: workflowId,
          voice: this.currentVoice
        });
      };

      this.websocket.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };

      this.websocket.onerror = (error) => {
        console.error('RealtimeSDK WebSocket error:', error);
        this.handleError('Connection error');
      };

      this.websocket.onclose = () => {
        console.log('🔌 RealtimeSDK WebSocket disconnected');
        this.updateConnectionState('disconnected');
        this.emit('disconnected', { provider: 'realtime-sdk' });
      };

    } catch (error) {
      this.handleError(error instanceof Error ? error.message : 'Failed to connect');
    }
  }

  private initializeSession(): void {
    if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
      return;
    }

    // Configure session with tools
    const sessionUpdate = {
      type: 'session.update',
      session: {
        modalities: ['text', 'audio'],
        instructions: `You are GVSES AI, a professional market analysis assistant. You have access to comprehensive market data tools through the Agents SDK. Provide concise, actionable market insights.

Key capabilities:
- Real-time stock quotes and analysis
- Chart pattern recognition
- Technical level identification (QE, ST, LTB, BTD, Retest)
- Market news and sentiment analysis
- Portfolio optimization recommendations

When users ask about stocks or market data:
1. Use the agents_sdk_orchestrate tool to get comprehensive analysis
2. Provide clear, concise responses with key levels
3. Include relevant market context and sentiment

Always be professional, accurate, and helpful.`,
        voice: this.currentVoice,
        input_audio_format: 'pcm16',
        output_audio_format: 'pcm16',
        input_audio_transcription: {
          model: 'whisper-1'
        },
        turn_detection: {
          type: 'server_vad',
          threshold: 0.5,
          prefix_padding_ms: 300,
          silence_duration_ms: 200
        },
        tools: [
          {
            type: 'function',
            name: 'agents_sdk_orchestrate',
            description: 'Get comprehensive market analysis and data using the Agents SDK',
            parameters: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'The market question or request'
                },
                conversation_history: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      role: { type: 'string' },
                      content: { type: 'string' }
                    }
                  },
                  description: 'Previous conversation context'
                }
              },
              required: ['query']
            }
          }
        ],
        tool_choice: 'auto'
      }
    };

    this.websocket.send(JSON.stringify(sessionUpdate));
  }

  private handleMessage(message: any): void {
    console.log('RealtimeSDK message:', message.type, message);

    switch (message.type) {
      case 'session.created':
        console.log('✅ RealtimeSDK session created via backend relay');
        this.updateConnectionState('connected');
        this.emit('connected', { provider: 'realtime-sdk' });
        break;

      case 'conversation.item.input_audio_transcription.completed':
        // User spoke - add to conversation history and emit transcript
        const userText = message.transcript;
        this.conversationHistory.push({ role: 'user', content: userText });
        
        const userMessage = this.createMessage('user', userText);
        this.emit('message', userMessage);
        this.emit('transcript', userText);
        break;

      case 'response.audio_transcript.done':
        // Assistant finished speaking - add to conversation history
        const assistantText = message.transcript;
        this.conversationHistory.push({ role: 'assistant', content: assistantText });
        
        const assistantMessage = this.createMessage('assistant', assistantText);
        this.emit('message', assistantMessage);
        break;

      case 'response.audio.delta':
        // Stream audio response
        if (message.delta) {
          const audioChunk: AudioChunk = {
            data: message.delta,
            format: 'pcm',
            sampleRate: 24000,
            channels: 1
          };
          this.emit('audio', audioChunk);
        }
        break;

      case 'response.function_call_arguments.done':
        // Function call completed - execute through Agents SDK
        this.handleToolCall(message.call_id, message.name, JSON.parse(message.arguments));
        break;

      case 'error':
        console.error('RealtimeSDK error:', message.error);
        this.handleError(message.error.message || 'Unknown error');
        break;

      default:
        // Handle other message types as needed
        break;
    }
  }

  private async handleToolCall(callId: string, toolName: string, args: any): Promise<void> {
    console.log('🔧 RealtimeSDK tool call:', toolName, args);
    
    try {
      if (toolName === 'agents_sdk_orchestrate') {
        // Use the SDK endpoint for enhanced analysis
        const response = await agentOrchestratorService.sendQuery(
          args.query,
          args.conversation_history || this.conversationHistory
        );

        // Send tool result back to OpenAI
        const toolResult = {
          type: 'conversation.item.create',
          item: {
            type: 'function_call_output',
            call_id: callId,
            output: JSON.stringify({
              text: response.text,
              tools_used: response.tools_used,
              data: response.data,
              chart_commands: response.chart_commands,
              chart_commands_structured: response.chart_commands_structured
            })
          }
        };

        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
          this.websocket.send(JSON.stringify(toolResult));
          
          // Trigger response generation
          this.websocket.send(JSON.stringify({ type: 'response.create' }));
        }

        // Emit tool events for debugging
        this.emit('toolCall', { name: toolName, arguments: args });
        this.emit('toolResult', { name: toolName, result: response });
      }
    } catch (error) {
      console.error('Tool call failed:', error);
      
      // Send error back to OpenAI
      const errorResult = {
        type: 'conversation.item.create',
        item: {
          type: 'function_call_output',
          call_id: callId,
          output: JSON.stringify({
            error: error instanceof Error ? error.message : 'Tool call failed'
          })
        }
      };

      if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(JSON.stringify(errorResult));
      }
    }
  }

  async disconnect(): Promise<void> {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    this.updateConnectionState('disconnected');
    this.emit('disconnected', { provider: 'realtime-sdk' });
  }

  // Voice conversation methods
  async startConversation(): Promise<void> {
    if (this._connectionState !== 'connected') {
      await this.connect();
    }
    
    this.isRecording = true;
    this.emit('conversationStarted', { timestamp: new Date().toISOString() });
  }

  async stopConversation(): Promise<void> {
    this.isRecording = false;
    this.emit('conversationStopped', { timestamp: new Date().toISOString() });
    await this.disconnect();
  }

  async sendAudio(audioChunk: AudioChunk): Promise<void> {
    if (this._connectionState !== 'connected' || !this.websocket || !this.isRecording) {
      return;
    }

    // Convert base64 audio to append format for OpenAI
    try {
      const audioAppend = {
        type: 'input_audio_buffer.append',
        audio: audioChunk.data
      };
      
      this.websocket.send(JSON.stringify(audioAppend));
    } catch (error) {
      console.error('Failed to send audio:', error);
      throw new Error('Failed to send audio data');
    }
  }

  async sendMessage(message: string): Promise<void> {
    if (this._connectionState !== 'connected' || !this.websocket) {
      throw new Error('Not connected to OpenAI Realtime');
    }

    // Add text message to conversation
    const textItem = {
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [
          {
            type: 'input_text',
            text: message
          }
        ]
      }
    };

    this.websocket.send(JSON.stringify(textItem));
    
    // Trigger response
    this.websocket.send(JSON.stringify({ type: 'response.create' }));
    
    // Update conversation history and emit event
    this.conversationHistory.push({ role: 'user', content: message });
    this.emit('message', this.createMessage('user', message));
  }

  async setVoice(voiceId: string): Promise<void> {
    this.currentVoice = voiceId;
    
    // Update session voice if connected
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      const sessionUpdate = {
        type: 'session.update',
        session: {
          voice: voiceId
        }
      };
      this.websocket.send(JSON.stringify(sessionUpdate));
    }
  }

  async getAvailableVoices(): Promise<Array<{ id: string; name: string; }>> {
    return [
      { id: 'alloy', name: 'Alloy' },
      { id: 'echo', name: 'Echo' },
      { id: 'fable', name: 'Fable' },
      { id: 'onyx', name: 'Onyx' },
      { id: 'nova', name: 'Nova' },
      { id: 'shimmer', name: 'Shimmer' }
    ];
  }

  // Additional methods for RealtimeSDK
  async interruptResponse(): Promise<void> {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({ type: 'response.cancel' }));
    }
  }

  getConversationHistory(): Array<{ role: string; content: string }> {
    return this.conversationHistory;
  }

  // Private methods
  private generateSessionId(): string {
    return `realtime_sdk_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}