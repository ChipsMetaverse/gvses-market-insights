import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, ExternalLink, Newspaper } from 'lucide-react';
import { marketDataService } from '../../services/marketDataService';

interface MarketNewsFeedWidgetProps {
  symbol?: string;
  onClose?: () => void;
  onAction?: (action: WidgetAction) => void;
}

type NewsSource = 'all' | 'cnbc' | 'yahoo';

type WidgetAction =
  | { type: 'news.refresh' }
  | { type: 'news.setSource'; payload: { value: NewsSource } }
  | { type: 'browser.openUrl'; payload: { url: string } };

interface NewsArticle {
  title: string;
  url: string;
  source: string;
  publishedAt: string;
  snippet?: string;
  thumbnail?: string;
}

export function MarketNewsFeedWidget({ symbol = 'TSLA', onClose, onAction }: MarketNewsFeedWidgetProps) {
  const [selectedSource, setSelectedSource] = useState<NewsSource>('all');
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNews = useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!opts?.silent) {
        setIsLoading(true);
      }
      setError(null);

      try {
        const response = await marketDataService.getStockNews(symbol);

        // Transform API response to NewsArticle format
        const newsArticles: NewsArticle[] = response.articles?.map((article: any) => ({
          title: article.headline || article.title,
          url: article.url,
          source: article.source || 'Unknown',
          publishedAt: article.datetime || article.created_at,
          snippet: article.summary,
          thumbnail: article.images?.[0]?.url,
        })) || [];

        // Filter by source if not 'all'
        const filteredArticles =
          selectedSource === 'all'
            ? newsArticles
            : newsArticles.filter((article) => {
                const source = article.source.toLowerCase();
                if (selectedSource === 'cnbc') {
                  return source.includes('cnbc');
                } else if (selectedSource === 'yahoo') {
                  return source.includes('yahoo') || source.includes('finance');
                }
                return true;
              });

        setArticles(filteredArticles);

        // Notify parent of refresh action
        onAction?.({ type: 'news.refresh' });
      } catch (err) {
        console.error('Failed to load news', err);
        setError('Unable to load market news. Please try again.');
      } finally {
        setIsLoading(false);
      }
    },
    [symbol, selectedSource, onAction]
  );

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  const handleSourceChange = (source: NewsSource) => {
    setSelectedSource(source);
    onAction?.({
      type: 'news.setSource',
      payload: { value: source },
    });
  };

  const handleArticleClick = (url: string) => {
    onAction?.({
      type: 'browser.openUrl',
      payload: { url },
    });
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  const handleRefresh = () => {
    fetchNews({ silent: true });
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    return `${diffDays}d ago`;
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center gap-3 p-6 border-b">
          <Newspaper className="w-6 h-6 text-blue-600" />
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-gray-900">Market News Feed</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-1 rounded">
                {symbol}
              </span>
              <span className="text-sm text-gray-500">Live market news & analysis</span>
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
            aria-label="Refresh news"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Source Filters */}
        <div className="px-6 py-4 border-b bg-gray-50">
          <div className="flex gap-2">
            <button
              onClick={() => handleSourceChange('all')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedSource === 'all'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              All Sources
            </button>
            <button
              onClick={() => handleSourceChange('cnbc')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedSource === 'cnbc'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              CNBC
            </button>
            <button
              onClick={() => handleSourceChange('yahoo')}
              className={`px-4 py-2 text-sm font-medium rounded-full transition-all ${
                selectedSource === 'yahoo'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              Yahoo Finance
            </button>
          </div>
        </div>

        {/* Articles List */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="m-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {isLoading && !error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mb-4" />
              <p className="text-sm text-gray-600">Loading market news…</p>
            </div>
          ) : articles.length === 0 ? (
            <div className="text-center py-16">
              <Newspaper className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-sm text-gray-600">
                No news articles available for {symbol}
                {selectedSource !== 'all' && ` from ${selectedSource.toUpperCase()}`}.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {articles.map((article, index) => (
                <button
                  key={index}
                  onClick={() => handleArticleClick(article.url)}
                  className="w-full p-6 text-left hover:bg-gray-50 transition-colors group"
                >
                  <div className="flex gap-4">
                    {/* Thumbnail */}
                    {article.thumbnail && (
                      <div className="flex-shrink-0">
                        <img
                          src={article.thumbnail}
                          alt=""
                          className="w-24 h-24 object-cover rounded-lg"
                        />
                      </div>
                    )}

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {/* Title */}
                      <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
                        {article.title}
                      </h4>

                      {/* Snippet */}
                      {article.snippet && (
                        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{article.snippet}</p>
                      )}

                      {/* Meta */}
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="font-medium text-blue-600">{article.source}</span>
                        <span>•</span>
                        <span>{formatTimeAgo(article.publishedAt)}</span>
                        <ExternalLink className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t bg-gray-50">
          <p className="text-xs text-gray-600 text-center">
            {articles.length} {articles.length === 1 ? 'article' : 'articles'} •{' '}
            {selectedSource === 'all' ? 'All sources' : selectedSource.toUpperCase()}
          </p>
        </div>
      </div>
    </div>
  );
}
