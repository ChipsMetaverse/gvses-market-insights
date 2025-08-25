import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, TrendingDown, Minus, BarChart3, Brain } from 'lucide-react';
import { cn } from '@/lib/utils';

type MarketSentiment = 'bullish' | 'bearish' | 'neutral';

interface MarketSentimentIndicatorProps {
  sentiment: MarketSentiment;
  confidence?: number; // 0-100
  sources?: string[];
  analysis?: string;
  className?: string;
  compact?: boolean;
}

export function MarketSentimentIndicator({ 
  sentiment, 
  confidence = 75,
  sources = [],
  analysis,
  className,
  compact = false
}: MarketSentimentIndicatorProps) {
  const getSentimentIcon = () => {
    switch (sentiment) {
      case 'bullish':
        return <TrendingUp className="w-5 h-5" />;
      case 'bearish':
        return <TrendingDown className="w-5 h-5" />;
      default:
        return <Minus className="w-5 h-5" />;
    }
  };

  const getSentimentColor = () => {
    switch (sentiment) {
      case 'bullish':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'bearish':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getProgressColor = () => {
    switch (sentiment) {
      case 'bullish':
        return 'bg-green-600';
      case 'bearish':
        return 'bg-red-600';
      default:
        return 'bg-gray-600';
    }
  };

  if (compact) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <Badge variant="outline" className={cn("flex items-center gap-1", getSentimentColor())}>
          {getSentimentIcon()}
          <span className="capitalize">{sentiment}</span>
        </Badge>
        {confidence !== undefined && (
          <span className="text-sm text-muted-foreground">
            {confidence}% confidence
          </span>
        )}
      </div>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="w-5 h-5" />
          Market Sentiment Analysis
        </CardTitle>
        <CardDescription>
          AI-powered sentiment analysis from multiple sources
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Main sentiment display */}
        <div className={cn(
          "rounded-lg border-2 p-4 text-center",
          getSentimentColor()
        )}>
          <div className="flex justify-center mb-2">
            {getSentimentIcon()}
          </div>
          <h3 className="text-2xl font-bold capitalize mb-1">
            {sentiment}
          </h3>
          <p className="text-sm opacity-75">
            Market Outlook
          </p>
        </div>

        {/* Confidence meter */}
        {confidence !== undefined && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Confidence Level</span>
              <span className="font-medium">{confidence}%</span>
            </div>
            <Progress 
              value={confidence} 
              className="h-2"
              indicatorClassName={getProgressColor()}
            />
          </div>
        )}

        {/* Analysis text */}
        {analysis && (
          <div className="pt-4 border-t">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
              <BarChart3 className="w-4 h-4" />
              Analysis Summary
            </h4>
            <p className="text-sm text-muted-foreground">
              {analysis}
            </p>
          </div>
        )}

        {/* Data sources */}
        {sources.length > 0 && (
          <div className="pt-4 border-t">
            <h4 className="text-sm font-medium mb-2">Data Sources</h4>
            <div className="flex flex-wrap gap-1">
              {sources.map((source, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {source}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Sentiment breakdown visualization */}
        <div className="pt-4 border-t grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">
              {sentiment === 'bullish' ? '●' : '○'}
            </div>
            <p className="text-xs text-muted-foreground">Bullish</p>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-600">
              {sentiment === 'neutral' ? '●' : '○'}
            </div>
            <p className="text-xs text-muted-foreground">Neutral</p>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">
              {sentiment === 'bearish' ? '●' : '○'}
            </div>
            <p className="text-xs text-muted-foreground">Bearish</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}