import React, { useState, useRef, useEffect } from 'react';
import { TimeRange } from '../types/dashboard';

interface TimeRangeSelectorProps {
  selected: TimeRange;
  options?: TimeRange[];
  onChange: (range: TimeRange) => void;
  showAdvancedMenu?: boolean;
}

const DEFAULT_OPTIONS: TimeRange[] = [
  '10S',
  '30S',
  '1m',
  '3m',
  '5m',
  '10m',
  '15m',
  '30m',
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
  '1M',
  '3M',
  '6M',
  '1Y',
  '2Y',
  '3Y',
  '5Y',
  'YTD',
  'MAX',
];

const ADVANCED_TIMEFRAMES: { category: string; options: TimeRange[] }[] = [
  { category: 'Seconds', options: ['10S', '30S'] },
  { category: 'Minutes', options: ['1m', '3m', '5m', '10m', '15m', '30m'] },
  { category: 'Hours', options: ['1H', '2H', '3H', '4H', '6H', '8H', '12H'] },
  { category: 'Days', options: ['2D', '3D'] },
  { category: 'Weeks', options: ['1W'] },
  { category: 'Months', options: ['3M'] },
  { category: 'Years', options: ['5Y'] },
];

export const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  selected,
  options = DEFAULT_OPTIONS,
  onChange,
  showAdvancedMenu = false,
}) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMenuOpen]);

  // Get all timeframes that are NOT in the main options
  const advancedTimeframes = ADVANCED_TIMEFRAMES.map(group => ({
    ...group,
    options: group.options.filter(tf => !options.includes(tf))
  })).filter(group => group.options.length > 0);

  const handleAdvancedSelect = (range: TimeRange) => {
    onChange(range);
    setIsMenuOpen(false);
  };

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
      
      {showAdvancedMenu && advancedTimeframes.length > 0 && (
        <div className="time-range-dropdown" ref={menuRef}>
          <button
            className="time-range-button time-range-menu-button"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            title="More timeframes"
          >
            ⋯
          </button>
          
          {isMenuOpen && (
            <div className="time-range-menu">
              {advancedTimeframes.map(({ category, options: groupOptions }) => (
                <div key={category} className="time-range-menu-group">
                  <div className="time-range-menu-category">{category.toUpperCase()}</div>
                  {groupOptions.map((range) => (
                    <button
                      key={range}
                      className={`time-range-menu-item ${selected === range ? 'active' : ''}`}
                      onClick={() => handleAdvancedSelect(range)}
                    >
                      {range}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};