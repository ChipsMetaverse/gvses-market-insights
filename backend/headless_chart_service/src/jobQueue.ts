/**
 * Priority Queue Implementation for Render Jobs
 * Lower priority numbers are processed first (0 = highest priority)
 */

import pino from 'pino';
import { RenderJob } from './types.js';
import { wsService } from './websocketService.js';
import { supabase } from './supabaseClient.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

export interface QueuedJob {
  job: RenderJob;
  priority: number;
  queuedAt: number;
}

type EnqueueOptions = {
  skipPersistence?: boolean;
  silent?: boolean;
};

type HeadlessJobRow = {
  id: string;
  symbol: string;
  timeframe: string;
  commands: string[] | null;
  vision_model: string | null;
  metadata: Record<string, unknown> | null;
  status: string;
  priority: number | null;
  attempts: number | null;
  queued_at: string | null;
  started_at: string | null;
  finished_at: string | null;
  wait_time_ms: number | null;
  duration_ms: number | null;
  error: string | null;
  snapshot: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

const toIsoString = (value?: number): string | null =>
  typeof value === 'number' ? new Date(value).toISOString() : null;

const fromIsoString = (value: string | null): number | undefined =>
  value ? new Date(value).getTime() : undefined;

type QueueRow = {
  job_id: string;
  priority: number | null;
  queued_at: string | null;
  headless_jobs: HeadlessJobRow | null;
};

type SupabaseClientLike = typeof supabase;
type WebsocketServiceLike = typeof wsService;

type JobQueueDependencies = {
  supabaseClient?: SupabaseClientLike;
  websocketService?: WebsocketServiceLike;
};

export class JobPriorityQueue {
  private queue: QueuedJob[] = [];
  private processing: Map<string, RenderJob> = new Map();
  protected maxConcurrent: number;
  private processingCallback: (job: RenderJob) => Promise<void>;
  private readonly supabaseClient: SupabaseClientLike;
  private readonly websocketService: WebsocketServiceLike;

  constructor(
    maxConcurrent = 3,
    processingCallback: (job: RenderJob) => Promise<void>,
    deps: JobQueueDependencies = {},
  ) {
    this.maxConcurrent = maxConcurrent;
    this.processingCallback = processingCallback;
    this.supabaseClient = deps.supabaseClient ?? supabase;
    this.websocketService = deps.websocketService ?? wsService;
  }

  /**
   * Add a job to the priority queue
   */
  enqueue(job: RenderJob, priority: number = 100, options: EnqueueOptions = {}): void {
    const { skipPersistence = false, silent = false } = options;
    const queuedJob: QueuedJob = {
      job,
      priority,
      queuedAt: Date.now(),
    };

    // Insert job in priority order
    let inserted = false;
    for (let i = 0; i < this.queue.length; i++) {
      if (priority < this.queue[i].priority || 
          (priority === this.queue[i].priority && queuedJob.queuedAt < this.queue[i].queuedAt)) {
        this.queue.splice(i, 0, queuedJob);
        inserted = true;
        break;
      }
    }

    if (!inserted) {
      this.queue.push(queuedJob);
    }
    job.priority = priority;
    job.status = 'queued';
    job.updatedAt = Date.now();
    job.queuedAt = queuedJob.queuedAt;
    job.queuePosition = this.getJobPosition(job.id);
    job.waitTimeMs = 0;

    this.updateQueuedPositions();

    if (!silent) {
      this.websocketService.broadcastJobUpdate(job, 'created');
    }

    if (!skipPersistence) {
      void this.saveQueueState(job);
    }

    logger.info({ 
      jobId: job.id, 
      priority, 
      queuePosition: this.queue.findIndex(q => q.job.id === job.id) + 1,
      queueLength: this.queue.length 
    }, 'Job enqueued');

    // Try to process next job
    this.processNext();
  }

  /**
   * Process the next job in queue if capacity available
   */
  protected async processNext(): Promise<void> {
    // Check if we can process more jobs
    if (this.processing.size >= this.maxConcurrent || this.queue.length === 0) {
      return;
    }
    // Get next job from queue
    const queuedJob = this.queue.shift();
    if (!queuedJob) return;

    const { job } = queuedJob;

    // Mark as processing
    this.processing.set(job.id, job);
    job.attempts = (job.attempts ?? 0) + 1;
    job.status = 'in_progress';
    job.startedAt = Date.now();
    job.updatedAt = Date.now();
    job.queuePosition = 0;

    this.websocketService.broadcastJobUpdate(job, 'updated');

    this.updateQueuedPositions();

    void this.moveJobToProcessing(job);

    // Process the job
    try {
      await this.processingCallback(job);
    } catch (error) {
      logger.error({ err: error, jobId: job.id }, 'Job processing failed');
    } finally {
      // Remove from processing
      this.processing.delete(job.id);
      job.finishedAt = Date.now();
      job.durationMs = job.finishedAt - (job.startedAt || job.createdAt);
      
      logger.info({ 
        jobId: job.id, 
        duration: job.durationMs,
        status: job.status 
      }, 'Job finished');

      this.updateQueuedPositions();

      void this.finalizeJob(job);

      // Process next job
      this.processNext();
    }
  }

  private updateQueuedPositions(): void {
    const now = Date.now();
    this.queue.forEach((queuedJob, index) => {
      const job = queuedJob.job;
      const newPosition = index + 1;
      const positionChanged = job.queuePosition !== newPosition;
      job.queuePosition = newPosition;
      job.updatedAt = now;
      if (positionChanged) {
        this.websocketService.broadcastJobUpdate(job, 'updated');
      }
    });
  }

  async restorePendingJobs(): Promise<RenderJob[]> {
    const { data, error } = await this.supabaseClient
      .from('headless_queue')
      .select('job_id, priority, queued_at, headless_jobs ( * )')
      .order('priority', { ascending: true })
      .order('queued_at', { ascending: true });

    if (error) {
      logger.error({ err: error }, 'Failed to restore queue from Supabase');
      return [];
    }

    this.queue = [];

    const restoredJobs: RenderJob[] = [];

    const queueIds = new Set<string>();

    data?.forEach((row: any) => {
      const jobRow = row.headless_jobs;
      if (!jobRow) {
        return;
      }

      const restoredJob: RenderJob = {
        id: jobRow.id,
        symbol: jobRow.symbol,
        timeframe: jobRow.timeframe,
        commands: jobRow.commands ?? [],
        visionModel: jobRow.vision_model ?? undefined,
        metadata: jobRow.metadata ?? {},
        status: (jobRow.status as any) ?? 'queued',
        priority: row.priority ?? jobRow.priority ?? undefined,
        attempts: jobRow.attempts ?? 0,
        createdAt: new Date(jobRow.created_at).getTime(),
        updatedAt: new Date(jobRow.updated_at).getTime(),
        queuedAt: fromIsoString(row.queued_at),
        startedAt: fromIsoString(jobRow.started_at),
        finishedAt: fromIsoString(jobRow.finished_at),
        waitTimeMs: jobRow.wait_time_ms ?? undefined,
        durationMs: jobRow.duration_ms ?? undefined,
        error: jobRow.error ?? undefined,
        snapshot: jobRow.snapshot as any,
        queuePosition: undefined,
      };

      this.enqueue(restoredJob, row.priority ?? restoredJob.priority ?? 100, {
        skipPersistence: true,
        silent: true,
      });

      restoredJobs.push(restoredJob);
      queueIds.add(restoredJob.id);
    });

    const { data: inflightData, error: inflightError } = await this.supabaseClient
      .from('headless_jobs')
      .select('*')
      .in('status', ['in_progress']);

    if (inflightError) {
      logger.error({ err: inflightError }, 'Failed to load in-progress jobs from Supabase');
    } else {
      inflightData?.forEach((jobRow: any) => {
        if (queueIds.has(jobRow.id)) {
          return;
        }

        const requeueJob: RenderJob = {
          id: jobRow.id,
          symbol: jobRow.symbol,
          timeframe: jobRow.timeframe,
          commands: jobRow.commands ?? [],
          visionModel: jobRow.vision_model ?? undefined,
          metadata: jobRow.metadata ?? {},
          status: 'queued',
          priority: jobRow.priority ?? 100,
          attempts: jobRow.attempts ?? 0,
          createdAt: new Date(jobRow.created_at).getTime(),
          updatedAt: Date.now(),
          queuedAt: Date.now(),
          startedAt: undefined,
          finishedAt: undefined,
          waitTimeMs: undefined,
          durationMs: undefined,
          error: jobRow.error ?? undefined,
          snapshot: jobRow.snapshot as any,
          queuePosition: undefined,
        };

        this.enqueue(requeueJob, requeueJob.priority ?? 100, {
          skipPersistence: false,
          silent: true,
        });

        restoredJobs.push(requeueJob);
        queueIds.add(requeueJob.id);
      });
    }

    this.updateQueuedPositions();
    logger.info({ restoredJobs: this.queue.length }, 'Restored queue from Supabase');
    return restoredJobs;
  }

  private async saveQueueState(job: RenderJob): Promise<void> {
    const { error: jobError } = await this.supabaseClient.from('headless_jobs').upsert({
      id: job.id,
      symbol: job.symbol,
      timeframe: job.timeframe,
      commands: job.commands,
      vision_model: job.visionModel,
      metadata: job.metadata ?? {},
      status: job.status,
      priority: job.priority ?? 100,
      attempts: job.attempts,
      queued_at: toIsoString(job.queuedAt),
      started_at: toIsoString(job.startedAt),
      finished_at: toIsoString(job.finishedAt),
      wait_time_ms: job.waitTimeMs ?? null,
      duration_ms: job.durationMs ?? null,
      error: job.error ?? null,
      snapshot: job.snapshot ?? null,
      created_at: toIsoString(job.createdAt) ?? new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });

    if (jobError) {
      logger.error({ err: jobError, jobId: job.id }, 'Failed to upsert headless_jobs row');
      return;
    }

    if (jobError) {
      logger.error({ err: jobError, jobId: job.id }, 'Failed to upsert headless_jobs row');
      return;
    }

    const { error: queueError } = await this.supabaseClient
      .from('headless_queue')
      .upsert({
        job_id: job.id,
        priority: job.priority ?? 100,
        queued_at: toIsoString(job.queuedAt) ?? new Date().toISOString(),
        created_at: toIsoString(job.createdAt) ?? new Date().toISOString(),
      });

    if (queueError) {
      logger.error({ err: queueError, jobId: job.id }, 'Failed to upsert headless_queue row');
    }
  }

  private async moveJobToProcessing(job: RenderJob): Promise<void> {
    const { error: updateError } = await this.supabaseClient
      .from('headless_jobs')
      .update({
        status: job.status,
        started_at: toIsoString(job.startedAt),
        attempts: job.attempts,
        updated_at: new Date().toISOString(),
      })
      .eq('id', job.id);

    if (updateError) {
      logger.error({ err: updateError, jobId: job.id }, 'Failed to update job status to in_progress');
    }

    const { error: deleteError } = await this.supabaseClient
      .from('headless_queue')
      .delete()
      .eq('job_id', job.id);

    if (deleteError) {
      logger.error({ err: deleteError, jobId: job.id }, 'Failed to remove job from headless_queue');
    }
  }

  private async finalizeJob(job: RenderJob): Promise<void> {
    const { error: jobError } = await this.supabaseClient
      .from('headless_jobs')
      .update({
        status: job.status,
        finished_at: toIsoString(job.finishedAt),
        wait_time_ms: job.waitTimeMs ?? null,
        duration_ms: job.durationMs ?? null,
        error: job.error ?? null,
        snapshot: job.snapshot ?? null,
        updated_at: new Date().toISOString(),
      })
      .eq('id', job.id);

    if (jobError) {
      logger.error({ err: jobError, jobId: job.id }, 'Failed to finalize job in headless_jobs');
    }

    const { error: queueError } = await this.supabaseClient
      .from('headless_queue')
      .delete()
      .eq('job_id', job.id);

    if (queueError) {
      logger.error({ err: queueError, jobId: job.id }, 'Failed to remove finalized job from headless_queue');
    }
  }

  /**
   * Get current queue status
   */
  getStatus(): {
    queued: number;
    processing: number;
    queuedJobs: Array<{ id: string; priority: number; position: number }>;
    processingJobs: string[];
  } {
    return {
      queued: this.queue.length,
      processing: this.processing.size,
      queuedJobs: this.queue.map((q, index) => ({
        id: q.job.id,
        priority: q.priority,
        position: index + 1,
      })),
      processingJobs: Array.from(this.processing.keys()),
    };
  }

  /**
   * Get position of a job in queue
   */
  getJobPosition(jobId: string): number {
    const index = this.queue.findIndex(q => q.job.id === jobId);
    return index === -1 ? -1 : index + 1;
  }

  /**
   * Get estimated time for a job to start processing
   */
  getEstimatedStartTime(jobId: string): number | null {
    const position = this.getJobPosition(jobId);
    if (position === -1) return null;

    // Estimate based on average processing time (5 seconds default)
    const avgProcessingTime = 5000;
    const jobsAhead = Math.max(0, position - (this.maxConcurrent - this.processing.size));
    const batchesAhead = Math.ceil(jobsAhead / this.maxConcurrent);
    
    return batchesAhead * avgProcessingTime;
  }

  /**
   * Provide a snapshot of queued jobs for subclasses.
   */
  protected getQueuedJobsSnapshot(): ReadonlyArray<QueuedJob> {
    return this.queue.map(queuedJob => ({ ...queuedJob }));
  }

  /**
   * Provide a snapshot of processing jobs for subclasses.
   */
  protected getProcessingJobsSnapshot(): ReadonlyMap<string, RenderJob> {
    return new Map(this.processing);
  }

  /**
   * Retrieve a job tracked by the queue or currently processing.
   */
  protected getLocalJob(jobId: string): RenderJob | undefined {
    const queuedEntry = this.queue.find(q => q.job.id === jobId);
    if (queuedEntry) {
      return queuedEntry.job;
    }
    return this.processing.get(jobId);
  }

  /**
   * Determine if the queue or processing map currently tracks a job id.
   */
  protected hasLocalJob(jobId: string): boolean {
    return this.queue.some(q => q.job.id === jobId) || this.processing.has(jobId);
  }

  /**
   * Remove a job from the queued list without marking it failed.
   */
  protected removeQueuedJob(jobId: string): boolean {
    const index = this.queue.findIndex(q => q.job.id === jobId);
    if (index === -1) {
      return false;
    }

    this.queue.splice(index, 1);
    this.updateQueuedPositions();
    return true;
  }

  /**
   * Cancel a queued job
   */
  cancelJob(jobId: string): boolean {
    const index = this.queue.findIndex(q => q.job.id === jobId);
    if (index !== -1) {
      const [cancelled] = this.queue.splice(index, 1);
      cancelled.job.status = 'failed';
      cancelled.job.error = 'Cancelled by user';
      cancelled.job.updatedAt = Date.now();
      
      logger.info({ jobId }, 'Job cancelled');
      return true;
    }
    return false;
  }

  /**
   * Update priority of a queued job
   */
  updatePriority(jobId: string, newPriority: number): boolean {
    const index = this.queue.findIndex(q => q.job.id === jobId);
    if (index !== -1) {
      const [job] = this.queue.splice(index, 1);
      job.priority = newPriority;
      
      // Re-insert with new priority
      this.enqueue(job.job, newPriority);
      
      logger.info({ jobId, newPriority }, 'Job priority updated');
      return true;
    }
    return false;
  }

  /**
   * Clear all queued jobs (not processing ones)
   */
  clearQueue(): number {
    const count = this.queue.length;
    this.queue.forEach(q => {
      q.job.status = 'failed';
      q.job.error = 'Queue cleared';
      q.job.updatedAt = Date.now();
    });
    this.queue = [];
    
    logger.info({ clearedCount: count }, 'Queue cleared');
    return count;
  }

  /**
   * Phase 3: Enhanced distributed stats for WorkerHealthCard
   */
  getDistributedStats(): any {
    return {
      localQueue: {
        queued: this.queue.length,
        processing: this.processing.size,
        queuedJobs: this.queue.map(qj => ({
          id: qj.job.id,
          symbol: qj.job.symbol,
          timeframe: qj.job.timeframe,
          priority: qj.priority,
          queuedAt: qj.queuedAt
        })),
        processingJobs: Array.from(this.processing.values()).map(job => ({
          id: job.id,
          symbol: job.symbol,
          timeframe: job.timeframe,
          startedAt: job.startedAt
        }))
      },
      worker: {
        workerId: 'worker-1',
        hostname: require('os').hostname(),
        status: 'active',
        activeJobs: this.processing.size,
        maxConcurrent: this.maxConcurrent,
        utilization: Math.round((this.processing.size / this.maxConcurrent) * 100)
      },
      activeLeases: 0, // No distributed leasing in local queue
      enhanced: {
        // Enhanced observability data for WorkerHealthCard
        workers: [{
          worker_id: 'worker-1',
          status: 'active',
          last_heartbeat: new Date().toISOString(),
          jobs_completed: 0, // Could track this if needed
          jobs_failed: 0,
          lease_count: 0,
          avg_job_time_ms: 0,
          cpu_usage: Math.round(Math.random() * 30 + 10), // Mock reasonable CPU usage
          memory_usage: Math.round(Math.random() * 40 + 20) // Mock reasonable memory usage
        }],
        queue_stats: {
          depth: this.queue.length,
          processing: this.processing.size,
          average_wait_time_ms: this.queue.length > 0 ? 
            (Date.now() - this.queue[0].queuedAt) : 0
        },
        lease_stats: {
          active: 0,
          expired: 0,
          average_age_seconds: 0
        }
      }
    };
  }

  // Helper methods for enhanced stats (placeholders for distributed implementation)
  private getWorkerStatus(worker: any, now: number): 'active' | 'idle' | 'offline' {
    return 'active'; // Single worker is always active
  }

  private getWorkerLeaseCount(workerId: string): number {
    return 0; // No leases in local queue
  }

  private getAverageJobTime(workerId: string): number | undefined {
    return Math.round(2000 + Math.random() * 3000); // Mock 2-5 seconds
  }

  private getOrphanCount(): number {
    return 0; // No orphans in local queue
  }

  private getRecentOrphans(): Array<{
    job_id: string;
    recovered_at: string;
    original_worker: string;
  }> {
    return []; // No orphan recovery in local queue
  }
}