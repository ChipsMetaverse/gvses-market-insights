import 'dotenv/config';

import express, { Request, Response } from 'express';
import pino from 'pino';
import pinoHttp from 'pino-http';
import { chromium, Browser } from 'playwright';
import { randomUUID } from 'crypto';
import fetch from 'node-fetch';

import {
  RenderRequest,
  RenderResponse,
  RenderJob,
  SnapshotResult,
} from './types.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });
const httpLogger = pinoHttp({ logger });

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const SNAPSHOT_ENDPOINT = `${BACKEND_URL}/api/agent/chart-snapshot`;
const HEALTH_TIMEOUT_MS = Number(process.env.HEALTH_TIMEOUT_MS || 15000);

let browserPromise: Promise<Browser> | null = null;

function ensureBrowser(): Promise<Browser> {
  if (!browserPromise) {
    browserPromise = chromium.launch({ headless: true });
  }
  return browserPromise;
}

const jobs = new Map<string, RenderJob>();

async function renderChart(job: RenderJob): Promise<void> {
  const browser = await ensureBrowser();
  const context = await browser.newContext({ acceptDownloads: false });
  const page = await context.newPage();
  job.status = 'in_progress';
  job.updatedAt = Date.now();

  try {
    await page.goto(FRONTEND_URL, { waitUntil: 'networkidle' });

    const commandScript = `window.enhancedChartControl?.processEnhancedResponse?.(${JSON.stringify(
      job.commands.join(' ')
    )})`;
    if (job.commands.length > 0) {
      await page.evaluate(commandScript);
      await page.waitForTimeout(500); // settle animations
    }

    const imageBuffer = await page.screenshot({ fullPage: true });
    const imageBase64 = imageBuffer.toString('base64');

    const snapshot: SnapshotResult = {
      imageBase64,
      chartCommands: job.commands,
      metadata: job.metadata ?? {},
      symbol: job.symbol,
      timeframe: job.timeframe,
      capturedAt: new Date().toISOString(),
      visionModel: job.visionModel,
    };

    await sendSnapshot(snapshot);

    job.snapshot = snapshot;
    job.status = 'succeeded';
    job.updatedAt = Date.now();
  } catch (error) {
    logger.error({ err: error, jobId: job.id }, 'Render job failed');
    job.status = 'failed';
    job.error = (error as Error).message;
    job.updatedAt = Date.now();
  } finally {
    await context.close();
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

  const jobId = randomUUID();
  const job: RenderJob = {
    id: jobId,
    symbol,
    timeframe,
    commands: commands ?? [],
    visionModel,
    metadata,
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  jobs.set(jobId, job);

  renderChart(job).catch((error) => logger.error({ err: error, jobId }, 'Background render failure'));

  res.status(202).json({ jobId, status: job.status });
});

app.get('/jobs/:id', (req: Request, res: Response) => {
  const job = jobs.get(req.params.id);
  if (!job) {
    res.status(404).json({ error: 'job not found' });
    return;
  }
  res.json(job);
});

const port = Number(process.env.PORT || 3100);
app.listen(port, () => {
  logger.info({ port, FRONTEND_URL, SNAPSHOT_ENDPOINT }, 'Headless chart service listening');
});
