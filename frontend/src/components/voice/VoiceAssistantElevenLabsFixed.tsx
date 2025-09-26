import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useElevenLabsConversation } from '../../hooks/useElevenLabsConversation';
import { AudioVisualizer } from '../ui/AudioVisualizer';
import { ChatHistory } from '../ui/ChatHistory';
import '../../styles/VoiceAssistant.css';
import { getApiUrl } from '../utils/apiConfig';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface VoiceAssistantElevenLabsProps {
  responseMode?: 'conversation' | 'overview';
  onModeChange?: (mode: 'conversation' | 'overview') => void;
}

export const VoiceAssistantElevenLabsFixed: React.FC<VoiceAssistantElevenLabsProps> = ({ 
  responseMode = 'conversation',
  onModeChange 
}) => {
  const [sessionId] = useState<string>(() => crypto.randomUUID());
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<'voice' | 'text'>('voice');
  const lastResponseMode = useRef<'conversation' | 'overview'>(responseMode);
  
  // Audio processing refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);

  const apiUrl = getApiUrl();

  // Save message to backend
  const saveMessage = async (role: string, content: string) => {
    try {
      await fetch(`${apiUrl}/conversations/record`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          role,
          content,
          user_id: null
        })
      });
    } catch (error) {
      console.error('Failed to save message:', error);
    }
  };

  const {
    isConnected,
    isLoading,
    error,
    messages: elevenLabsMessages,
    startConversation,
    stopConversation,
    sendTextMessage,
    sendAudioChunk,
  } = useElevenLabsConversation({
    apiUrl,
    onUserTranscript: (transcript) => {
      const message: Message = {
        role: 'user',
        content: transcript,
        timestamp: new Date().toISOString()
      };
      setLocalMessages(prev => [...prev, message]);
      saveMessage('user', transcript);
    },
    onAgentResponse: (response) => {
      const message: Message = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString()
      };
      setLocalMessages(prev => [...prev, message]);
      saveMessage('assistant', response);
    },
    onConnectionChange: (connected) => {
      if (!connected) {
        setIsRecording(false);
        stopVoiceRecording();
      }
    }
  });

  // Convert Float32 PCM to Int16 PCM (required by ElevenLabs)
  const convertFloat32ToInt16 = (float32Array: Float32Array): Int16Array => {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      // Convert float32 (-1 to 1) to int16 (-32768 to 32767)
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
  };

  // Convert Int16Array to base64
  const int16ArrayToBase64 = (int16Array: Int16Array): string => {
    const uint8Array = new Uint8Array(int16Array.buffer);
    let binary = '';
    for (let i = 0; i < uint8Array.length; i++) {
      binary += String.fromCharCode(uint8Array[i]);
    }
    return btoa(binary);
  };

  // FIXED: Stream PCM audio continuously
  const startVoiceRecording = useCallback(async () => {
    if (!isConnected) {
      await startConversation();
      // Wait a bit for connection to establish
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    try {
      // Get microphone stream
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        } 
      });
      streamRef.current = stream;

      // Create audio context with 16kHz sample rate (ElevenLabs requirement)
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Create processor for real-time PCM capture
      const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        if (!isRecording) return;

        // Get raw PCM data
        const inputData = e.inputBuffer.getChannelData(0);
        
        // Calculate audio level for visualization
        const sum = inputData.reduce((acc, val) => acc + Math.abs(val), 0);
        const average = sum / inputData.length;
        setAudioLevel(average * 5); // Scale for visualization

        // Convert to 16-bit PCM and send
        const pcm16 = convertFloat32ToInt16(inputData);
        const base64Audio = int16ArrayToBase64(pcm16);
        
        // Stream audio chunk immediately
        sendAudioChunk(base64Audio);
      };

      // Connect audio nodes
      source.connect(processor);
      processor.connect(audioContextRef.current.destination);

      setIsRecording(true);
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Microphone access denied or unavailable. Please check permissions.');
    }
  }, [isConnected, startConversation, sendAudioChunk]);

  const stopVoiceRecording = useCallback(() => {
    setIsRecording(false);
    setAudioLevel(0);

    // Clean up audio nodes
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  // Handle text input
  const handleSendText = () => {
    if (inputText.trim() && isConnected) {
      const message: Message = {
        role: 'user',
        content: inputText,
        timestamp: new Date().toISOString()
      };
      setLocalMessages(prev => [...prev, message]);
      
      // Prepend mode context if in overview mode
      const textToSend = responseMode === 'overview' 
        ? `[Overview mode requested] ${inputText}`
        : inputText;
      
      sendTextMessage(textToSend);
      saveMessage('user', inputText);
      setInputText('');
    }
  };

  const handleClearHistory = () => {
    setLocalMessages([]);
    if (isConnected) {
      stopConversation();
    }
  };

  const toggleMode = () => {
    setMode(prev => prev === 'voice' ? 'text' : 'voice');
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopVoiceRecording();
    };
  }, [stopVoiceRecording]);

  return (
    <div className="voice-assistant">
      <div className="status-bar">
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </div>
        <div className="mode-toggle">
          <button onClick={toggleMode} className="mode-button">
            Input: {mode === 'voice' ? '🎤 Voice' : '⌨️ Text'}
          </button>
        </div>
        <div className="response-mode-indicator">
          {responseMode === 'conversation' ? '💬 Quick' : '📊 Detailed'}
        </div>
      </div>

      <div className="chat-container">
        <ChatHistory messages={localMessages} />
      </div>

      <AudioVisualizer isActive={isRecording} audioLevel={audioLevel} />

      <div className="controls">
        {mode === 'voice' ? (
          <>
            {!isConnected ? (
              <button 
                onClick={() => startConversation()}
                disabled={isLoading}
                className="connect-button"
              >
                {isLoading ? 'Connecting...' : 'Start Voice Chat'}
              </button>
            ) : (
              <div className="voice-controls">
                <button
                  onMouseDown={startVoiceRecording}
                  onMouseUp={stopVoiceRecording}
                  onMouseLeave={stopVoiceRecording}
                  onTouchStart={startVoiceRecording}
                  onTouchEnd={stopVoiceRecording}
                  className={`mic-button ${isRecording ? 'recording' : ''}`}
                  disabled={!isConnected}
                >
                  {isRecording ? '🔴 Recording' : '🎤 Hold to Talk'}
                </button>
                <button 
                  onClick={stopConversation}
                  className="disconnect-button"
                >
                  End Chat
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-controls">
            {!isConnected && (
              <button 
                onClick={() => startConversation()}
                disabled={isLoading}
                className="connect-button"
              >
                {isLoading ? 'Connecting...' : 'Connect'}
              </button>
            )}
            <div className="text-input-group">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
                placeholder="Type your message..."
                disabled={!isConnected}
                className="text-input"
              />
              <button 
                onClick={handleSendText}
                disabled={!isConnected || !inputText.trim()}
                className="send-button"
              >
                Send
              </button>
            </div>
          </div>
        )}

        <button onClick={handleClearHistory} className="clear-button">
          Clear History
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
    </div>
  );
};