import React from 'react';
import { TimeRange } from '../types/dashboard';

interface TimeRangeSelectorProps {
  selected: TimeRange;
  options?: TimeRange[];
  onChange: (range: TimeRange) => void;
}

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ 
  selected, 
  options = ['1D', '5D', '1M', '6M', 'YTD', '1Y', '5Y', 'MAX'],
  onChange 
}) => {
  return (
    <div className="time-range-selector">
      {options.map((range) => (
        <button
          key={range}
          className={`time-range-button ${selected === range ? 'active' : ''}`}
          onClick={() => onChange(range)}
        >
          {range}
        </button>
      ))}
    </div>
  );
};