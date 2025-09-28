import 'dotenv/config';

import express, { Request, Response } from 'express';
import pino from 'pino';
import pinoHttp from 'pino-http';
import { chromium, Browser } from 'playwright';
import { randomUUID } from 'crypto';
import fetch from 'node-fetch';
import type { Server } from 'http';

import {
  RenderRequest,
  RenderResponse,
  RenderJob,
  SnapshotResult,
} from './types.js';
import { CommandValidator } from './commandValidator.js';
import { wsService } from './websocketService.js';
import { DistributedQueue } from './distributedQueue.js';
import { workerService } from './workerService.js';
import { supabase } from './supabaseClient.js';
import { webhookService } from './webhookService.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

type HeadlessJobMetricsRow = {
  pending_jobs: number | null;
  in_progress_jobs: number | null;
  succeeded_jobs: number | null;
  failed_jobs: number | null;
  avg_wait_ms: number | null;
  avg_duration_ms: number | null;
  captured_at: string;
};

async function bootstrapQueueState(): Promise<void> {
  try {
    const restoredJobs = await jobQueue.restorePendingJobs();
    restoredJobs.forEach((job) => {
      jobs.set(job.id, job);
    });

    const queueStatus = jobQueue.getStatus();
    metrics.totalJobs = jobs.size;
    metrics.queuedJobs = queueStatus.queued;
    metrics.activeJobs = queueStatus.processing;
    metrics.startedJobs = queueStatus.processing;
    metrics.lastUpdated = Date.now();

    const { data: summary, error: summaryError } = await supabase
      .from('headless_job_metrics')
      .select('pending_jobs, in_progress_jobs, succeeded_jobs, failed_jobs, avg_wait_ms, avg_duration_ms, captured_at')
      .maybeSingle();

    if (!summaryError && summary) {
      const summaryData = summary as any;
      const pending = summaryData.pending_jobs ?? 0;
      const inProgress = summaryData.in_progress_jobs ?? 0;
      const succeeded = summaryData.succeeded_jobs ?? 0;
      const failed = summaryData.failed_jobs ?? 0;

      metrics.totalJobs = pending + inProgress + succeeded + failed;
      metrics.startedJobs = inProgress + succeeded + failed;
      metrics.completedJobs = succeeded;
      metrics.failedJobs = failed;
      metrics.queuedJobs = queueStatus.queued;
      metrics.activeJobs = queueStatus.processing;
      metrics.averageWaitMs = summaryData.avg_wait_ms ?? metrics.averageWaitMs;
      metrics.averageDurationMs = summaryData.avg_duration_ms ?? metrics.averageDurationMs;
      metrics.lastUpdated = Date.now();
    } else if (summaryError) {
      logger.warn({ err: summaryError }, 'Failed to hydrate metrics from Supabase');
    }
  } catch (error) {
    logger.error({ err: error }, 'Queue bootstrap failed');
  }
}
const httpLogger = (pinoHttp as any)({ logger });

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5174';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const SNAPSHOT_ENDPOINT = `${BACKEND_URL}/api/agent/chart-snapshot`;
const HEALTH_TIMEOUT_MS = Number(process.env.HEALTH_TIMEOUT_MS || 15000);

let browserPromise: Promise<Browser> | null = null;
let browserInstance: Browser | null = null;
let lastActivityTime = Date.now();
const BROWSER_IDLE_TIMEOUT = 5 * 60 * 1000; // 5 minutes
const MAX_CONTEXTS = Number(process.env.MAX_CONTEXTS || 5);
const MAX_CONCURRENT_JOBS = Math.max(
  1,
  Math.min(Number(process.env.MAX_CONCURRENT_JOBS || 1), MAX_CONTEXTS)
);

async function ensureBrowser(): Promise<Browser> {
  try {
    // Check if browser needs restart due to idle timeout
    if (browserInstance && Date.now() - lastActivityTime > BROWSER_IDLE_TIMEOUT) {
      logger.info('Browser idle timeout reached, closing browser');
      await browserInstance.close();
      browserInstance = null;
      browserPromise = null;
    }

    // Initialize browser if needed
    if (!browserPromise) {
      browserPromise = chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      }).then(browser => {
        browserInstance = browser;
        browser.on('disconnected', () => {
          logger.warn('Browser disconnected unexpectedly');
          browserInstance = null;
          browserPromise = null;
        });
        return browser;
      }).catch(error => {
        logger.error({ err: error }, 'Failed to launch browser');
        browserInstance = null;
        browserPromise = null;
        throw error;
      });
    }

    lastActivityTime = Date.now();
    return browserPromise;
  } catch (error) {
    logger.error({ err: error }, 'Error ensuring browser');
    throw error;
  }
}

async function cleanupOldContexts(browser: Browser): Promise<void> {
  const contexts = browser.contexts();
  if (contexts.length > MAX_CONTEXTS) {
    logger.warn(`Too many contexts (${contexts.length}), cleaning up old ones`);
    const contextsToClose = contexts.slice(0, contexts.length - MAX_CONTEXTS);
    await Promise.all(contextsToClose.map(ctx => ctx.close().catch(err => 
      logger.error({ err }, 'Failed to close context')
    )));
  }
}

const jobs = new Map<string, RenderJob>();
let httpServer: Server | null = null;

const metrics = {
  totalJobs: 0,
  startedJobs: 0,
  completedJobs: 0,
  failedJobs: 0,
  activeJobs: 0,
  queuedJobs: 0,
  totalWaitMs: 0,
  totalDurationMs: 0,
  averageWaitMs: 0,
  averageDurationMs: 0,
  maxWaitMs: 0,
  maxDurationMs: 0,
  lastUpdated: Date.now(),
};



function recordWaitTime(job: RenderJob): void {
  metrics.startedJobs += 1;
  metrics.totalWaitMs += job.waitTimeMs ?? 0;
  metrics.maxWaitMs = Math.max(metrics.maxWaitMs, job.waitTimeMs ?? 0);
  metrics.averageWaitMs = Math.round(
    metrics.startedJobs > 0 ? metrics.totalWaitMs / metrics.startedJobs : 0
  );
  metrics.lastUpdated = Date.now();
}

function recordDuration(job: RenderJob, succeeded: boolean): void {
  const finishedAt = Date.now();
  job.finishedAt = finishedAt;
  job.durationMs = finishedAt - (job.startedAt ?? finishedAt);
  metrics.totalDurationMs += job.durationMs;
  metrics.maxDurationMs = Math.max(metrics.maxDurationMs, job.durationMs);
  if (succeeded) {
    metrics.completedJobs += 1;
  } else {
    metrics.failedJobs += 1;
  }
  const denom = Math.max(metrics.completedJobs + metrics.failedJobs, 1);
  metrics.averageDurationMs = Math.round(metrics.totalDurationMs / denom);
  metrics.lastUpdated = finishedAt;
}



// Initialize distributed queue with proper callback
const jobQueue = new DistributedQueue(MAX_CONCURRENT_JOBS, async (job: RenderJob) => {
  try {
    // Update metrics when job starts
    const now = Date.now();
    job.waitTimeMs = now - (job.queuedAt ?? job.createdAt);
    recordWaitTime(job);
    metrics.activeJobs = jobQueue.getStatus().processing;
    metrics.queuedJobs = jobQueue.getStatus().queued;
    metrics.lastUpdated = now;
    
    // Execute the render
    await renderChart(job);
    
    // Update success metrics
    recordDuration(job, true);
    metrics.activeJobs = jobQueue.getStatus().processing;
    metrics.queuedJobs = jobQueue.getStatus().queued;
  } catch (error) {
    // Update failure metrics
    logger.error({ err: error, jobId: job.id }, 'Job processing failed');
    job.status = 'failed';
    job.error = error instanceof Error ? error.message : 'Unknown error';
    recordDuration(job, false);
    metrics.activeJobs = jobQueue.getStatus().processing;
    metrics.queuedJobs = jobQueue.getStatus().queued;
    wsService.broadcastJobUpdate(job, 'updated');
    
    // Trigger webhook for job failure
    webhookService.triggerWebhooks(job, 'job.failed').catch(webhookError => {
      logger.error({ err: webhookError, jobId: job.id }, 'Failed to trigger job.failed webhook');
    });
  }
});

async function renderChart(job: RenderJob): Promise<void> {
  let browser: Browser | null = null;
  let context = null;
  let page = null;
  
  try {
    browser = await ensureBrowser();
    
    // Clean up old contexts if needed
    await cleanupOldContexts(browser);
    
    // Create new context with viewport settings
    context = await browser.newContext({ 
      acceptDownloads: false,
      viewport: { width: 1920, height: 1080 },
      deviceScaleFactor: 2 // Higher quality screenshots
    });
    
    page = await context.newPage();
    
    // Set longer timeouts for slow operations
    page.setDefaultTimeout(30000);
    
    job.status = 'in_progress';
    job.startedAt = Date.now();
    job.updatedAt = Date.now();
    
    // Broadcast job status update
    wsService.broadcastJobUpdate(job, 'updated');
    
    // Trigger webhook for job start
    webhookService.triggerWebhooks(job, 'job.started').catch(error => {
      logger.error({ err: error, jobId: job.id }, 'Failed to trigger job.started webhook');
    });

    // Navigate to frontend with retry logic
    let retries = 3;
    while (retries > 0) {
      try {
        await page.goto(FRONTEND_URL, { 
          waitUntil: 'networkidle',
          timeout: 30000
        });
        break;
      } catch (navError) {
        retries--;
        if (retries === 0) throw navError;
        logger.warn({ retries, err: navError }, 'Navigation failed, retrying');
        await page.waitForTimeout(1000);
      }
    }

    // Wait for chart to be ready
    await page.waitForFunction(
      '() => window.enhancedChartControl !== undefined',
      { timeout: 10000 }
    ).catch(() => {
      logger.warn('enhancedChartControl not found, continuing anyway');
    });

    // Execute commands if provided
    if (job.commands.length > 0) {
      const commandScript = `
        if (window.enhancedChartControl && window.enhancedChartControl.processEnhancedResponse) {
          window.enhancedChartControl.processEnhancedResponse(${JSON.stringify(job.commands.join(' '))});
        } else {
          console.warn('enhancedChartControl not available');
        }
      `;
      await page.evaluate(commandScript);
      
      // Allow more time for complex commands
      const waitTime = Math.min(job.commands.length * 100, 2000);
      await page.waitForTimeout(waitTime);
    }

    // Capture screenshot with retry
    let screenshotBuffer: Buffer | null = null;
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        screenshotBuffer = await page.screenshot({ 
          fullPage: false, // Only capture viewport for consistency
          type: 'png'
        });
        break;
      } catch (screenshotError) {
        if (attempt === 3) throw screenshotError;
        logger.warn({ attempt, err: screenshotError }, 'Screenshot failed, retrying');
        await page.waitForTimeout(500);
      }
    }

    if (!screenshotBuffer) {
      throw new Error('Failed to capture screenshot after 3 attempts');
    }

    const imageBase64 = screenshotBuffer.toString('base64');

    const snapshot: SnapshotResult = {
      imageBase64,
      chartCommands: job.commands,
      metadata: {
        ...job.metadata,
        renderTimestamp: Date.now(),
        browserContexts: browser?.contexts().length
      },
      symbol: job.symbol,
      timeframe: job.timeframe,
      capturedAt: new Date().toISOString(),
      visionModel: job.visionModel,
    };

    // Send snapshot to backend
    await sendSnapshot(snapshot);

    job.snapshot = snapshot;
    job.status = 'succeeded';
    job.updatedAt = Date.now();
    job.finishedAt = Date.now();
    job.durationMs = job.finishedAt - (job.startedAt || job.createdAt);
    
    logger.info({ jobId: job.id, symbol: job.symbol }, 'Render job completed successfully');
    
    // Broadcast job completion
    wsService.broadcastJobUpdate(job, 'completed');
    
    // Trigger webhook for job completion
    webhookService.triggerWebhooks(job, 'job.completed').catch(error => {
      logger.error({ err: error, jobId: job.id }, 'Failed to trigger job.completed webhook');
    });
  } catch (error) {
    logger.error({ err: error, jobId: job.id }, 'Render job failed');
    job.status = 'failed';
    job.error = (error as Error).message;
    job.updatedAt = Date.now();
    job.finishedAt = Date.now();
    job.durationMs = job.finishedAt - (job.startedAt || job.createdAt);
    
    // Broadcast job failure
    wsService.broadcastJobUpdate(job, 'failed');
    
    // Trigger webhook for job failure
    webhookService.triggerWebhooks(job, 'job.failed').catch(error => {
      logger.error({ err: error, jobId: job.id }, 'Failed to trigger job.failed webhook');
    });
  } finally {
    // Ensure proper cleanup
    if (page) {
      await page.close().catch(err => 
        logger.error({ err }, 'Failed to close page')
      );
    }
    if (context) {
      await context.close().catch(err => 
        logger.error({ err }, 'Failed to close context')
      );
    }
  }
}

async function sendSnapshot(snapshot: SnapshotResult): Promise<void> {
  const payload = {
    symbol: snapshot.symbol,
    timeframe: snapshot.timeframe,
    image_base64: snapshot.imageBase64,
    chart_commands: snapshot.chartCommands,
    metadata: snapshot.metadata,
    vision_model: snapshot.visionModel,
  };

  const response = await fetch(SNAPSHOT_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Snapshot ingestion failed: ${response.status} ${text}`);
  }
}

const app = express();
app.use(express.json({ limit: '8mb' }));
app.use(httpLogger);

app.get('/health', async (_req: Request, res: Response) => {
  try {
    const browser = await Promise.race([
      ensureBrowser(),
      new Promise<Browser>((_, reject) =>
        setTimeout(() => reject(new Error('health timeout')), HEALTH_TIMEOUT_MS)
      ),
    ]);

    res.json({ status: 'ok', version: '0.1.0', contexts: browser.contexts().length });
  } catch (error) {
    res.status(500).json({ status: 'error', message: (error as Error).message });
  }
});

app.post('/render', async (req: Request<unknown, unknown, RenderRequest>, res: Response<RenderResponse>) => {
  const { symbol, timeframe, commands, visionModel, metadata } = req.body ?? {};

  if (!symbol || !timeframe) {
    res.status(400).json({ jobId: 'invalid', status: 'failed' });
    return;
  }

  // Validate and normalize commands
  let validatedCommands: string[] = [];
  if (commands && commands.length > 0) {
    const validation = CommandValidator.validate(commands);
    
    if (!validation.valid) {
      logger.error({ errors: validation.errors, commands }, 'Invalid commands received');
      res.status(400).json({ 
        jobId: 'invalid', 
        status: 'failed',
        error: `Invalid commands: ${validation.errors.join(', ')}`
      } as any);
      return;
    }
    
    if (validation.warnings.length > 0) {
      logger.warn({ warnings: validation.warnings }, 'Command validation warnings');
    }
    
    validatedCommands = validation.normalizedCommands;
    logger.info({ 
      originalCount: commands.length, 
      validatedCount: validatedCommands.length 
    }, 'Commands validated and normalized');
  }

  const jobId = randomUUID();
  const job: RenderJob = {
    id: jobId,
    symbol,
    timeframe,
    commands: validatedCommands,
    visionModel,
    metadata: {
      ...metadata,
      originalCommands: commands,
      commandsValidated: true,
    },
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    attempts: 0,
  };
  jobs.set(jobId, job);

  metrics.totalJobs += 1;
  metrics.lastUpdated = Date.now();

  // Trigger webhook for job creation
  webhookService.triggerWebhooks(job, 'job.created').catch(error => {
    logger.error({ err: error, jobId }, 'Failed to trigger job.created webhook');
  });

  // Extract priority from request (default to 100)
  const priority = typeof req.body.priority === 'number' ? req.body.priority : 100;
  
  // Add job to priority queue
  jobQueue.enqueue(job, priority);
  
  const queueStatus = jobQueue.getStatus();
  metrics.queuedJobs = queueStatus.queued;
  metrics.activeJobs = queueStatus.processing;
  metrics.lastUpdated = Date.now();

  // Get queue position and estimated time
  const queuePosition = jobQueue.getJobPosition(jobId);
  const estimatedStartMs = jobQueue.getEstimatedStartTime(jobId);
  const estimatedStartSeconds = estimatedStartMs ? Math.round(estimatedStartMs / 1000) : undefined;

  res.status(202).json({ 
    jobId, 
    status: job.status,
    queuePosition: queuePosition > 0 ? queuePosition : undefined,
    estimatedStartSeconds,
  });
});

app.get('/jobs/:id', (req: Request, res: Response) => {
  const job = jobs.get(req.params.id);
  if (!job) {
    res.status(404).json({ error: 'job not found' });
    return;
  }
  res.json(job);
});

// GET /metrics endpoint - expose performance metrics
app.get('/metrics', (_req: Request, res: Response) => {
  const queueStatus = jobQueue.getStatus();
  
  res.json({
    ...metrics,
    queue: {
      queued: queueStatus.queued,
      processing: queueStatus.processing,
      queuedJobs: queueStatus.queuedJobs,
      processingJobs: queueStatus.processingJobs,
    },
    browser: {
      contexts: browserInstance ? browserInstance.contexts().length : 0,
      maxContexts: MAX_CONTEXTS,
    },
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage(),
    timestamp: Date.now(),
  });
});

// GET /status/:id endpoint - detailed job status with queue info
app.get('/status/:id', (req: Request, res: Response) => {
  const job = jobs.get(req.params.id);
  if (!job) {
    res.status(404).json({ error: 'job not found' });
    return;
  }
  
  const queuePosition = job.status === 'queued' ? jobQueue.getJobPosition(job.id) : 0;
  const estimatedStartMs = job.status === 'queued' ? jobQueue.getEstimatedStartTime(job.id) : null;
  
  res.json({
    ...job,
    queuePosition: queuePosition > 0 ? queuePosition : undefined,
    estimatedStartMs,
    estimatedStartSeconds: estimatedStartMs ? Math.round(estimatedStartMs / 1000) : undefined,
  });
});

// GET /snapshot/:id endpoint - retrieve job snapshot result
app.get('/snapshot/:id', (req: Request, res: Response) => {
  const job = jobs.get(req.params.id);
  if (!job) {
    res.status(404).json({ error: 'job not found' });
    return;
  }
  
  if (!job.snapshot) {
    if (job.status === 'pending' || job.status === 'queued' || job.status === 'in_progress') {
      res.status(202).json({ 
        message: 'snapshot not yet available',
        status: job.status,
      });
    } else {
      res.status(404).json({ 
        error: 'no snapshot available for this job',
        status: job.status,
      });
    }
    return;
  }
  
  res.json(job.snapshot);
});

// WebSocket stats endpoint
app.get('/ws/stats', (_req: Request, res: Response) => {
  const stats = wsService.getStats();
  res.json({
    ...stats,
    activeJobs: jobs.size,
    timestamp: Date.now()
  });
});

// Webhook stats endpoint
app.get('/webhooks/stats', async (_req: Request, res: Response) => {
  try {
    const stats = await webhookService.getStats();
    res.json({
      ...stats,
      timestamp: Date.now()
    });
  } catch (error) {
    logger.error({ err: error }, 'Failed to get webhook stats');
    res.status(500).json({ error: 'Failed to get webhook stats' });
  }
});

// Manual webhook processing endpoint (for debugging)
app.post('/webhooks/process', async (_req: Request, res: Response) => {
  try {
    await webhookService.processPendingWebhooks();
    res.json({ message: 'Webhook processing triggered' });
  } catch (error) {
    logger.error({ err: error }, 'Manual webhook processing failed');
    res.status(500).json({ error: 'Failed to process webhooks' });
  }
});

// Webhook cleanup endpoint
app.delete('/webhooks/cleanup', async (req: Request, res: Response) => {
  try {
    const olderThanDays = Number(req.query.days) || 7;
    const deletedCount = await webhookService.cleanupOldEvents(olderThanDays);
    res.json({ deletedCount, olderThanDays });
  } catch (error) {
    logger.error({ err: error }, 'Webhook cleanup failed');
    res.status(500).json({ error: 'Failed to cleanup webhooks' });
  }
});

// Distributed queue stats endpoint
app.get('/distributed/stats', (_req: Request, res: Response) => {
  console.log('JobQueue instance:', jobQueue.constructor.name);
  console.log('JobQueue methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(jobQueue)));
  const stats = jobQueue.getDistributedStats();
  console.log('Stats from getDistributedStats:', JSON.stringify(stats, null, 2));
  console.log('Stats has enhanced property:', 'enhanced' in stats);
  res.json({
    ...stats,
    timestamp: Date.now()
  });
});

// Worker stats endpoint
app.get('/worker/stats', (_req: Request, res: Response) => {
  const stats = workerService.getStats();
  res.json({
    ...stats,
    timestamp: Date.now()
  });
});

// Orphan recovery endpoint (for manual triggering)
app.post('/distributed/recover-orphans', async (_req: Request, res: Response) => {
  try {
    await jobQueue.recoverOrphanedJobs();
    res.json({ message: 'Orphan recovery triggered' });
  } catch (error) {
    logger.error({ err: error }, 'Manual orphan recovery failed');
    res.status(500).json({ error: 'Failed to recover orphaned jobs' });
  }
});

// Clean up old jobs periodically
const JOB_RETENTION_MS = 10 * 60 * 1000; // 10 minutes
setInterval(() => {
  const now = Date.now();
  const jobsToDelete: string[] = [];

  jobs.forEach((job, id) => {
    if (now - job.updatedAt > JOB_RETENTION_MS) {
      jobsToDelete.push(id);
    }
  });

  jobsToDelete.forEach(id => {
    jobs.delete(id);
    logger.debug({ jobId: id }, 'Cleaned up old job');
  });

  if (jobsToDelete.length > 0) {
    logger.info({ count: jobsToDelete.length }, 'Cleaned up old jobs');
  }
}, 60000); // Run every minute

// Graceful shutdown handling
async function shutdown(signal: string): Promise<void> {
  logger.info({ signal }, 'Shutdown signal received');
  
  try {
    // Start draining - stop accepting new jobs
    await workerService.drain();
    logger.info('Worker draining started');

    // Shutdown WebSocket service
    wsService.shutdown();

    // Shutdown distributed queue
    await jobQueue.shutdown();
    logger.info('Distributed queue shutdown');

    // Shutdown worker service
    await workerService.shutdown();
    logger.info('Worker service shutdown');

    if (httpServer) {
      const serverToClose = httpServer;
      await new Promise<void>((resolve, reject) => {
        serverToClose.close((err) => {
          if (err) {
            reject(err);
          } else {
            resolve();
          }
        });
      });
      logger.info('HTTP server closed');
      httpServer = null;
    }

    // Close browser if exists
    if (browserInstance) {
      await browserInstance.close();
      logger.info('Browser closed');
    }
    
    // Exit cleanly
    process.exit(0);
  } catch (error) {
    logger.error({ err: error }, 'Error during shutdown');
    process.exit(1);
  }
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

const port = Number(process.env.PORT || 3100);

async function startServer(): Promise<void> {
  // Start worker service first
  await workerService.start();
  logger.info('Worker service started');

  await bootstrapQueueState();

  httpServer = app.listen(port, () => {
    if (!httpServer) {
      return;
    }

    wsService.initialize(httpServer);

    logger.info(
      {
        port,
        FRONTEND_URL,
        BACKEND_URL,
        SNAPSHOT_ENDPOINT,
        MAX_CONTEXTS,
        BROWSER_IDLE_TIMEOUT,
        websocket: true,
        workerId: workerService.getWorkerId(),
      },
      'Headless chart service listening with distributed queue + WebSocket'
    );
  });
}

startServer().catch((error) => {
  logger.error({ err: error }, 'Failed to start headless chart service');
  process.exit(1);
});
