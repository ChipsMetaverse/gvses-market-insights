import React from 'react';
import clsx from 'clsx';
import { LineChart, Mic, Newspaper } from 'lucide-react';

export type MobileTabKey = 'chart' | 'analysis' | 'voice';

interface MobileTabBarProps {
  activeTab: MobileTabKey;
  onTabChange: (tab: MobileTabKey) => void;
  analysisBadgeCount?: number;
  voiceBadgeCount?: number;
}

type TabConfig = {
  key: MobileTabKey;
  label: string;
  Icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
};

const TAB_CONFIG: TabConfig[] = [
  { key: 'analysis', label: 'Analysis', Icon: Newspaper },
  { key: 'chart', label: 'Chart', Icon: LineChart },
  { key: 'voice', label: 'Voice', Icon: Mic },
];

const formatBadgeCount = (count?: number): string | null => {
  if (!count || count <= 0) {
    return null;
  }
  if (count > 9) {
    return '9+';
  }
  return count.toString();
};

export const MobileTabBar: React.FC<MobileTabBarProps> = ({
  activeTab,
  onTabChange,
  analysisBadgeCount = 0,
  voiceBadgeCount = 0,
}) => {
  const getBadgeCount = (key: MobileTabKey): number => {
    if (key === 'analysis') {
      return analysisBadgeCount;
    }
    if (key === 'voice') {
      return voiceBadgeCount;
    }
    return 0;
  };

  return (
    <nav className="mobile-tab-bar" aria-label="Dashboard navigation">
      <ul className="mobile-tab-bar__list">
        {TAB_CONFIG.map(({ key, label, Icon }) => {
          const badge = formatBadgeCount(getBadgeCount(key));
          return (
            <li key={key}>
              <button
                type="button"
                className={clsx('mobile-tab-bar__button', {
                  'mobile-tab-bar__button--active': activeTab === key,
                })}
                aria-pressed={activeTab === key}
                aria-label={label}
                onClick={() => onTabChange(key)}
              >
                <Icon aria-hidden="true" />
                <span>{label}</span>
                {badge && <span className="mobile-tab-bar__badge">{badge}</span>}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};
