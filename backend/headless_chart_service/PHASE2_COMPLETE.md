# Phase 2: Multi-Worker Coordination - COMPLETE

## Summary
Phase 2 has been successfully implemented, adding multi-worker coordination capabilities to the headless chart service. This enables horizontal scaling and distributed job processing across multiple service instances.

## Components Implemented

### 1. Worker Service (`src/workerService.ts`)
- **Worker Registration**: Each instance registers with unique ID in Supabase
- **Heartbeat System**: 30-second heartbeat intervals to maintain worker alive status
- **Job Lease Management**: Acquire, renew, and release job leases atomically
- **Stale Worker Cleanup**: Automatic cleanup of workers that haven't sent heartbeat in 90 seconds
- **Worker Stats**: Real-time worker statistics and utilization tracking

### 2. Distributed Queue (`src/distributedQueue.ts`)
- **Extends JobPriorityQueue**: Inherits all priority queue functionality
- **Job Leasing**: Acquires exclusive lease before processing jobs
- **Lease Renewal**: Automatic lease renewal every 2 minutes during processing
- **Orphan Recovery**: Recovers jobs from expired leases every minute
- **Stuck Job Recovery**: Identifies and re-queues jobs stuck in progress
- **Distributed Stats**: Comprehensive statistics for multi-worker coordination

### 3. Server Integration (`src/server.ts`)
- **Worker Lifecycle**: Integrated worker service startup and shutdown
- **Distributed Queue**: Replaced JobPriorityQueue with DistributedQueue
- **New Endpoints**:
  - `GET /distributed/stats` - Distributed queue statistics
  - `GET /worker/stats` - Worker service statistics
  - `POST /distributed/recover-orphans` - Manual orphan recovery trigger
- **Graceful Shutdown**: Proper draining and cleanup on shutdown

### 4. Database Schema (`migrations/phase2_supabase.sql`)
- **headless_workers table**: Tracks active worker instances
- **headless_job_leases table**: Manages exclusive job leases with constraints
- **headless_webhook_events table**: Tracks webhook delivery attempts
- **Monitoring views**: Added for operational visibility

## Key Features

### Worker Coordination
- Multiple workers can run simultaneously without job duplication
- Automatic load balancing across available workers
- Workers claim jobs atomically using database constraints
- Failed workers automatically release their jobs

### Fault Tolerance
- Jobs automatically recovered from dead workers
- Lease expiry ensures no job gets stuck forever
- Retry logic for transient failures
- Graceful degradation when workers fail

### Monitoring
- Real-time worker health tracking
- Job lease visibility
- Queue distribution statistics
- Webhook delivery tracking

## Configuration

### Environment Variables
```bash
WORKER_ID=<unique-id>           # Optional, auto-generated if not set
WORKER_MAX_JOBS=3               # Max concurrent jobs per worker
MAX_CONCURRENT_JOBS=3           # Max jobs this worker can process
```

## API Endpoints

### Worker Management
- `GET /worker/stats` - Current worker statistics
- `GET /distributed/stats` - Distributed queue statistics
- `POST /distributed/recover-orphans` - Trigger orphan recovery

### Existing Enhanced
- `/health` - Now includes worker ID
- `/metrics` - Enhanced with distributed metrics

## Migration Instructions

1. Run the Phase 2 migration in Supabase:
   ```sql
   -- Execute migrations/phase2_supabase.sql in Supabase SQL editor
   ```

2. Update environment variables with Supabase credentials

3. Deploy multiple instances for testing:
   ```bash
   # Instance 1
   WORKER_ID=worker-1 npm start
   
   # Instance 2
   WORKER_ID=worker-2 npm start
   ```

## Testing Multi-Worker Coordination

1. Start multiple worker instances
2. Submit jobs via `/render` endpoint
3. Observe job distribution across workers via `/distributed/stats`
4. Kill a worker mid-processing to test orphan recovery
5. Monitor lease acquisition and renewal in logs

## Next Steps (Phase 3)
- Implement webhook retry logic
- Add worker auto-scaling
- Create monitoring dashboard
- Add worker priority/capability matching
- Implement job retry with backoff

## Architectural Benefits

### Scalability
- Horizontal scaling by adding more workers
- No single point of failure
- Load automatically distributed

### Reliability
- Jobs never lost due to worker failure
- Automatic recovery mechanisms
- Database-backed persistence

### Observability
- Real-time worker monitoring
- Job tracking across workers
- Comprehensive statistics

## Troubleshooting

### Common Issues
1. **Worker not registering**: Check Supabase connection
2. **Jobs not being picked up**: Verify lease table isn't full
3. **Orphaned jobs**: Check orphan recovery is running
4. **Duplicate processing**: Ensure lease constraints are active

### Debug Commands
```bash
# Check worker status
curl http://localhost:3100/worker/stats

# View distributed stats
curl http://localhost:3100/distributed/stats

# Manually trigger orphan recovery
curl -X POST http://localhost:3100/distributed/recover-orphans
```

## Performance Considerations

- Lease duration: 5 minutes (configurable)
- Lease renewal: Every 2 minutes
- Orphan check: Every 1 minute
- Heartbeat interval: 30 seconds
- Stale worker threshold: 90 seconds

These values can be tuned based on workload characteristics.