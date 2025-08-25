import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileText, Calendar, ExternalLink, Search, Loader2 } from 'lucide-react';
import { searchSECFilings } from '@/services/perplexityFinance';

export interface SECFiling {
  type: string;
  date: string;
  url: string;
  summary: string;
}

interface SECFilingsListProps {
  symbol?: string;
  filings?: SECFiling[];
  maxHeight?: string;
  onFilingClick?: (filing: SECFiling) => void;
}

export function SECFilingsList({ 
  symbol, 
  filings: propFilings, 
  maxHeight = '400px',
  onFilingClick 
}: SECFilingsListProps) {
  const [filings, setFilings] = useState<SECFiling[]>(propFilings || []);
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState<string>('all');

  // Filing type colors
  const getFilingTypeColor = (type: string) => {
    switch (type) {
      case '10-K': return 'bg-blue-600';
      case '10-Q': return 'bg-green-600';
      case '8-K': return 'bg-orange-600';
      case 'S-1': return 'bg-purple-600';
      case 'S-4': return 'bg-pink-600';
      default: return 'bg-gray-600';
    }
  };

  // Load filings if symbol is provided and no filings passed as prop
  useEffect(() => {
    if (symbol && !propFilings) {
      loadFilings();
    }
  }, [symbol]);

  const loadFilings = async () => {
    if (!symbol) return;
    
    setLoading(true);
    try {
      // Fetch multiple filing types
      const filingTypes = ['10-K', '10-Q', '8-K'];
      const results = await Promise.allSettled(
        filingTypes.map(type => searchSECFilings(symbol, type))
      );
      
      const allFilings: SECFiling[] = [];
      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          const data = result.value;
          if (data.filings && Array.isArray(data.filings)) {
            allFilings.push(...data.filings.map((f: any) => ({
              type: f.type || filingTypes[index],
              date: f.date || 'Unknown',
              url: f.url || '',
              summary: f.summary || data.keyFindings || 'No summary available'
            })));
          }
        }
      });
      
      // Sort by date (newest first)
      allFilings.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
      setFilings(allFilings.slice(0, 10)); // Keep top 10 most recent
    } catch (error) {
      console.error('Error loading SEC filings:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredFilings = selectedType === 'all' 
    ? filings 
    : filings.filter(f => f.type === selectedType);

  const uniqueTypes = Array.from(new Set(filings.map(f => f.type)));

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              SEC Filings
              {symbol && <Badge variant="secondary">{symbol}</Badge>}
            </CardTitle>
            <CardDescription>
              Recent regulatory filings and disclosures
            </CardDescription>
          </div>
          {symbol && !propFilings && (
            <Button 
              size="sm" 
              variant="outline"
              onClick={loadFilings}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Filter buttons */}
        {uniqueTypes.length > 1 && (
          <div className="flex gap-2 mb-4 flex-wrap">
            <Button
              size="sm"
              variant={selectedType === 'all' ? 'default' : 'outline'}
              onClick={() => setSelectedType('all')}
            >
              All ({filings.length})
            </Button>
            {uniqueTypes.map(type => (
              <Button
                key={type}
                size="sm"
                variant={selectedType === type ? 'default' : 'outline'}
                onClick={() => setSelectedType(type)}
              >
                {type} ({filings.filter(f => f.type === type).length})
              </Button>
            ))}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : filteredFilings.length > 0 ? (
          <ScrollArea className="w-full" style={{ height: maxHeight }}>
            <div className="space-y-3 pr-4">
              {filteredFilings.map((filing, index) => (
                <div 
                  key={index} 
                  className="border rounded-lg p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                  onClick={() => onFilingClick?.(filing)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <Badge className={`${getFilingTypeColor(filing.type)} text-white`}>
                      {filing.type}
                    </Badge>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Calendar className="w-3 h-3" />
                      {new Date(filing.date).toLocaleDateString()}
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    {filing.summary}
                  </p>
                  
                  {filing.url && (
                    <a 
                      href={filing.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
                      onClick={(e) => e.stopPropagation()}
                    >
                      View Filing
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        ) : (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">
              {symbol ? 'No SEC filings found' : 'No filings to display'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}