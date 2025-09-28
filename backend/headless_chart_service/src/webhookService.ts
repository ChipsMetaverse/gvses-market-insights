import pino from 'pino';
import fetch from 'node-fetch';
import { supabase } from './supabaseClient.js';
import type { RenderJob, JobStatus } from './types.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

export type WebhookEventType = 'job.created' | 'job.started' | 'job.completed' | 'job.failed' | 'worker.offline' | 'worker.overloaded' | 'queue.backlog' | 'jobs.orphaned';

export interface WebhookEvent {
  id?: string;
  job_id: string;
  event_type: WebhookEventType;
  webhook_url: string;
  payload: Record<string, unknown>;
  attempts?: number;
  last_attempt_at?: string;
  delivered_at?: string;
  error?: string;
  created_at?: string;
}

export interface WebhookPayload {
  event: WebhookEventType;
  job_id?: string;
  job?: {
    id: string;
    symbol: string;
    timeframe: string;
    status: JobStatus;
    created_at: number;
    updated_at: number;
    started_at?: number;
    finished_at?: number;
    duration_ms?: number;
    error?: string;
    metadata?: Record<string, unknown>;
  };
  // Worker health alert data
  worker_id?: string;
  alert_type?: 'worker_offline' | 'worker_overloaded' | 'queue_backlog' | 'orphan_jobs';
  severity?: 'low' | 'medium' | 'high' | 'critical';
  message?: string;
  data?: Record<string, unknown>;
  timestamp: string;
}

export class WebhookService {
  private readonly maxRetries = 3;
  private readonly baseDelayMs = 1000; // 1 second
  private readonly maxDelayMs = 30000; // 30 seconds
  private processingQueue = false;

  constructor() {
    // Start background processing
    this.startBackgroundProcessing();
  }

  /**
   * Trigger webhook notifications for a job lifecycle event
   */
  async triggerWebhooks(job: RenderJob, eventType: WebhookEventType): Promise<void> {
    try {
      // Extract webhook URLs from job metadata
      const webhookUrls = this.extractWebhookUrls(job);
      
      if (webhookUrls.length === 0) {
        logger.debug({ jobId: job.id, eventType }, 'No webhook URLs configured for job');
        return;
      }

      // Create webhook events for each URL
      const webhookEvents = webhookUrls.map(url => this.createWebhookEvent(job, eventType, url));
      
      // Store events in database
      await this.storeWebhookEvents(webhookEvents);
      
      logger.info(
        { jobId: job.id, eventType, webhookCount: webhookUrls.length },
        'Webhook events created and queued'
      );
    } catch (error) {
      logger.error(
        { err: error, jobId: job.id, eventType },
        'Failed to trigger webhooks'
      );
    }
  }

  /**
   * Process pending webhook events with retry logic
   */
  async processPendingWebhooks(): Promise<void> {
    if (this.processingQueue) {
      return;
    }

    this.processingQueue = true;
    
    try {
      // Get pending webhook events (not delivered and under retry limit)
      const { data: events, error } = await supabase
        .from('headless_webhook_events')
        .select('*')
        .is('delivered_at', null)
        .lt('attempts', this.maxRetries)
        .order('created_at', { ascending: true })
        .limit(50); // Process in batches

      if (error) {
        throw error;
      }

      if (!events || events.length === 0) {
        return;
      }

      logger.info({ count: events.length }, 'Processing pending webhook events');

      // Process events concurrently with limited parallelism
      const batchSize = 5;
      for (let i = 0; i < events.length; i += batchSize) {
        const batch = events.slice(i, i + batchSize);
        await Promise.allSettled(batch.map(event => this.processWebhookEvent(event)));
      }
    } catch (error) {
      logger.error({ err: error }, 'Failed to process pending webhooks');
    } finally {
      this.processingQueue = false;
    }
  }

  /**
   * Process a single webhook event
   */
  private async processWebhookEvent(event: WebhookEvent): Promise<void> {
    const attempt = (event.attempts || 0) + 1;
    
    try {
      logger.debug(
        { eventId: event.id, webhookUrl: event.webhook_url, attempt },
        'Processing webhook event'
      );

      // Calculate delay for exponential backoff
      if (attempt > 1) {
        const delay = Math.min(
          this.baseDelayMs * Math.pow(2, attempt - 2),
          this.maxDelayMs
        );
        await this.sleep(delay);
      }

      // Send webhook request
      const response = await fetch(event.webhook_url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'HeadlessChartService/0.1.0',
          'X-Webhook-Event': event.event_type,
          'X-Webhook-Delivery': event.id || 'unknown',
        },
        body: JSON.stringify(event.payload),
        // Using manual timeout with AbortController for node-fetch v3 compatibility
        signal: (() => {
          const controller = new AbortController();
          setTimeout(() => controller.abort(), 10000);
          return controller.signal;
        })()
      });

      if (response.ok) {
        // Success - mark as delivered
        await this.markWebhookDelivered(event.id!);
        logger.info(
          { eventId: event.id, webhookUrl: event.webhook_url, statusCode: response.status },
          'Webhook delivered successfully'
        );
      } else {
        // HTTP error - record attempt
        const errorText = await response.text().catch(() => 'Unknown error');
        const errorMessage = `HTTP ${response.status}: ${errorText}`;
        await this.recordWebhookAttempt(event.id!, errorMessage);
        
        logger.warn(
          { 
            eventId: event.id, 
            webhookUrl: event.webhook_url, 
            statusCode: response.status,
            attempt,
            maxRetries: this.maxRetries
          },
          'Webhook delivery failed'
        );
      }
    } catch (error) {
      // Network or other error - record attempt
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      await this.recordWebhookAttempt(event.id!, errorMessage);
      
      logger.error(
        { 
          err: error, 
          eventId: event.id, 
          webhookUrl: event.webhook_url, 
          attempt,
          maxRetries: this.maxRetries
        },
        'Webhook request failed'
      );
    }
  }

  /**
   * Extract webhook URLs from job metadata
   */
  private extractWebhookUrls(job: RenderJob): string[] {
    const urls: string[] = [];
    
    if (!job.metadata) {
      return urls;
    }

    // Support multiple webhook URL formats in metadata
    if (job.metadata.webhook_url && typeof job.metadata.webhook_url === 'string') {
      urls.push(job.metadata.webhook_url);
    }
    
    if (job.metadata.webhook_urls && Array.isArray(job.metadata.webhook_urls)) {
      job.metadata.webhook_urls.forEach(url => {
        if (typeof url === 'string') {
          urls.push(url);
        }
      });
    }

    // Filter out invalid URLs
    return urls.filter(url => this.isValidWebhookUrl(url));
  }

  /**
   * Validate webhook URL
   */
  private isValidWebhookUrl(url: string): boolean {
    try {
      const parsed = new URL(url);
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
      return false;
    }
  }

  /**
   * Create webhook event object
   */
  private createWebhookEvent(job: RenderJob, eventType: WebhookEventType, webhookUrl: string): WebhookEvent {
    const payload: WebhookPayload = {
      event: eventType,
      job_id: job.id,
      job: {
        id: job.id,
        symbol: job.symbol,
        timeframe: job.timeframe,
        status: job.status,
        created_at: job.createdAt,
        updated_at: job.updatedAt,
        started_at: job.startedAt,
        finished_at: job.finishedAt,
        duration_ms: job.durationMs,
        error: job.error,
        metadata: job.metadata,
      },
      timestamp: new Date().toISOString(),
    };

    return {
      job_id: job.id,
      event_type: eventType,
      webhook_url: webhookUrl,
      payload: payload as unknown as Record<string, unknown>,
      attempts: 0,
    };
  }

  /**
   * Store webhook events in database
   */
  private async storeWebhookEvents(events: WebhookEvent[]): Promise<void> {
    const { error } = await supabase
      .from('headless_webhook_events')
      .insert(events);

    if (error) {
      logger.error({ err: error, count: events.length }, 'Failed to store webhook events');
      throw error;
    }
  }

  /**
   * Mark webhook as delivered
   */
  private async markWebhookDelivered(eventId: string): Promise<void> {
    // First get current attempts count
    const { data: currentEvent, error: fetchError } = await supabase
      .from('headless_webhook_events')
      .select('attempts')
      .eq('id', eventId)
      .single();

    if (fetchError) {
      logger.error({ err: fetchError, eventId }, 'Failed to fetch current webhook event');
      return;
    }

    const newAttempts = (currentEvent?.attempts || 0) + 1;

    const { error } = await supabase
      .from('headless_webhook_events')
      .update({ 
        delivered_at: new Date().toISOString(),
        last_attempt_at: new Date().toISOString(),
        attempts: newAttempts
      })
      .eq('id', eventId);

    if (error) {
      logger.error({ err: error, eventId }, 'Failed to mark webhook as delivered');
    }
  }

  /**
   * Record webhook attempt with error
   */
  private async recordWebhookAttempt(eventId: string, errorMessage: string): Promise<void> {
    // First get current attempts count
    const { data: currentEvent, error: fetchError } = await supabase
      .from('headless_webhook_events')
      .select('attempts')
      .eq('id', eventId)
      .single();

    if (fetchError) {
      logger.error({ err: fetchError, eventId }, 'Failed to fetch current webhook event');
      return;
    }

    const newAttempts = (currentEvent?.attempts || 0) + 1;

    const { error } = await supabase
      .from('headless_webhook_events')
      .update({
        attempts: newAttempts,
        last_attempt_at: new Date().toISOString(),
        error: errorMessage,
      })
      .eq('id', eventId);

    if (error) {
      logger.error({ err: error, eventId }, 'Failed to record webhook attempt');
    }
  }

  /**
   * Start background processing of webhook queue
   */
  private startBackgroundProcessing(): void {
    // Process webhooks every 30 seconds
    const intervalMs = 30000;
    
    setInterval(() => {
      this.processPendingWebhooks().catch(error => {
        logger.error({ err: error }, 'Background webhook processing failed');
      });
    }, intervalMs);

    logger.info({ intervalMs }, 'Started background webhook processing');
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get webhook statistics
   */
  async getStats(): Promise<{
    pending: number;
    delivered: number;
    failed: number;
    total: number;
  }> {
    try {
      const { data: stats, error } = await supabase
        .from('headless_webhook_events')
        .select('delivered_at, attempts')
        .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()); // Last 24 hours

      if (error) {
        throw error;
      }

      const total = stats?.length || 0;
      const delivered = stats?.filter(s => s.delivered_at).length || 0;
      const failed = stats?.filter(s => !s.delivered_at && s.attempts >= this.maxRetries).length || 0;
      const pending = total - delivered - failed;

      return { pending, delivered, failed, total };
    } catch (error) {
      logger.error({ err: error }, 'Failed to get webhook stats');
      return { pending: 0, delivered: 0, failed: 0, total: 0 };
    }
  }

  /**
   * Trigger worker health alerts
   */
  async triggerWorkerOfflineAlert(workerId: string, lastHeartbeat: Date, webhookUrls: string[]): Promise<void> {
    const timeSinceHeartbeat = Date.now() - lastHeartbeat.getTime();
    const severity = timeSinceHeartbeat > 300000 ? 'critical' : 'high'; // 5+ minutes is critical
    
    await this.triggerHealthAlert({
      event: 'worker.offline',
      worker_id: workerId,
      alert_type: 'worker_offline',
      severity,
      message: `Worker ${workerId} has been offline for ${Math.round(timeSinceHeartbeat / 1000)}s`,
      data: {
        worker_id: workerId,
        last_heartbeat: lastHeartbeat.toISOString(),
        offline_duration_ms: timeSinceHeartbeat
      },
      timestamp: new Date().toISOString()
    }, webhookUrls);
  }

  async triggerWorkerOverloadedAlert(workerId: string, metrics: any, webhookUrls: string[]): Promise<void> {
    await this.triggerHealthAlert({
      event: 'worker.overloaded',
      worker_id: workerId,
      alert_type: 'worker_overloaded',
      severity: 'medium',
      message: `Worker ${workerId} is overloaded (CPU: ${metrics.cpu_usage}%, Memory: ${metrics.memory_usage}%)`,
      data: {
        worker_id: workerId,
        cpu_usage: metrics.cpu_usage,
        memory_usage: metrics.memory_usage,
        active_jobs: metrics.active_jobs
      },
      timestamp: new Date().toISOString()
    }, webhookUrls);
  }

  async triggerQueueBacklogAlert(queueSize: number, averageWaitTime: number, webhookUrls: string[]): Promise<void> {
    const severity = queueSize > 100 ? 'critical' : queueSize > 50 ? 'high' : 'medium';
    
    await this.triggerHealthAlert({
      event: 'queue.backlog',
      alert_type: 'queue_backlog',
      severity,
      message: `Job queue backlog detected: ${queueSize} jobs, avg wait ${Math.round(averageWaitTime)}ms`,
      data: {
        queue_size: queueSize,
        average_wait_time_ms: averageWaitTime,
        threshold_exceeded: queueSize > 25
      },
      timestamp: new Date().toISOString()
    }, webhookUrls);
  }

  async triggerOrphanJobsAlert(orphanCount: number, recoveredCount: number, webhookUrls: string[]): Promise<void> {
    await this.triggerHealthAlert({
      event: 'jobs.orphaned',
      alert_type: 'orphan_jobs',
      severity: orphanCount > 10 ? 'high' : 'medium',
      message: `${orphanCount} orphan jobs detected, ${recoveredCount} recovered`,
      data: {
        orphan_jobs_count: orphanCount,
        recovered_jobs_count: recoveredCount,
        recovery_rate: recoveredCount / Math.max(orphanCount, 1)
      },
      timestamp: new Date().toISOString()
    }, webhookUrls);
  }

  /**
   * Internal method to trigger health alerts
   */
  private async triggerHealthAlert(payload: WebhookPayload, webhookUrls: string[]): Promise<void> {
    try {
      if (webhookUrls.length === 0) {
        logger.debug({ alertType: payload.alert_type }, 'No webhook URLs configured for health alert');
        return;
      }

      // Create webhook events for each URL
      const webhookEvents = webhookUrls.map(url => ({
        job_id: payload.job_id || 'health-alert',
        event_type: payload.event!,
        webhook_url: url,
        payload: payload as unknown as Record<string, unknown>,
        attempts: 0,
      }));
      
      // Store events in database
      await this.storeWebhookEvents(webhookEvents);
      
      logger.info(
        { alertType: payload.alert_type, severity: payload.severity, webhookCount: webhookUrls.length },
        'Health alert webhook events created and queued'
      );
    } catch (error) {
      logger.error(
        { err: error, alertType: payload.alert_type },
        'Failed to trigger health alert webhooks'
      );
    }
  }

  /**
   * Clean up old webhook events
   */
  async cleanupOldEvents(olderThanDays: number = 7): Promise<number> {
    try {
      const cutoffDate = new Date(Date.now() - olderThanDays * 24 * 60 * 60 * 1000).toISOString();
      
      const { count, error } = await supabase
        .from('headless_webhook_events')
        .delete()
        .lt('created_at', cutoffDate);

      if (error) {
        throw error;
      }

      const deletedCount = count || 0;
      
      if (deletedCount > 0) {
        logger.info({ deletedCount, olderThanDays }, 'Cleaned up old webhook events');
      }

      return deletedCount;
    } catch (error) {
      logger.error({ err: error, olderThanDays }, 'Failed to cleanup old webhook events');
      return 0;
    }
  }
}

// Export singleton instance
export const webhookService = new WebhookService();