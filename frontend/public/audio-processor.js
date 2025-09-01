/**
 * AudioWorklet Processor for real-time audio processing
 * Replaces deprecated ScriptProcessorNode
 */

class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.bufferSize = 4096;
    this.buffer = new Float32Array(this.bufferSize);
    this.bufferIndex = 0;
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    
    if (input && input[0]) {
      const inputChannel = input[0];
      
      // Copy input samples to buffer
      for (let i = 0; i < inputChannel.length; i++) {
        this.buffer[this.bufferIndex++] = inputChannel[i];
        
        // When buffer is full, send to main thread
        if (this.bufferIndex >= this.bufferSize) {
          this.port.postMessage({
            type: 'audio',
            buffer: this.buffer.slice(0, this.bufferIndex)
          });
          this.bufferIndex = 0;
        }
      }
      
      // Also send volume level for visualization
      const sum = inputChannel.reduce((acc, val) => acc + Math.abs(val), 0);
      const average = sum / inputChannel.length;
      const volume = Math.min(1, average * 10); // Scale for visualization
      
      this.port.postMessage({
        type: 'volume',
        level: volume
      });
    }
    
    // Keep processor alive
    return true;
  }
}

// Register the processor
registerProcessor('audio-processor', AudioProcessor);