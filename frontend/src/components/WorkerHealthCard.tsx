import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Server, 
  Clock, 
  AlertCircle,
  CheckCircle,
  TrendingUp,
  RefreshCw,
  Database
} from 'lucide-react';
import './WorkerHealthCard.css';

interface WorkerStats {
  worker_id: string;
  status: 'active' | 'idle' | 'offline';
  last_heartbeat: string;
  jobs_completed: number;
  jobs_failed: number;
  cpu_usage?: number;
  memory_usage?: number;
  lease_count: number;
  avg_job_time_ms?: number;
}

interface DistributedStats {
  active_workers: number;
  total_workers: number;
  queue_depth: number;
  orphan_count: number;
  lease_stats: {
    active: number;
    expired: number;
    average_age_seconds: number;
  };
  workers: WorkerStats[];
  recent_orphans: Array<{
    job_id: string;
    recovered_at: string;
    original_worker: string;
  }>;
}

interface WorkerHealthCardProps {
  className?: string;
  refreshInterval?: number; // milliseconds
}

const WorkerHealthCard: React.FC<WorkerHealthCardProps> = ({
  className = '',
  refreshInterval = 5000
}) => {
  const [stats, setStats] = useState<DistributedStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [expandedWorker, setExpandedWorker] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const fetchStats = async () => {
    try {
      const response = await fetch('/distributed/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
        setError(null);
        setLastUpdate(new Date());
      } else {
        setError('Failed to fetch worker stats');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'status-active';
      case 'idle': return 'status-idle';
      case 'offline': return 'status-offline';
      default: return 'status-unknown';
    }
  };

  const getHealthStatus = () => {
    if (!stats) return 'unknown';
    const activeRatio = stats.active_workers / stats.total_workers;
    if (activeRatio >= 0.8) return 'healthy';
    if (activeRatio >= 0.5) return 'degraded';
    return 'critical';
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = (now.getTime() - date.getTime()) / 1000; // seconds
    
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
  };

  if (isLoading && !stats) {
    return (
      <div className={`worker-health-card ${className} loading`}>
        <div className="loading-spinner">
          <RefreshCw className="spin" size={24} />
        </div>
      </div>
    );
  }

  const healthStatus = getHealthStatus();

  return (
    <div className={`worker-health-card ${className} health-${healthStatus}`}>
      <div className="card-header">
        <h3>
          <Server size={20} />
          Worker Health
          <span className={`health-indicator ${healthStatus}`} />
        </h3>
        <div className="header-actions">
          <span className="last-update" title={lastUpdate.toLocaleString()}>
            Updated {formatTime(lastUpdate.toISOString())}
          </span>
          <button className="refresh-btn" onClick={fetchStats} title="Refresh">
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {error ? (
        <div className="error-state">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      ) : stats ? (
        <>
          <div className="summary-metrics">
            <div className="metric-card">
              <div className="metric-label">
                <Activity size={16} />
                Workers
              </div>
              <div className="metric-value">
                <span className="active">{stats.active_workers}</span>
                <span className="separator">/</span>
                <span className="total">{stats.total_workers}</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                <Database size={16} />
                Queue
              </div>
              <div className="metric-value">{stats.queue_depth}</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                <Clock size={16} />
                Lease Age
              </div>
              <div className="metric-value">
                {formatDuration(stats.lease_stats.average_age_seconds)}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">
                <AlertCircle size={16} />
                Orphans
              </div>
              <div className="metric-value">
                {stats.orphan_count}
              </div>
            </div>
          </div>

          <div className="workers-list">
            <h4>Worker Details</h4>
            {stats.workers.map(worker => (
              <div 
                key={worker.worker_id} 
                className={`worker-item ${getStatusColor(worker.status)}`}
                onClick={() => setExpandedWorker(
                  expandedWorker === worker.worker_id ? null : worker.worker_id
                )}
              >
                <div className="worker-header">
                  <div className="worker-id">
                    <span className={`status-dot ${worker.status}`} />
                    {worker.worker_id.slice(0, 8)}...
                  </div>
                  <div className="worker-stats">
                    <span className="stat">
                      <CheckCircle size={14} />
                      {worker.jobs_completed}
                    </span>
                    {worker.jobs_failed > 0 && (
                      <span className="stat failed">
                        <AlertCircle size={14} />
                        {worker.jobs_failed}
                      </span>
                    )}
                    <span className="heartbeat">
                      {formatTime(worker.last_heartbeat)}
                    </span>
                  </div>
                </div>

                {expandedWorker === worker.worker_id && (
                  <div className="worker-details">
                    <div className="detail-row">
                      <label>Active Leases:</label>
                      <span>{worker.lease_count}</span>
                    </div>
                    {worker.avg_job_time_ms && (
                      <div className="detail-row">
                        <label>Avg Job Time:</label>
                        <span>{worker.avg_job_time_ms}ms</span>
                      </div>
                    )}
                    {worker.cpu_usage !== undefined && (
                      <div className="detail-row">
                        <label>CPU Usage:</label>
                        <div className="usage-bar">
                          <div 
                            className="usage-fill cpu"
                            style={{ width: `${worker.cpu_usage}%` }}
                          />
                          <span>{worker.cpu_usage}%</span>
                        </div>
                      </div>
                    )}
                    {worker.memory_usage !== undefined && (
                      <div className="detail-row">
                        <label>Memory:</label>
                        <div className="usage-bar">
                          <div 
                            className="usage-fill memory"
                            style={{ width: `${worker.memory_usage}%` }}
                          />
                          <span>{worker.memory_usage}%</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {stats.recent_orphans && stats.recent_orphans.length > 0 && (
            <div className="orphans-section">
              <h4>
                Recent Orphan Recovery
                <TrendingUp size={16} />
              </h4>
              <div className="orphans-list">
                {stats.recent_orphans.slice(0, 3).map((orphan, idx) => (
                  <div key={idx} className="orphan-item">
                    <span className="job-id">{orphan.job_id.slice(0, 8)}...</span>
                    <span className="recovery-time">
                      {formatTime(orphan.recovered_at)}
                    </span>
                    <span className="original-worker">
                      from {orphan.original_worker.slice(0, 8)}...
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="lease-summary">
            <div className="lease-stat">
              <span className="label">Active Leases</span>
              <span className="value">{stats.lease_stats.active}</span>
            </div>
            <div className="lease-stat">
              <span className="label">Expired</span>
              <span className="value">{stats.lease_stats.expired}</span>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default WorkerHealthCard;