import { test, mock } from 'node:test';
import assert from 'node:assert/strict';
import type { RenderJob } from '../src/types.js';

process.env.SUPABASE_URL ??= 'https://example.supabase.co';
process.env.SUPABASE_SERVICE_ROLE_KEY ??= 'service-role-key';
process.env.SUPABASE_SCHEMA ??= 'headless';

const createMutationChain = () => ({
  eq: mock.fn(async () => ({ data: null, error: null })),
});

const createSupabaseMock = (options?: {
  queueRows?: any[];
  inflightRows?: any[];
}) => {
  const queueRows = options?.queueRows ?? [];
  const inflightRows = options?.inflightRows ?? [];

  const headlessJobsUpsert = mock.fn(async () => ({ data: null, error: null }));
  const headlessJobsUpdate = mock.fn(() => createMutationChain());
  const headlessJobsDelete = mock.fn(() => createMutationChain());
  const headlessQueueUpsert = mock.fn(async () => ({ data: null, error: null }));
  const headlessQueueDelete = mock.fn(() => createMutationChain());

  const headlessQueueSelect = {
    order: mock.fn(() => ({
      order: mock.fn(() => Promise.resolve({ data: queueRows, error: null })),
    })),
  };

  const headlessJobsSelect = {
    in: mock.fn(() => Promise.resolve({ data: inflightRows, error: null })),
  };

  const client = {
    from: mock.fn((table: string) => {
      if (table === 'headless_jobs') {
        return {
          upsert: headlessJobsUpsert,
          update: headlessJobsUpdate,
          delete: headlessJobsDelete,
          select: () => headlessJobsSelect,
        };
      }
      if (table === 'headless_queue') {
        return {
          upsert: headlessQueueUpsert,
          delete: headlessQueueDelete,
          select: () => headlessQueueSelect,
        };
      }
      if (table === 'headless_job_history') {
        return {
          insert: mock.fn(async () => ({ data: null, error: null })),
        };
      }
      throw new Error(`Unexpected table ${table}`);
    }),
  } as const;

  return {
    client: client as unknown as typeof import('../src/supabaseClient.js').supabase,
    headlessJobsUpsert,
    headlessJobsUpdate,
    headlessQueueUpsert,
    headlessQueueDelete,
  };
};

const createWsServiceMock = () => {
  const service = {
    broadcastJobUpdate: mock.fn(),
    initialize: mock.fn(),
    shutdown: mock.fn(),
    getStats: mock.fn(() => ({ clients: 0 })),
  };

  return service as unknown as typeof import('../src/websocketService.js').wsService & {
    broadcastJobUpdate: ReturnType<typeof mock.fn>;
    initialize: ReturnType<typeof mock.fn>;
    shutdown: ReturnType<typeof mock.fn>;
    getStats: ReturnType<typeof mock.fn>;
  };
};

const flushMicrotasks = () => new Promise(resolve => setTimeout(resolve, 0));

test('persists newly enqueued jobs to Supabase tables', async (t) => {
  mock.restoreAll();

  const supabaseMock = createSupabaseMock();
  const wsMock = createWsServiceMock();

  const { JobPriorityQueue } = await import('../src/jobQueue.js');

  const queue = new JobPriorityQueue(0, async () => undefined, {
    supabaseClient: supabaseMock.client,
    websocketService: wsMock,
  });
  const job: RenderJob = {
    id: 'job-1',
    symbol: 'AAPL',
    timeframe: '1D',
    commands: [] as string[],
    status: 'pending',
    createdAt: Date.now(),
    updatedAt: Date.now(),
    attempts: 0,
  };

  queue.enqueue({ ...job }, 40);

  await flushMicrotasks();

  assert.ok(supabaseMock.headlessJobsUpsert.mock.calls.length >= 1, 'headless_jobs upsert invoked');
  assert.ok(supabaseMock.headlessQueueUpsert.mock.calls.length >= 1, 'headless_queue upsert invoked');

  const firstCall = supabaseMock.headlessJobsUpsert.mock.calls[0];
  assert.ok(firstCall, 'headless_jobs upsert should have at least one call');
  const [jobPayload] = (firstCall?.arguments ?? []) as Array<Record<string, any>>;
  assert.ok(jobPayload, 'upsert payload should be defined');
  assert.equal(jobPayload.id, 'job-1');
  assert.equal(jobPayload.priority, 40);
});

test('restores queued jobs from Supabase on service startup', async () => {
  mock.restoreAll();

  const nowIso = new Date().toISOString();
  const supabaseMock = createSupabaseMock({
    queueRows: [
      {
        job_id: 'job-queued',
        priority: 55,
        queued_at: nowIso,
        headless_jobs: {
          id: 'job-queued',
          symbol: 'MSFT',
          timeframe: '1H',
          commands: ['LOAD:MSFT'],
          vision_model: null,
          metadata: {},
          status: 'queued',
          priority: 55,
          attempts: 1,
          queued_at: nowIso,
          started_at: null,
          finished_at: null,
          wait_time_ms: null,
          duration_ms: null,
          error: null,
          snapshot: null,
          created_at: nowIso,
          updated_at: nowIso,
        },
      },
    ],
    inflightRows: [],
  });
  const wsMock = createWsServiceMock();

  const { JobPriorityQueue } = await import('../src/jobQueue.js');
  const queue = new JobPriorityQueue(0, async () => undefined, {
    supabaseClient: supabaseMock.client,
    websocketService: wsMock,
  });

  const restored = await queue.restorePendingJobs();

  assert.equal(restored.length, 1);
  const status = queue.getStatus();
  assert.equal(status.queued, 1);
  assert.equal(status.queuedJobs[0]?.id, 'job-queued');
});

test('requeues in-progress jobs detected during bootstrap', async () => {
  mock.restoreAll();

  const nowIso = new Date().toISOString();
  const supabaseMock = createSupabaseMock({
    queueRows: [],
    inflightRows: [
      {
        id: 'job-inflight',
        symbol: 'TSLA',
        timeframe: '15M',
        commands: ['LOAD:TSLA'],
        vision_model: null,
        metadata: {},
        status: 'in_progress',
        priority: 60,
        attempts: 2,
        queued_at: nowIso,
        started_at: nowIso,
        finished_at: null,
        wait_time_ms: null,
        duration_ms: null,
        error: null,
        snapshot: null,
        created_at: nowIso,
        updated_at: nowIso,
      },
    ],
  });
  const wsMock = createWsServiceMock();

  const { JobPriorityQueue } = await import('../src/jobQueue.js');
  const queue = new JobPriorityQueue(0, async () => undefined, {
    supabaseClient: supabaseMock.client,
    websocketService: wsMock,
  });

  const restored = await queue.restorePendingJobs();

  assert.equal(restored.length, 1, 'in-progress job should be requeued');
  const status = queue.getStatus();
  assert.equal(status.queued, 1, 'queue should contain requeued job');
  assert.equal(status.queuedJobs[0]?.id, 'job-inflight');

  assert.ok(supabaseMock.headlessQueueUpsert.mock.calls.some(call => {
    const [payload] = (call.arguments ?? []) as Array<Record<string, any>>;
    return payload?.job_id === 'job-inflight';
  }),
    'requeued job should be persisted back to headless_queue');
});
