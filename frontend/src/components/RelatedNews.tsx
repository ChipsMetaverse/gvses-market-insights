import React from 'react';
import { RelatedNews as RelatedNewsType } from '../types/dashboard';

interface RelatedNewsProps {
  data: RelatedNewsType;
  onClickItem?: (newsId: string) => void;
}

export const RelatedNews: React.FC<RelatedNewsProps> = ({ data, onClickItem }) => {
  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return `${diffMinutes}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else {
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays}d ago`;
    }
  };
  
  return (
    <div className="card" data-testid="related-news">
      <div className="card-header">
        <h3 className="card-title">Related News</h3>
      </div>
      
      <div className="news-grid">
        {data.items.map((item) => (
          <div 
            key={item.id} 
            className="news-card"
            onClick={() => {
              if (onClickItem) {
                onClickItem(item.id);
              } else {
                window.open(item.url, '_blank');
              }
            }}
          >
            <img 
              src={item.image_url} 
              alt={item.title}
              className="news-card-image"
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x225?text=News';
              }}
            />
            
            <div className="news-card-content">
              <h4 className="news-card-title">{item.title}</h4>
              
              {item.description && (
                <p style={{ 
                  fontSize: '12px', 
                  color: 'var(--text-secondary)',
                  marginBottom: '8px',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}>
                  {item.description}
                </p>
              )}
              
              <div className="news-card-meta">
                <span>{item.source}</span>
                <span>{formatTimeAgo(item.published_at)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};