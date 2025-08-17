import { useCallback, useEffect, useRef, useState } from 'react';
import { useVoiceStream } from 'voice-stream';

type BaseEvent = { type: string };

type PingEvent = BaseEvent & {
  type: 'ping';
  ping_event: { event_id: number; ping_ms?: number };
};

type AudioEvent = BaseEvent & {
  type: 'audio';
  audio_event: { audio_base_64: string; event_id: number };
};

type UserTranscriptEvent = BaseEvent & {
  type: 'user_transcript';
  user_transcription_event: { user_transcript: string };
};

type AgentResponseEvent = BaseEvent & {
  type: 'agent_response';
  agent_response_event: { agent_response: string };
};

type AgentResponseCorrectionEvent = BaseEvent & {
  type: 'agent_response_correction';
  agent_response_correction_event: { original_agent_response: string; corrected_agent_response: string };
};

type ElevenLabsWebSocketEvent =
  | PingEvent
  | AudioEvent
  | UserTranscriptEvent
  | AgentResponseEvent
  | AgentResponseCorrectionEvent
  | BaseEvent;

export type ConversationMessage = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};

type UseAgentConversationResult = {
  isConnected: boolean;
  isStreamingAudio: boolean;
  audioLevel: number;
  messages: ConversationMessage[];
  startConversation: () => Promise<void>;
  stopConversation: () => Promise<void>;
  sendUserMessage: (text: string) => void;
};

// Basic PCM playback queue for 16-bit mono PCM at 44.1kHz
function createPcmPlayer() {
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  let queueTime = audioContext.currentTime;

  const playPcmBase64 = async (base64: string, sampleRate = 44100) => {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const buffer = new ArrayBuffer(len);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < len; i++) view[i] = binaryString.charCodeAt(i);

    // Interpret as 16-bit signed little-endian PCM
    const int16 = new Int16Array(buffer);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) {
      float32[i] = Math.max(-1, Math.min(1, int16[i] / 32768));
    }

    const audioBuffer = audioContext.createBuffer(1, float32.length, sampleRate);
    audioBuffer.copyToChannel(float32, 0, 0);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);

    const startAt = Math.max(audioContext.currentTime, queueTime);
    source.start(startAt);
    queueTime = startAt + audioBuffer.duration;
  };

  return { playPcmBase64 };
}

export const useAgentConversation = (): UseAgentConversationResult => {
  const websocketRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreamingAudio, setIsStreamingAudio] = useState(false);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [audioLevel, setAudioLevel] = useState(0);

  const { startStreaming, stopStreaming } = useVoiceStream({
    onAudioChunked: (audioDataBase64: string) => {
      const ws = websocketRef.current;
      if (!ws || ws.readyState !== WebSocket.OPEN) return;
      ws.send(
        JSON.stringify({
          user_audio_chunk: audioDataBase64,
        })
      );

      // Derive audio level from PCM base64 chunk (assumes 16-bit PCM little-endian)
      try {
        const bin = atob(audioDataBase64);
        const len = bin.length;
        // Use a small window to limit work
        const step = 2; // 16-bit samples
        let sumSquares = 0;
        let count = 0;
        for (let i = 0; i < len - 1; i += step * 16) { // downsample level computation
          const low = bin.charCodeAt(i);
          const high = bin.charCodeAt(i + 1);
          // little-endian int16
          let sample = (high << 8) | low;
          if (sample & 0x8000) sample = sample - 0x10000;
          const norm = sample / 32768;
          sumSquares += norm * norm;
          count++;
        }
        if (count > 0) {
          const rms = Math.sqrt(sumSquares / count);
          // Smooth level to avoid jitter
          setAudioLevel((prev) => prev * 0.7 + rms * 0.3);
        }
      } catch {
        // ignore level errors
      }
    },
  });

  const { playPcmBase64 } = createPcmPlayer();

  const startConversation = useCallback(async () => {
    if (isConnected) return;
    // Get signed URL from backend
    const apiUrl = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';
    const resp = await fetch(`${apiUrl}/elevenlabs/signed-url`);
    if (!resp.ok) throw new Error('Failed to obtain ElevenLabs signed URL');
    const { signed_url, signedUrl } = await resp.json();
    const url: string = signed_url || signedUrl;
    if (!url) throw new Error('Invalid signed URL response');

    const ws = new WebSocket(url);

    ws.onopen = async () => {
      setIsConnected(true);
      setIsStreamingAudio(true);
      // Notify server about client capabilities if needed
      ws.send(
        JSON.stringify({
          type: 'conversation_initiation_client_data',
        })
      );
      await startStreaming();
    };

    ws.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data) as ElevenLabsWebSocketEvent;

        if (data.type === 'ping') {
          const ping = data as PingEvent;
          setTimeout(() => {
            ws.send(
              JSON.stringify({
                type: 'pong',
                event_id: ping.ping_event.event_id,
              })
            );
          }, ping.ping_event.ping_ms || 0);
          return;
        }

        if (data.type === 'audio') {
          const audio = data as AudioEvent;
          // ElevenLabs default example uses PCM 44.1kHz
          await playPcmBase64(audio.audio_event.audio_base_64, 44100);
          return;
        }

        if (data.type === 'user_transcript') {
          const e = data as UserTranscriptEvent;
          setMessages((prev) => [
            ...prev,
            { role: 'user', content: e.user_transcription_event.user_transcript, timestamp: new Date().toISOString() },
          ]);
          return;
        }

        if (data.type === 'agent_response') {
          const e = data as AgentResponseEvent;
          setMessages((prev) => [
            ...prev,
            { role: 'assistant', content: e.agent_response_event.agent_response, timestamp: new Date().toISOString() },
          ]);
          return;
        }

        if (data.type === 'agent_response_correction') {
          const e = data as AgentResponseCorrectionEvent;
          setMessages((prev) => {
            const copy = [...prev];
            for (let i = copy.length - 1; i >= 0; i--) {
              if (copy[i].role === 'assistant') {
                copy[i] = { ...copy[i], content: e.agent_response_correction_event.corrected_agent_response };
                break;
              }
            }
            return copy;
          });
          return;
        }
      } catch (err) {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      websocketRef.current = null;
      setIsConnected(false);
      setIsStreamingAudio(false);
      stopStreaming();
    };

    websocketRef.current = ws;
  }, [isConnected, startStreaming, stopStreaming, playPcmBase64]);

  const stopConversation = useCallback(async () => {
    const ws = websocketRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
  }, []);

  const sendUserMessage = useCallback((text: string) => {
    const ws = websocketRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(
      JSON.stringify({
        type: 'user_message',
        text,
      })
    );
  }, []);

  useEffect(() => {
    return () => {
      const ws = websocketRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, []);

  return {
    isConnected,
    isStreamingAudio,
    audioLevel,
    messages,
    startConversation,
    stopConversation,
    sendUserMessage,
  };
};


