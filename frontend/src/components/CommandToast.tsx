import { useEffect, useState } from 'react';
import './CommandToast.css';

interface CommandToastProps {
  command: string | null;
  type: 'success' | 'error' | 'info';
  duration?: number;
  onClose?: () => void;
}

export function CommandToast({ command, type, duration = 2000, onClose }: CommandToastProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (command) {
      setIsVisible(true);
      setIsExiting(false);

      const timer = setTimeout(() => {
        setIsExiting(true);
        setTimeout(() => {
          setIsVisible(false);
          onClose?.();
        }, 300); // Animation duration
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [command, duration, onClose]);

  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'info':
      default:
        return '📊';
    }
  };

  const getTypeClass = () => {
    switch (type) {
      case 'success':
        return 'toast-success';
      case 'error':
        return 'toast-error';
      case 'info':
      default:
        return 'toast-info';
    }
  };

  return (
    <div className={`command-toast ${getTypeClass()} ${isExiting ? 'toast-exit' : 'toast-enter'}`}>
      <span className="toast-icon">{getIcon()}</span>
      <span className="toast-message">{command}</span>
    </div>
  );
}