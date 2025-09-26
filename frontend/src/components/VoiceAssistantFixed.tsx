import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useElevenLabsConversation } from '../hooks/useElevenLabsConversation';
import { AudioVisualizer } from './AudioVisualizer';
import { ChatHistory } from './ChatHistory';
import './VoiceAssistant.css';
import { getApiUrl } from '../utils/apiConfig';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const VoiceAssistantFixed: React.FC = () => {
  const [sessionId] = useState<string>(() => crypto.randomUUID());
  const [inputText, setInputText] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<'voice' | 'text'>('voice');
  const [isListening, setIsListening] = useState(false);
  
  const apiUrl = getApiUrl();
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);

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
    startConversation,
    stopConversation,
    sendTextMessage,
    sendAudioChunk,
  } = useElevenLabsConversation({
    apiUrl,
    onUserTranscript: (transcript) => {
      console.log('User transcript:', transcript);
      const message: Message = {
        role: 'user',
        content: transcript,
        timestamp: new Date().toISOString()
      };
      setLocalMessages(prev => [...prev, message]);
      saveMessage('user', transcript);
    },
    onAgentResponse: (response) => {
      console.log('Agent response:', response);
      const message: Message = {
        role: 'assistant',
        content: response,
        timestamp: new Date().toISOString()
      };
      setLocalMessages(prev => [...prev, message]);
      saveMessage('assistant', response);
    },
    onConnectionChange: (connected) => {
      console.log('Connection changed:', connected);
      if (!connected) {
        stopListening();
      }
    }
  });

  // Audio level monitoring
  const updateAudioLevel = useCallback(() => {
    if (analyserRef.current && isListening) {
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setAudioLevel(average / 255);
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, [isListening]);

  // Start listening and streaming
  const startListening = useCallback(async () => {
    if (isListening) return;
    
    try {
      console.log('Starting voice streaming...');
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      streamRef.current = stream;
      
      // Set up audio context for visualization
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const visualSource = audioContextRef.current.createMediaStreamSource(stream);
      visualSource.connect(analyserRef.current);
      
      // Set up separate audio context to capture PCM data at 16kHz
      const captureContext = new AudioContext({ sampleRate: 16000 });
      const captureSource = captureContext.createMediaStreamSource(stream);
      const processor = captureContext.createScriptProcessor(4096, 1, 1);
      
      processor.onaudioprocess = (e) => {
        if (!isConnected) return;
        
        const inputData = e.inputBuffer.getChannelData(0);
        // Convert Float32Array to Int16Array (PCM16)
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        
        // Convert to base64
        const buffer = new ArrayBuffer(pcm16.length * 2);
        const view = new DataView(buffer);
        for (let i = 0; i < pcm16.length; i++) {
          view.setInt16(i * 2, pcm16[i], true); // little-endian
        }
        
        const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
        sendAudioChunk(base64);
      };
      
      captureSource.connect(processor);
      processor.connect(captureContext.destination);
      
      // Store references for cleanup
      (streamRef.current as any).captureContext = captureContext;
      (streamRef.current as any).processor = processor;
      setIsListening(true);
      updateAudioLevel();
      
      console.log('Voice streaming started');
    } catch (error) {
      console.error('Failed to start voice streaming:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  }, [isListening, isConnected, sendAudioChunk, updateAudioLevel]);

  // Stop listening
  const stopListening = useCallback(() => {
    console.log('Stopping voice streaming...');
    
    // Stop the audio processor
    if ((streamRef.current as any)?.processor) {
      (streamRef.current as any).processor.disconnect();
    }
    
    // Close capture context
    if ((streamRef.current as any)?.captureContext) {
      (streamRef.current as any).captureContext.close();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    setIsListening(false);
    setAudioLevel(0);
    console.log('Voice streaming stopped');
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
      sendTextMessage(inputText);
      saveMessage('user', inputText);
      setInputText('');
    }
  };

  // Clear history
  const handleClearHistory = () => {
    setLocalMessages([]);
    if (isConnected) {
      stopConversation();
    }
  };

  // Toggle mode
  const toggleMode = () => {
    if (isListening) {
      stopListening();
    }
    setMode(prev => prev === 'voice' ? 'text' : 'voice');
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopListening();
      if (isConnected) {
        stopConversation();
      }
    };
  }, []);

  // Start listening immediately when connected in voice mode
  useEffect(() => {
    if (isConnected && mode === 'voice' && !isListening) {
      startListening();
    }
  }, [isConnected, mode, isListening, startListening]);

  return (
    <div className="voice-assistant">
      <div className="status-bar">
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected to G\'sves' : '○ Disconnected'}
        </div>
        <div className="mode-toggle">
          <button onClick={toggleMode} className="mode-button">
            Mode: {mode === 'voice' ? '🎤 Voice' : '⌨️ Text'}
          </button>
        </div>
      </div>

      <div className="chat-container">
        <ChatHistory messages={localMessages} />
      </div>

      <AudioVisualizer isActive={isListening} audioLevel={audioLevel} />

      <div className="controls">
        {!isConnected ? (
          <button 
            onClick={() => startConversation()}
            disabled={isLoading}
            className="connect-button"
          >
            {isLoading ? 'Connecting...' : 'Start Voice Chat'}
          </button>
        ) : (
          <>
            {mode === 'voice' ? (
              <div className="voice-controls">
                <button 
                  onClick={() => {
                    stopListening();
                    stopConversation();
                  }}
                  className="disconnect-button"
                >
                  Stop Voice Chat
                </button>
                {isListening && (
                  <div className="listening-status">
                    🎤 Listening... Speak anytime
                  </div>
                )}
              </div>
            ) : (
              <div className="text-controls">
                <div className="text-input-group">
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
                    placeholder="Or type your message..."
                    className="text-input"
                  />
                  <button 
                    onClick={handleSendText}
                    disabled={!inputText.trim()}
                    className="send-button"
                  >
                    Send
                  </button>
                </div>
                <button 
                  onClick={() => {
                    stopListening();
                    stopConversation();
                  }}
                  className="disconnect-button"
                >
                  Stop Voice Chat
                </button>
              </div>
            )}
          </>
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

      {isConnected && localMessages.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          {mode === 'voice' 
            ? '🎤 Listening... You can speak now!'
            : 'Type your message and press Send'}
        </div>
      )}
    </div>
  );
};