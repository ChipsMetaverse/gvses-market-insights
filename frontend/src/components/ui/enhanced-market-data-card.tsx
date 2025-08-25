import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Activity, TrendingUp, TrendingDown, FileText, Wifi, WifiOff } from 'lucide-react';
import { HybridMarketData } from '@/services/hybridMarketDataService';

interface EnhancedMarketDataCardProps {
  data: HybridMarketData;
  className?: string;
}

export function EnhancedMarketDataCard({ data, className }: EnhancedMarketDataCardProps) {
  const priceChange = data.changePercent || 0;
  const isPositive = priceChange >= 0;
  
  // Determine GVSES level color
  const getSignalColor = (signal?: string) => {
    switch (signal) {
      case 'LTB': return 'bg-green-600';
      case 'ST': return 'bg-yellow-600';
      case 'QE': return 'bg-orange-600';
      default: return 'bg-gray-600';
    }
  };

  // Determine sentiment color
  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment) {
      case 'bullish': return 'text-green-600';
      case 'bearish': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000000) return `${(volume / 1000000000).toFixed(2)}B`;
    if (volume >= 1000000) return `${(volume / 1000000).toFixed(2)}M`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(2)}K`;
    return volume.toString();
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-bold">{data.symbol}</CardTitle>
            <CardDescription className="flex items-center gap-2">
              <span className="text-2xl font-semibold">
                {formatPrice(data.streamingPrice || data.price)}
              </span>
              <span className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                {Math.abs(data.change).toFixed(2)} ({Math.abs(priceChange).toFixed(2)}%)
              </span>
            </CardDescription>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge className={getSignalColor(data.signal)}>
              GVSES: {data.signal || 'N/A'}
            </Badge>
            {data.isStreaming ? (
              <Badge variant="outline" className="flex items-center gap-1">
                <Wifi className="w-3 h-3" />
                Live
              </Badge>
            ) : (
              <Badge variant="secondary" className="flex items-center gap-1">
                <WifiOff className="w-3 h-3" />
                Static
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="filings">SEC Filings</TabsTrigger>
            <TabsTrigger value="sources">Sources</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Volume</p>
                <p className="text-lg font-semibold">{formatVolume(data.volume || 0)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Market Cap</p>
                <p className="text-lg font-semibold">{formatVolume(data.marketCap || 0)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Day Range</p>
                <p className="text-lg font-semibold">
                  {formatPrice(data.low || 0)} - {formatPrice(data.high || 0)}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Sentiment</p>
                <p className={`text-lg font-semibold capitalize ${getSentimentColor(data.marketSentiment)}`}>
                  {data.marketSentiment || 'Neutral'}
                </p>
              </div>
            </div>
            {data.newsAnalysis && (
              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-2">Latest News</h4>
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {data.newsAnalysis}
                </p>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="analysis" className="space-y-4">
            {data.fundamentalAnalysis && (
              <div>
                <h4 className="font-semibold mb-2">Fundamental Analysis</h4>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {data.fundamentalAnalysis}
                </p>
              </div>
            )}
            {data.technicalAnalysis && (
              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-2">Technical Analysis</h4>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {data.technicalAnalysis}
                </p>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="filings" className="space-y-3">
            {data.secFilings && data.secFilings.length > 0 ? (
              data.secFilings.map((filing, index) => (
                <div key={index} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <Badge variant="outline" className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {filing.type}
                    </Badge>
                    <span className="text-sm text-muted-foreground">{filing.date}</span>
                  </div>
                  <p className="text-sm mt-2">{filing.summary}</p>
                  {filing.url && (
                    <a 
                      href={filing.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline mt-1 inline-block"
                    >
                      View Filing →
                    </a>
                  )}
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No recent SEC filings available
              </p>
            )}
          </TabsContent>
          
          <TabsContent value="sources" className="space-y-4">
            <div className="space-y-2">
              {Object.entries(data.dataSource).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center py-2 border-b">
                  <span className="text-sm font-medium capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </span>
                  <Badge variant="secondary" className="text-xs">
                    {value}
                  </Badge>
                </div>
              ))}
            </div>
            {data.timestamp && (
              <p className="text-xs text-muted-foreground text-center pt-2">
                Last updated: {new Date(data.timestamp).toLocaleString()}
              </p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}