export type ChartCommand = string;

export interface RenderRequest {
  symbol: string;
  timeframe: string;
  commands: ChartCommand[];
  visionModel?: string;
  metadata?: Record<string, unknown>;
}

export interface RenderJob extends RenderRequest {
  id: string;
  status: "pending" | "in_progress" | "succeeded" | "failed";
  error?: string;
  snapshot?: SnapshotResult;
  createdAt: number;
  updatedAt: number;
}

export interface SnapshotResult {
  imageBase64: string;
  chartCommands: ChartCommand[];
  metadata: Record<string, unknown>;
  symbol: string;
  timeframe: string;
  capturedAt: string;
  visionModel?: string;
}

export interface RenderResponse {
  jobId: string;
  status: RenderJob["status"];
}
