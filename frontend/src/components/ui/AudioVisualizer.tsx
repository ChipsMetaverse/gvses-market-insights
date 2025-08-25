import React, { useEffect, useRef } from 'react';
import '../../styles/AudioVisualizer.css';

interface AudioVisualizerProps {
  isActive: boolean;
  audioLevel: number;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({ isActive, audioLevel }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    canvas.height = canvas.offsetHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const bars = 32;
    const barWidth = canvas.offsetWidth / bars;
    const barGap = 2;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

      if (isActive) {
        // Draw animated bars based on audio level
        for (let i = 0; i < bars; i++) {
          const randomHeight = Math.random() * 0.5 + 0.5;
          const height = isActive ? audioLevel * 100 * randomHeight : 0;
          const x = i * barWidth;
          const y = (canvas.offsetHeight - height) / 2;

          // Create gradient
          const gradient = ctx.createLinearGradient(0, y, 0, y + height);
          gradient.addColorStop(0, '#4f46e5');
          gradient.addColorStop(1, '#818cf8');

          ctx.fillStyle = gradient;
          ctx.fillRect(x + barGap / 2, y, barWidth - barGap, height);
        }
      } else {
        // Draw idle state (flat line)
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, canvas.offsetHeight / 2);
        ctx.lineTo(canvas.offsetWidth, canvas.offsetHeight / 2);
        ctx.stroke();
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, audioLevel]);

  return (
    <div className="audio-visualizer">
      <canvas ref={canvasRef} className="visualizer-canvas" />
      {isActive && (
        <div className="pulse-ring">
          <div className="pulse-core"></div>
        </div>
      )}
    </div>
  );
};
