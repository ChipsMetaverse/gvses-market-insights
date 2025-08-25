import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Database, Globe, Zap, FileSearch, Brain, Wifi } from 'lucide-react';
import { cn } from '@/lib/utils';

interface DataSource {
  name: string;
  type: 'pricing' | 'fundamentals' | 'streaming' | 'analysis' | 'filings' | 'news';
  status?: 'active' | 'inactive' | 'error';
  lastUpdate?: string;
}

interface DataSourceBadgesProps {
  sources: DataSource[] | Record<string, string>;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showStatus?: boolean;
}

export function DataSourceBadges({ 
  sources, 
  className,
  size = 'md',
  showStatus = false
}: DataSourceBadgesProps) {
  // Convert object format to array format if needed
  const sourcesArray: DataSource[] = Array.isArray(sources) 
    ? sources 
    : Object.entries(sources).map(([type, name]) => ({
        name,
        type: type as DataSource['type'],
        status: 'active'
      }));

  const getIcon = (type: DataSource['type']) => {
    const iconSize = size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
    switch (type) {
      case 'pricing':
        return <Database className={iconSize} />;
      case 'fundamentals':
        return <FileSearch className={iconSize} />;
      case 'streaming':
        return <Wifi className={iconSize} />;
      case 'analysis':
        return <Brain className={iconSize} />;
      case 'filings':
        return <FileSearch className={iconSize} />;
      case 'news':
        return <Globe className={iconSize} />;
      default:
        return <Database className={iconSize} />;
    }
  };

  const getColor = (type: DataSource['type'], status?: DataSource['status']) => {
    if (status === 'error') return 'border-red-500 text-red-700 bg-red-50';
    if (status === 'inactive') return 'border-gray-300 text-gray-500 bg-gray-50';

    switch (type) {
      case 'pricing':
        return 'border-blue-500 text-blue-700 bg-blue-50';
      case 'fundamentals':
        return 'border-purple-500 text-purple-700 bg-purple-50';
      case 'streaming':
        return 'border-green-500 text-green-700 bg-green-50';
      case 'analysis':
        return 'border-orange-500 text-orange-700 bg-orange-50';
      case 'filings':
        return 'border-indigo-500 text-indigo-700 bg-indigo-50';
      case 'news':
        return 'border-pink-500 text-pink-700 bg-pink-50';
      default:
        return 'border-gray-500 text-gray-700 bg-gray-50';
    }
  };

  const getStatusIcon = (status?: DataSource['status']) => {
    const iconSize = size === 'sm' ? 'w-2 h-2' : 'w-3 h-3';
    switch (status) {
      case 'active':
        return <Zap className={cn(iconSize, 'text-green-600')} />;
      case 'error':
        return <span className={cn(iconSize, 'block rounded-full bg-red-600')} />;
      default:
        return null;
    }
  };

  const badgeSize = size === 'sm' ? 'text-xs px-2 py-0.5' : size === 'lg' ? 'text-base px-3 py-1.5' : '';

  return (
    <TooltipProvider>
      <div className={cn('flex flex-wrap gap-2', className)}>
        {sourcesArray.map((source, index) => (
          <Tooltip key={index}>
            <TooltipTrigger asChild>
              <Badge 
                variant="outline" 
                className={cn(
                  'flex items-center gap-1 cursor-help',
                  getColor(source.type, source.status),
                  badgeSize
                )}
              >
                {getIcon(source.type)}
                <span className="font-medium">{source.name}</span>
                {showStatus && source.status && (
                  <span className="ml-1">
                    {getStatusIcon(source.status)}
                  </span>
                )}
              </Badge>
            </TooltipTrigger>
            <TooltipContent>
              <div className="space-y-1">
                <p className="font-semibold capitalize">{source.type} Data</p>
                <p className="text-xs">Provider: {source.name}</p>
                {source.status && (
                  <p className="text-xs">
                    Status: <span className="capitalize">{source.status}</span>
                  </p>
                )}
                {source.lastUpdate && (
                  <p className="text-xs">
                    Updated: {new Date(source.lastUpdate).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </TooltipContent>
          </Tooltip>
        ))}
      </div>
    </TooltipProvider>
  );
}

// Standalone component for a single data source indicator
export function DataSourceIndicator({ 
  source, 
  type,
  className,
  size = 'md'
}: { 
  source: string; 
  type: DataSource['type'];
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}) {
  return (
    <DataSourceBadges 
      sources={[{ name: source, type, status: 'active' }]}
      className={className}
      size={size}
    />
  );
}