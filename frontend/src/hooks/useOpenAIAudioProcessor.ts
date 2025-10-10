/**
 * OpenAI Audio Processor Hook
 * Handles microphone capture and audio processing for OpenAI Realtime API
 * Captures audio in PCM16 format at 24kHz sample rate as required by OpenAI
 */

import { useCallback, useRef, useState } from 'react';

interface UseOpenAIAudioProcessorOptions {
  onAudioData: (audioData: Int16Array) => void;
  onError?: (error: Error) => void;
}

export const useOpenAIAudioProcessor = (options: UseOpenAIAudioProcessorOptions) => {
  const { onAudioData, onError } = options;

  const [isRecording, setIsRecording] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorNodeRef = useRef<ScriptProcessorNode | null>(null);

  // Store callbacks in refs to prevent re-creating startRecording/stopRecording
  const callbacksRef = useRef({ onAudioData, onError });
  callbacksRef.current = { onAudioData, onError };

  const startRecording = useCallback(async () => {
    console.log('🎤 [AUDIO PROCESSOR] ========== startRecording() CALLED ==========');
    console.log('🎤 [AUDIO PROCESSOR] Checking navigator.mediaDevices availability:', !!navigator.mediaDevices);
    console.log('🎤 [AUDIO PROCESSOR] Checking getUserMedia availability:', !!navigator.mediaDevices?.getUserMedia);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const error = new Error('getUserMedia not supported in this browser');
      console.error('❌ [AUDIO PROCESSOR]', error.message);
      callbacksRef.current.onError?.(error);
      return;
    }

    try {
      console.log('🎤 [AUDIO PROCESSOR] About to call getUserMedia()...');

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 24000, // OpenAI requires 24kHz
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      console.log('✅ [AUDIO PROCESSOR] getUserMedia() completed successfully!');
      console.log('✅ [AUDIO PROCESSOR] Stream obtained:', stream);
      mediaStreamRef.current = stream;
      console.log('✅ [AUDIO PROCESSOR] Microphone access granted');

      // Create AudioContext with 24kHz sample rate
      const audioContext = new AudioContext({ sampleRate: 24000 });
      audioContextRef.current = audioContext;

      // Resume if suspended (browser autoplay policy)
      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      console.log('🔊 AudioContext created, state:', audioContext.state);

      // Create source node from microphone stream
      const sourceNode = audioContext.createMediaStreamSource(stream);
      sourceNodeRef.current = sourceNode;

      // Create ScriptProcessor for audio processing
      // Buffer size 4096 = ~170ms chunks at 24kHz
      const processorNode = audioContext.createScriptProcessor(4096, 1, 1);
      processorNodeRef.current = processorNode;

      // Process audio data
      processorNode.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0); // Float32Array

        // Convert Float32 to Int16 PCM (required by OpenAI)
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          // Clamp to [-1, 1] and convert to Int16 range
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Send to OpenAI via callback
        callbacksRef.current.onAudioData(pcmData);
      };

      // Connect audio graph
      sourceNode.connect(processorNode);
      processorNode.connect(audioContext.destination);

      setIsRecording(true);
      console.log('🎙️ Recording started, sending audio to OpenAI...');

    } catch (error) {
      console.error('❌ Failed to start microphone recording:', error);
      const err = error instanceof Error ? error : new Error('Microphone access denied');
      callbacksRef.current.onError?.(err);
      setIsRecording(false);
    }
  }, []);

  const stopRecording = useCallback(() => {
    console.log('🛑 Stopping microphone recording...');

    // Disconnect and clean up processor
    if (processorNodeRef.current) {
      processorNodeRef.current.disconnect();
      processorNodeRef.current.onaudioprocess = null;
      processorNodeRef.current = null;
    }

    // Disconnect source
    if (sourceNodeRef.current) {
      sourceNodeRef.current.disconnect();
      sourceNodeRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop media stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    setIsRecording(false);
    console.log('✅ Recording stopped');
  }, []);

  return {
    isRecording,
    startRecording,
    stopRecording
  };
};
