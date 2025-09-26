import React, { useState, useEffect, useCallback } from 'react';
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

export const VoiceAssistantElevenlabs: React.FC = () => {
  const [sessionId] = useState<string>(() => crypto.randomUUID());
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [localMessages, setLocalMessages] = useState<Message[]>([]);
  const [mode, setMode] = useState<'voice' | 'text'>('voice');

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
          user_id: null // Add if you have user auth
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
      }
    }
  });

  // Handle microphone for voice mode
  const startVoiceRecording = useCallback(async () => {
    if (!isConnected) {
      await startConversation();
    }
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks: Blob[] = [];

      // Create audio context for visualization
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      
      const updateAudioLevel = () => {
        if (isRecording) {
          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
          setAudioLevel(average / 255);
          requestAnimationFrame(updateAudioLevel);
        }
      };
      updateAudioLevel();

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result?.toString().split(',')[1];
          if (base64) {
            sendAudioChunk(base64);
          }
        };
        reader.readAsDataURL(audioBlob);
        
        stream.getTracks().forEach(track => track.stop());
        setAudioLevel(0);
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);

      // Store recorder reference to stop later
      (window as any).currentMediaRecorder = mediaRecorder;
      
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  }, [isConnected, startConversation, sendAudioChunk, isRecording]);

  const stopVoiceRecording = useCallback(() => {
    const mediaRecorder = (window as any).currentMediaRecorder;
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  }, []);

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

  const handleClearHistory = () => {
    setLocalMessages([]);
    if (isConnected) {
      stopConversation();
    }
  };

  const toggleMode = () => {
    setMode(prev => prev === 'voice' ? 'text' : 'voice');
  };

  return (
    <div className="voice-assistant">
      <div className="status-bar">
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
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