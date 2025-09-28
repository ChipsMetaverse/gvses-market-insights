export type ChartCommand = string;

export type JobStatus =
  | "pending"
  | "queued"
  | "in_progress"
  | "succeeded"
  | "failed";

export interface RenderRequest {
  symbol: string;
  timeframe: string;
  commands: ChartCommand[];
  visionModel?: string;
  metadata?: Record<string, unknown>;
  /**
   * Lower numbers are processed before higher numbers. Defaults to 100.
   */
  priority?: number;
}

export interface RenderJob extends RenderRequest {
  id: string;
  status: JobStatus;
  error?: string;
  snapshot?: SnapshotResult;
  createdAt: number;
  updatedAt: number;
  startedAt?: number;
  finishedAt?: number;
  durationMs?: number;
  attempts: number;
  priority?: number;
  queuedAt?: number;
  queuePosition?: number;
  waitTimeMs?: number;
}

export interface SnapshotResult {
  imageBase64: string;
  chartCommands: ChartCommand[];
  metadata: Record<string, unknown>;
  symbol: string;
  timeframe: string;
  capturedAt: string;
  visionModel?: string;
  state?: Record<string, unknown>;
}

export interface RenderResponse {
  jobId: string;
  status: JobStatus;
  queuePosition?: number;
  estimatedStartSeconds?: number;
}

export type WebhookEventType = 'job.created' | 'job.started' | 'job.completed' | 'job.failed';

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
