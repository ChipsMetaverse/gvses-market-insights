import React from 'react';
import './NewsModal.css';

interface NewsModalProps {
  isOpen: boolean;
  onClose: () => void;
  news: {
    title: string;
    link?: string;
    source?: string;
    published?: string;
    summary?: string;
  } | null;
}

export const NewsModal: React.FC<NewsModalProps> = ({ isOpen, onClose, news }) => {
  if (!isOpen || !news) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Recently';
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 60) {
        return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
      }
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) {
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
      }
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays < 7) {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
      }
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="news-modal-backdrop" onClick={handleBackdropClick}>
      <div className="news-modal">
        <div className="news-modal-header">
          <button className="news-modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="news-modal-content">
          <h2 className="news-modal-title">{news.title}</h2>
          
          <div className="news-modal-meta">
            {news.source && (
              <span className="news-modal-source">{news.source}</span>
            )}
            {news.published && (
              <span className="news-modal-date">• {formatDate(news.published)}</span>
            )}
          </div>
          
          <div className="news-modal-body">
            {news.summary ? (
              <p className="news-modal-summary">{news.summary}</p>
            ) : (
              <p className="news-modal-placeholder">
                Full article content is not available in the preview. 
                Click the button below to read the full article on the source website.
              </p>
            )}
          </div>
          
          <div className="news-modal-actions">
            {news.link ? (
              <a
                href={news.link}
                target="_blank"
                rel="noopener noreferrer"
                className="news-modal-link"
              >
                Read Full Article →
              </a>
            ) : (
              <span className="news-modal-no-link">External link not available</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};