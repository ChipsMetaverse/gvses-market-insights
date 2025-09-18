import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './StructuredResponse.css';

interface StructuredResponseProps {
  content: string;
  className?: string;
}

const StructuredResponse: React.FC<StructuredResponseProps> = ({ content, className = '' }) => {
  return (
    <div className={`structured-response ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Custom table styling
          table: ({ children }) => (
            <div className="table-container">
              <table className="market-data-table">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="table-header">
              {children}
            </thead>
          ),
          tbody: ({ children }) => (
            <tbody className="table-body">
              {children}
            </tbody>
          ),
          tr: ({ children }) => (
            <tr className="table-row">
              {children}
            </tr>
          ),
          th: ({ children }) => (
            <th className="table-header-cell">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="table-data-cell">
              {children}
            </td>
          ),
          // Custom heading styling
          h1: ({ children }) => (
            <h1 className="response-h1">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="response-h2">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="response-h3">
              {children}
            </h3>
          ),
          // Price highlighting
          strong: ({ children }) => {
            const text = children?.toString() || '';
            // Highlight price-like patterns
            if (text.match(/^\$[\d,]+\.?\d*$/)) {
              return <span className="price-highlight">{children}</span>;
            }
            // Highlight percentage changes
            if (text.match(/^[+-]?\d+\.?\d*%$/)) {
              const isPositive = text.startsWith('+') || (!text.startsWith('-') && !text.startsWith('0'));
              return <span className={`percentage-change ${isPositive ? 'positive' : 'negative'}`}>{children}</span>;
            }
            return <strong className="response-bold">{children}</strong>;
          },
          // List styling
          ul: ({ children }) => (
            <ul className="response-list">
              {children}
            </ul>
          ),
          li: ({ children }) => (
            <li className="response-list-item">
              {children}
            </li>
          ),
          // Horizontal rule styling
          hr: () => (
            <hr className="response-divider" />
          ),
          // Paragraph styling
          p: ({ children }) => (
            <p className="response-paragraph">
              {children}
            </p>
          ),
          // Em/italic for sources
          em: ({ children }) => (
            <em className="response-source">
              {children}
            </em>
          ),
          // Code/inline code styling
          code: ({ children }) => (
            <code className="response-code">
              {children}
            </code>
          ),
          // Blockquote styling
          blockquote: ({ children }) => (
            <blockquote className="response-quote">
              {children}
            </blockquote>
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default StructuredResponse;