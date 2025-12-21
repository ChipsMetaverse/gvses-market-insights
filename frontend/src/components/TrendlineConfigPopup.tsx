import React, { useEffect, useRef, useState } from 'react';
import type { Trendline } from '../drawings/types';
import './TrendlineConfigPopup.css';

interface TrendlineConfigPopupProps {
  trendline: Trendline;
  position: { x: number; y: number };
  onDelete: () => void;
  onExtendLeft: () => void;
  onExtendRight: () => void;
  onClose: () => void;
}

export const TrendlineConfigPopup: React.FC<TrendlineConfigPopupProps> = ({
  trendline,
  position,
  onDelete,
  onExtendLeft,
  onExtendRight,
  onClose,
}) => {
  const popupRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(position);

  // Adjust position to keep popup within viewport
  useEffect(() => {
    if (!popupRef.current) return;

    const popup = popupRef.current;
    const rect = popup.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let { x, y } = position;

    // Adjust horizontal position
    if (x + rect.width > viewportWidth) {
      x = viewportWidth - rect.width - 10;
    }
    if (x < 0) {
      x = 10;
    }

    // Adjust vertical position
    if (y + rect.height > viewportHeight) {
      y = viewportHeight - rect.height - 10;
    }
    if (y < 0) {
      y = 10;
    }

    setAdjustedPosition({ x, y });
  }, [position]);

  // Close popup when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (popupRef.current && !popupRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  return (
    <div
      ref={popupRef}
      className="trendline-config-popup"
      style={{
        left: `${adjustedPosition.x}px`,
        top: `${adjustedPosition.y}px`,
      }}
    >
      <div className="trendline-config-header">
        <span className="trendline-config-title">
          {trendline.name || 'Trendline'}
        </span>
        <button
          className="trendline-config-close"
          onClick={onClose}
          aria-label="Close"
        >
          ×
        </button>
      </div>

      <div className="trendline-config-body">
        <div className="trendline-config-section">
          <label>Extend Line</label>
          <div className="trendline-config-buttons">
            <button
              className="trendline-config-btn"
              onClick={onExtendLeft}
              title="Extend line to the left"
            >
              ← Extend Left
            </button>
            <button
              className="trendline-config-btn"
              onClick={onExtendRight}
              title="Extend line to the right"
            >
              Extend Right →
            </button>
          </div>
        </div>

        <div className="trendline-config-section">
          <button
            className="trendline-config-btn trendline-config-delete"
            onClick={onDelete}
          >
            🗑️ Delete Trendline
          </button>
        </div>
      </div>

      <div className="trendline-config-info">
        <small>
          Lines extend infinitely in their direction.<br />
          Segments stop at points.
        </small>
      </div>
    </div>
  );
};
