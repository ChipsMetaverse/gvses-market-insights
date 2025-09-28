import React, { useState, useEffect } from 'react';
import { 
  Check, 
  X, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  MessageSquare,
  TrendingUp,
  History
} from 'lucide-react';
import './PatternReviewPanel.css';

interface PatternVerdict {
  pattern_id: string;
  verdict: 'accepted' | 'rejected' | 'deferred';
  operator_id?: string;
  notes?: string;
  symbol?: string;
  timeframe?: string;
  submitted_at: string;
}

interface Pattern {
  id: string;
  type: string;
  confidence: number;
  symbol: string;
  timeframe: string;
  status: 'pending' | 'confirmed' | 'invalidated';
  created_at: string;
  targets?: number[];
  stop_loss?: number;
}

interface PatternReviewPanelProps {
  patterns: Pattern[];
  onVerdictSubmit: (patternId: string, verdict: string, notes?: string) => void;
  className?: string;
}

const PatternReviewPanel: React.FC<PatternReviewPanelProps> = ({
  patterns,
  onVerdictSubmit,
  className = ''
}) => {
  const [expandedPattern, setExpandedPattern] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [history, setHistory] = useState<PatternVerdict[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState<string | null>(null);

  // Fetch pattern history on mount
  useEffect(() => {
    fetchPatternHistory();
  }, []);

  const fetchPatternHistory = async () => {
    try {
      const response = await fetch('/api/agent/pattern-history?limit=20');
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (error) {
      console.error('Failed to fetch pattern history:', error);
    }
  };

  const handleVerdict = async (patternId: string, verdict: 'accepted' | 'rejected' | 'deferred') => {
    setIsSubmitting(patternId);
    
    try {
      const pattern = patterns.find(p => p.id === patternId);
      const response = await fetch('/api/agent/pattern-verdict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pattern_id: patternId,
          verdict,
          notes: notes[patternId],
          symbol: pattern?.symbol,
          timeframe: pattern?.timeframe
        })
      });

      if (response.ok) {
        // Callback to parent component
        onVerdictSubmit(patternId, verdict, notes[patternId]);
        
        // Clear notes for this pattern
        setNotes(prev => {
          const newNotes = { ...prev };
          delete newNotes[patternId];
          return newNotes;
        });

        // Refresh history
        await fetchPatternHistory();
        
        // Collapse this pattern
        if (expandedPattern === patternId) {
          setExpandedPattern(null);
        }
      }
    } catch (error) {
      console.error('Failed to submit verdict:', error);
    } finally {
      setIsSubmitting(null);
    }
  };

  const pendingPatterns = patterns.filter(p => p.status === 'pending');

  return (
    <div className={`pattern-review-panel ${className}`}>
      <div className="panel-header">
        <h3>
          <TrendingUp size={20} />
          Pattern Review
          {pendingPatterns.length > 0 && (
            <span className="badge">{pendingPatterns.length}</span>
          )}
        </h3>
        <button 
          className="history-toggle"
          onClick={() => setShowHistory(!showHistory)}
        >
          <History size={18} />
          History
        </button>
      </div>

      {showHistory ? (
        <div className="pattern-history">
          <h4>Recent Decisions</h4>
          <div className="history-list">
            {history.map((entry, idx) => (
              <div key={idx} className={`history-entry verdict-${entry.verdict}`}>
                <div className="history-header">
                  <span className="pattern-id">{entry.pattern_id}</span>
                  <span className={`verdict-badge ${entry.verdict}`}>
                    {entry.verdict}
                  </span>
                </div>
                <div className="history-meta">
                  <span>{entry.symbol} · {entry.timeframe}</span>
                  <span>{new Date(entry.submitted_at).toLocaleDateString()}</span>
                </div>
                {entry.notes && (
                  <div className="history-notes">{entry.notes}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="patterns-list">
          {pendingPatterns.length === 0 ? (
            <div className="no-patterns">
              No patterns pending review
            </div>
          ) : (
            pendingPatterns.map(pattern => (
              <div key={pattern.id} className="pattern-card">
                <div 
                  className="pattern-header"
                  onClick={() => setExpandedPattern(
                    expandedPattern === pattern.id ? null : pattern.id
                  )}
                >
                  <div className="pattern-info">
                    <span className="pattern-type">{pattern.type}</span>
                    <span className="pattern-confidence">
                      {Math.round(pattern.confidence * 100)}% confidence
                    </span>
                  </div>
                  <div className="pattern-meta">
                    <span>{pattern.symbol} · {pattern.timeframe}</span>
                    {expandedPattern === pattern.id ? 
                      <ChevronUp size={16} /> : 
                      <ChevronDown size={16} />
                    }
                  </div>
                </div>

                {expandedPattern === pattern.id && (
                  <div className="pattern-details">
                    <div className="pattern-metrics">
                      {pattern.targets && pattern.targets.length > 0 && (
                        <div className="metric">
                          <label>Targets:</label>
                          <span>{pattern.targets.join(', ')}</span>
                        </div>
                      )}
                      {pattern.stop_loss && (
                        <div className="metric">
                          <label>Stop Loss:</label>
                          <span>{pattern.stop_loss}</span>
                        </div>
                      )}
                    </div>

                    <div className="notes-section">
                      <label>
                        <MessageSquare size={16} />
                        Notes (optional)
                      </label>
                      <textarea
                        placeholder="Add notes about this pattern..."
                        value={notes[pattern.id] || ''}
                        onChange={(e) => setNotes(prev => ({
                          ...prev,
                          [pattern.id]: e.target.value
                        }))}
                        rows={3}
                      />
                    </div>

                    <div className="verdict-actions">
                      <button
                        className="accept-btn"
                        onClick={() => handleVerdict(pattern.id, 'accepted')}
                        disabled={isSubmitting === pattern.id}
                      >
                        <Check size={16} />
                        Accept
                      </button>
                      <button
                        className="reject-btn"
                        onClick={() => handleVerdict(pattern.id, 'rejected')}
                        disabled={isSubmitting === pattern.id}
                      >
                        <X size={16} />
                        Reject
                      </button>
                      <button
                        className="defer-btn"
                        onClick={() => handleVerdict(pattern.id, 'deferred')}
                        disabled={isSubmitting === pattern.id}
                      >
                        <Clock size={16} />
                        Defer
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default PatternReviewPanel;