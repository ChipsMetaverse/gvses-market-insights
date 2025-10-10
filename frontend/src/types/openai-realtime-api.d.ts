declare module 'openai-realtime-api' {
  export type EventHandlerCallback<T = any> = (event: T) => void;

  export namespace RealtimeClientEvents {
    export type EventType = string;
  }

  export namespace RealtimeServerEvents {
    export type EventType = string;
  }

  export namespace RealtimeCustomEvents {
    export type EventType = string;
  }

  export interface ConversationAPI {
    getItems(): any[];
  }

  export interface RealtimeClientOptions {
    url: string;
    apiKey: string;
    dangerouslyAllowAPIKeyInBrowser?: boolean;
  }

  export class RealtimeClient {
    constructor(options: RealtimeClientOptions);
    on<T = any>(event: string, handler: EventHandlerCallback<T>): void;
    connect(): Promise<void>;
    disconnect(): void;
    appendInputAudio(audio: Int16Array): void;
    createResponse(): void;
    cancelResponse(id: string, code?: number): void;
    readonly conversation: ConversationAPI;
    readonly realtime: {
      send(event: string, payload: any): void;
    };
  }
}
