/**
 * WebSocket Service for Real-time Job Updates
 * Provides live streaming of job status changes and progress
 */

import { WebSocketServer, WebSocket } from 'ws';
import { Server } from 'http';
import pino from 'pino';
import { RenderJob } from './types.js';

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });

interface WSClient {
  id: string;
  ws: WebSocket;
  subscriptions: Set<string>; // Job IDs this client is watching
  isAlive: boolean;
}

export class WebSocketService {
  private wss: WebSocketServer | null = null;
  private clients: Map<string, WSClient> = new Map();
  private pingInterval: NodeJS.Timeout | null = null;

  /**
   * Initialize WebSocket server
   */
  initialize(server: Server): void {
    this.wss = new WebSocketServer({ 
      server,
      path: '/ws'
    });

    this.wss.on('connection', this.handleConnection.bind(this));

    // Start heartbeat to detect disconnected clients
    this.pingInterval = setInterval(() => {
      this.clients.forEach((client) => {
        if (!client.isAlive) {
          client.ws.terminate();
          this.clients.delete(client.id);
          logger.debug({ clientId: client.id }, 'Client disconnected (ping timeout)');
          return;
        }
        client.isAlive = false;
        client.ws.ping();
      });
    }, 30000); // 30 seconds

    logger.info({ path: '/ws' }, 'WebSocket service initialized');
  }

  /**
   * Handle new WebSocket connection
   */
  private handleConnection(ws: WebSocket, req: any): void {
    const clientId = this.generateClientId();
    const client: WSClient = {
      id: clientId,
      ws,
      subscriptions: new Set(),
      isAlive: true
    };

    this.clients.set(clientId, client);
    logger.info({ clientId, ip: req.socket.remoteAddress }, 'WebSocket client connected');

    // Send welcome message
    this.sendToClient(client, {
      type: 'connected',
      clientId,
      timestamp: Date.now()
    });

    // Handle incoming messages
    ws.on('message', (data: Buffer) => {
      try {
        const message = JSON.parse(data.toString());
        this.handleClientMessage(client, message);
      } catch (error) {
        logger.error({ error, clientId }, 'Invalid WebSocket message');
        this.sendToClient(client, {
          type: 'error',
          message: 'Invalid message format'
        });
      }
    });

    // Handle pong responses
    ws.on('pong', () => {
      client.isAlive = true;
    });

    // Handle client disconnect
    ws.on('close', () => {
      this.clients.delete(clientId);
      logger.info({ clientId }, 'WebSocket client disconnected');
    });

    // Handle errors
    ws.on('error', (error) => {
      logger.error({ error, clientId }, 'WebSocket error');
      this.clients.delete(clientId);
    });
  }

  /**
   * Handle messages from clients
   */
  private handleClientMessage(client: WSClient, message: any): void {
    const { type, jobId, jobIds } = message;

    switch (type) {
      case 'subscribe':
        if (jobId) {
          client.subscriptions.add(jobId);
          logger.debug({ clientId: client.id, jobId }, 'Client subscribed to job');
          this.sendToClient(client, {
            type: 'subscribed',
            jobId,
            timestamp: Date.now()
          });
        } else if (jobIds && Array.isArray(jobIds)) {
          jobIds.forEach(id => client.subscriptions.add(id));
          logger.debug({ clientId: client.id, count: jobIds.length }, 'Client subscribed to multiple jobs');
          this.sendToClient(client, {
            type: 'subscribed',
            jobIds,
            timestamp: Date.now()
          });
        }
        break;

      case 'unsubscribe':
        if (jobId) {
          client.subscriptions.delete(jobId);
          logger.debug({ clientId: client.id, jobId }, 'Client unsubscribed from job');
          this.sendToClient(client, {
            type: 'unsubscribed',
            jobId,
            timestamp: Date.now()
          });
        }
        break;

      case 'unsubscribe_all':
        client.subscriptions.clear();
        logger.debug({ clientId: client.id }, 'Client unsubscribed from all jobs');
        this.sendToClient(client, {
          type: 'unsubscribed_all',
          timestamp: Date.now()
        });
        break;

      case 'ping':
        this.sendToClient(client, {
          type: 'pong',
          timestamp: Date.now()
        });
        break;

      default:
        logger.warn({ clientId: client.id, type }, 'Unknown message type');
        this.sendToClient(client, {
          type: 'error',
          message: `Unknown message type: ${type}`
        });
    }
  }

  /**
   * Send message to specific client
   */
  private sendToClient(client: WSClient, message: any): void {
    if (client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(JSON.stringify(message));
    }
  }

  /**
   * Broadcast job update to all subscribed clients
   */
  broadcastJobUpdate(job: RenderJob, eventType: 'created' | 'updated' | 'completed' | 'failed'): void {
    const message = {
      type: 'job_update',
      eventType,
      job: {
        id: job.id,
        status: job.status,
        symbol: job.symbol,
        timeframe: job.timeframe,
        createdAt: job.createdAt,
        updatedAt: job.updatedAt,
        error: job.error,
        progress: this.calculateProgress(job)
      },
      timestamp: Date.now()
    };

    let broadcastCount = 0;
    this.clients.forEach((client) => {
      if (client.subscriptions.has(job.id) || client.subscriptions.has('*')) {
        this.sendToClient(client, message);
        broadcastCount++;
      }
    });

    if (broadcastCount > 0) {
      logger.debug({ 
        jobId: job.id, 
        eventType, 
        broadcastCount 
      }, 'Job update broadcasted');
    }
  }

  /**
   * Broadcast system-wide message
   */
  broadcastSystemMessage(message: any): void {
    const systemMessage = {
      type: 'system',
      ...message,
      timestamp: Date.now()
    };

    this.clients.forEach((client) => {
      this.sendToClient(client, systemMessage);
    });

    logger.info({ 
      clientCount: this.clients.size 
    }, 'System message broadcasted');
  }

  /**
   * Phase 3: Broadcast pattern overlay updates
   */
  broadcastPatternOverlay(
    patternId: string,
    eventType: 'created' | 'updated' | 'validated' | 'invalidated',
    overlayData: any
  ): number {
    const patternMessage = {
      type: 'pattern:overlay',
      eventType,
      patternId,
      data: overlayData,
      timestamp: Date.now()
    };

    // Broadcast to all connected clients
    let broadcastCount = 0;
    this.clients.forEach((client) => {
      this.sendToClient(client, patternMessage);
      broadcastCount++;
    });

    logger.info({ 
      patternId,
      eventType,
      broadcastCount
    }, 'Pattern overlay broadcasted');
    return broadcastCount;
  }

  /**
   * Phase 3: Broadcast pattern delta updates (efficient streaming)
   */
  broadcastPatternDelta(
    symbol: string,
    deltas: Array<{
      patternId: string;
      operation: 'add' | 'update' | 'remove';
      geometry?: any;
      metadata?: any;
    }>
  ): number {
    const deltaMessage = {
      type: 'pattern:delta',
      symbol,
      deltas,
      timestamp: Date.now()
    };

    // Only send to clients subscribed to this symbol
    let broadcastCount = 0;
    this.clients.forEach((client) => {
      // In future, check if client is subscribed to this symbol
      // For now, broadcast to all
      this.sendToClient(client, deltaMessage);
      broadcastCount++;
    });

    logger.debug({ 
      symbol,
      deltaCount: deltas.length,
      broadcastCount
    }, 'Pattern deltas broadcasted');
    return broadcastCount;
  }

  /**
   * Calculate job progress percentage
   */
  private calculateProgress(job: RenderJob): number {
    if (job.status === 'pending') return 0;
    if (job.status === 'succeeded') return 100;
    if (job.status === 'failed') return -1;
    
    // Estimate progress based on time elapsed (assuming avg 5 seconds)
    const elapsed = Date.now() - job.createdAt;
    const estimated = Math.min(95, Math.floor((elapsed / 5000) * 100));
    return estimated;
  }

  /**
   * Generate unique client ID
   */
  private generateClientId(): string {
    return `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get current statistics
   */
  getStats(): any {
    const subscriptionCounts = new Map<string, number>();
    this.clients.forEach(client => {
      client.subscriptions.forEach(jobId => {
        subscriptionCounts.set(jobId, (subscriptionCounts.get(jobId) || 0) + 1);
      });
    });

    return {
      connectedClients: this.clients.size,
      totalSubscriptions: Array.from(this.clients.values())
        .reduce((sum, client) => sum + client.subscriptions.size, 0),
      subscriptionsByJob: Object.fromEntries(subscriptionCounts)
    };
  }

  /**
   * Cleanup on shutdown
   */
  shutdown(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }

    this.clients.forEach(client => {
      client.ws.close(1000, 'Server shutting down');
    });
    this.clients.clear();

    if (this.wss) {
      this.wss.close();
      this.wss = null;
    }

    logger.info('WebSocket service shut down');
  }
}

// Export singleton instance
export const wsService = new WebSocketService();