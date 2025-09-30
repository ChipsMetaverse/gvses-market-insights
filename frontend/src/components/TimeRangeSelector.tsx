import React from 'react';
import { TimeRange } from '../types/dashboard';

interface TimeRangeSelectorProps {
  selected: TimeRange;
  options?: TimeRange[];
  onChange: (range: TimeRange) => void;
}

const DEFAULT_OPTIONS: TimeRange[] = [
  '10S',
  '30S',
  '1M',
  '3M',
  '5M',
  '10M',
  '15M',
  '30M',
  '1H',
  '2H',
  '3H',
  '4H',
  '6H',
  '8H',
  '12H',
  '1D',
  '2D',
  '3D',
  '5D',
  '1W',
  '1M_CAL',
  '1Y',
  '2Y',
  '3Y',
];

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  selected,
  options = DEFAULT_OPTIONS,
  onChange,
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