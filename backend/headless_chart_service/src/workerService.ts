/**
 * Worker Registration and Heartbeat Service for Multi-Worker Coordination
 */

import pino from 'pino';
import { randomUUID } from 'crypto';
import os from 'os';
import { supabase } from './supabaseClient.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

export interface WorkerInfo {
  id: string;
  hostname: string;
  capabilities: Record<string, any>;
  max_concurrent: number;
  active_jobs: number;
  last_heartbeat: string;
  status: 'starting' | 'active' | 'idle' | 'draining' | 'stopped';
  created_at: string;
  updated_at: string;
}

export class WorkerService {
  private workerId: string;
  private hostname: string;
  private maxConcurrent: number;
  private activeJobs: number = 0;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private status: WorkerInfo['status'] = 'starting';
  private capabilities: Record<string, any> = {};
  private isShuttingDown = false;

  constructor(maxConcurrent = 3) {
    this.workerId = process.env.WORKER_ID || randomUUID();
    this.hostname = os.hostname();
    this.maxConcurrent = Number(process.env.WORKER_MAX_JOBS) || maxConcurrent;
    
    // Set worker capabilities
    this.capabilities = {
      nodeVersion: process.version,
      platform: os.platform(),
      arch: os.arch(),
      cpus: os.cpus().length,
      totalMemory: os.totalmem(),
      headlessService: true,
    };
    
    logger.info({
      workerId: this.workerId,
      hostname: this.hostname,
      maxConcurrent: this.maxConcurrent,
      capabilities: this.capabilities,
    }, 'Worker service initialized');
  }

  /**
   * Register worker and start heartbeat
   */
  async start(): Promise<void> {
    try {
      // Register worker in database
      const { error } = await supabase
        .from('headless_workers')
        .upsert({
          id: this.workerId,
          hostname: this.hostname,
          capabilities: this.capabilities,
          max_concurrent: this.maxConcurrent,
          active_jobs: this.activeJobs,
          last_heartbeat: new Date().toISOString(),
          status: 'active',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }, {
          onConflict: 'id',
        });

      if (error) {
        logger.error({ err: error }, 'Failed to register worker');
        throw error;
      }

      this.status = 'active';
      
      // Start heartbeat
      this.startHeartbeat();
      
      // Clean up stale workers on startup
      await this.cleanupStaleWorkers();
      
      logger.info({ workerId: this.workerId }, 'Worker registered and heartbeat started');
    } catch (error) {
      logger.error({ err: error }, 'Failed to start worker service');
      throw error;
    }
  }

  /**
   * Start heartbeat to keep worker alive
   */
  private startHeartbeat(): void {
    const HEARTBEAT_INTERVAL = 30000; // 30 seconds
    
    this.heartbeatInterval = setInterval(async () => {
      try {
        const { error } = await supabase
          .from('headless_workers')
          .update({
            last_heartbeat: new Date().toISOString(),
            active_jobs: this.activeJobs,
            status: this.status,
            updated_at: new Date().toISOString(),
          })
          .eq('id', this.workerId);

        if (error) {
          logger.error({ err: error, workerId: this.workerId }, 'Heartbeat failed');
        } else {
          logger.debug({ workerId: this.workerId }, 'Heartbeat sent');
        }
      } catch (error) {
        logger.error({ err: error }, 'Heartbeat error');
      }
    }, HEARTBEAT_INTERVAL);
  }

  /**
   * Clean up workers that haven't sent heartbeat in 90 seconds
   */
  async cleanupStaleWorkers(): Promise<void> {
    const STALE_THRESHOLD = 90000; // 90 seconds
    const cutoffTime = new Date(Date.now() - STALE_THRESHOLD).toISOString();
    
    try {
      // Mark stale workers as stopped
      const { data: staleWorkers, error } = await supabase
        .from('headless_workers')
        .update({
          status: 'stopped',
          updated_at: new Date().toISOString(),
        })
        .lt('last_heartbeat', cutoffTime)
        .neq('status', 'stopped')
        .select('id');

      if (error) {
        logger.error({ err: error }, 'Failed to cleanup stale workers');
        return;
      }

      if (staleWorkers && staleWorkers.length > 0) {
        logger.info({ 
          count: staleWorkers.length,
          workerIds: staleWorkers.map(w => w.id),
        }, 'Cleaned up stale workers');
        
        // Release any job leases held by stale workers
        for (const worker of staleWorkers) {
          await this.releaseWorkerLeases(worker.id);
        }
      }
    } catch (error) {
      logger.error({ err: error }, 'Error cleaning up stale workers');
    }
  }

  /**
   * Release all job leases held by a worker
   */
  async releaseWorkerLeases(workerId: string): Promise<void> {
    try {
      const { data: leases, error: fetchError } = await supabase
        .from('headless_job_leases')
        .delete()
        .eq('worker_id', workerId)
        .select('job_id');

      if (fetchError) {
        logger.error({ err: fetchError, workerId }, 'Failed to release worker leases');
        return;
      }

      if (leases && leases.length > 0) {
        logger.info({
          workerId,
          releasedCount: leases.length,
          jobIds: leases.map(l => l.job_id),
        }, 'Released job leases for worker');
        
        // Update jobs back to queued status
        for (const lease of leases) {
          await supabase
            .from('headless_jobs')
            .update({
              status: 'queued',
              updated_at: new Date().toISOString(),
            })
            .eq('id', lease.job_id)
            .eq('status', 'in_progress');
        }
      }
    } catch (error) {
      logger.error({ err: error, workerId }, 'Error releasing worker leases');
    }
  }

  /**
   * Acquire a lease on a job
   */
  async acquireJobLease(jobId: string, leaseDurationMs = 300000): Promise<boolean> {
    const now = new Date();
    const leaseExpires = new Date(now.getTime() + leaseDurationMs);
    
    try {
      // Try to insert a new lease
      const { error } = await supabase
        .from('headless_job_leases')
        .insert({
          job_id: jobId,
          worker_id: this.workerId,
          leased_at: now.toISOString(),
          lease_expires_at: leaseExpires.toISOString(),
          lease_token: randomUUID(),
          renewed_count: 0,
          created_at: now.toISOString(),
          updated_at: now.toISOString(),
        });

      if (error) {
        // Lease already exists for this job
        if (error.code === '23505') { // Unique violation
          logger.debug({ jobId, workerId: this.workerId }, 'Job already leased');
          return false;
        }
        logger.error({ err: error, jobId }, 'Failed to acquire job lease');
        return false;
      }

      logger.info({ 
        jobId, 
        workerId: this.workerId,
        leaseExpires: leaseExpires.toISOString(),
      }, 'Acquired job lease');
      
      return true;
    } catch (error) {
      logger.error({ err: error, jobId }, 'Error acquiring job lease');
      return false;
    }
  }

  /**
   * Renew an existing job lease
   */
  async renewJobLease(jobId: string, extensionMs = 300000): Promise<boolean> {
    const now = new Date();
    const newExpiry = new Date(now.getTime() + extensionMs);
    
    try {
      // First get current lease to increment counter
      const { data: currentLease } = await supabase
        .from('headless_job_leases')
        .select('renewed_count')
        .eq('job_id', jobId)
        .eq('worker_id', this.workerId)
        .single();
      
      const currentCount = currentLease?.renewed_count || 0;
      
      const { data, error } = await supabase
        .from('headless_job_leases')
        .update({
          lease_expires_at: newExpiry.toISOString(),
          renewed_count: currentCount + 1,
          updated_at: now.toISOString(),
        })
        .eq('job_id', jobId)
        .eq('worker_id', this.workerId)
        .select();

      if (error || !data || data.length === 0) {
        logger.error({ err: error, jobId }, 'Failed to renew job lease');
        return false;
      }

      logger.debug({ 
        jobId, 
        workerId: this.workerId,
        newExpiry: newExpiry.toISOString(),
      }, 'Renewed job lease');
      
      return true;
    } catch (error) {
      logger.error({ err: error, jobId }, 'Error renewing job lease');
      return false;
    }
  }

  /**
   * Release a job lease
   */
  async releaseJobLease(jobId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('headless_job_leases')
        .delete()
        .eq('job_id', jobId)
        .eq('worker_id', this.workerId);

      if (error) {
        logger.error({ err: error, jobId }, 'Failed to release job lease');
      } else {
        logger.info({ jobId, workerId: this.workerId }, 'Released job lease');
      }
    } catch (error) {
      logger.error({ err: error, jobId }, 'Error releasing job lease');
    }
  }

  /**
   * Update active job count
   */
  setActiveJobs(count: number): void {
    this.activeJobs = count;
    this.status = count === 0 ? 'idle' : 'active';
  }

  /**
   * Check if worker can accept more jobs
   */
  canAcceptJobs(): boolean {
    return !this.isShuttingDown && 
           this.status !== 'draining' && 
           this.status !== 'stopped' &&
           this.activeJobs < this.maxConcurrent;
  }

  /**
   * Start draining (stop accepting new jobs)
   */
  async drain(): Promise<void> {
    this.status = 'draining';
    logger.info({ workerId: this.workerId }, 'Worker draining started');
    
    await supabase
      .from('headless_workers')
      .update({
        status: 'draining',
        updated_at: new Date().toISOString(),
      })
      .eq('id', this.workerId);
  }

  /**
   * Shutdown worker and cleanup
   */
  async shutdown(): Promise<void> {
    if (this.isShuttingDown) return;
    
    this.isShuttingDown = true;
    this.status = 'stopped';
    
    logger.info({ workerId: this.workerId }, 'Worker shutdown initiated');
    
    // Stop heartbeat
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    // Update worker status
    await supabase
      .from('headless_workers')
      .update({
        status: 'stopped',
        active_jobs: 0,
        updated_at: new Date().toISOString(),
      })
      .eq('id', this.workerId);
    
    // Release all leases
    await this.releaseWorkerLeases(this.workerId);
    
    logger.info({ workerId: this.workerId }, 'Worker shutdown complete');
  }

  /**
   * Get worker statistics
   */
  getStats(): {
    workerId: string;
    hostname: string;
    status: string;
    activeJobs: number;
    maxConcurrent: number;
    utilization: number;
  } {
    return {
      workerId: this.workerId,
      hostname: this.hostname,
      status: this.status,
      activeJobs: this.activeJobs,
      maxConcurrent: this.maxConcurrent,
      utilization: this.maxConcurrent > 0 ? (this.activeJobs / this.maxConcurrent) * 100 : 0,
    };
  }

  getWorkerId(): string {
    return this.workerId;
  }
}

// Export singleton instance
export const workerService = new WorkerService();