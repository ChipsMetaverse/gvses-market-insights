/**
 * Retry utility with exponential backoff for handling network errors
 *
 * Specifically designed to handle ERR_NETWORK_CHANGED errors and other
 * transient network failures during development and production.
 */

import axios, { AxiosError } from 'axios';
import { toast } from '@/components/ui/use-toast';

interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  retryableErrors?: string[];
  showToast?: boolean; // Show toast notifications for retries
}

const DEFAULT_OPTIONS: Required<Omit<RetryOptions, 'showToast'>> & { showToast: boolean } = {
  maxRetries: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
  retryableErrors: [
    'ERR_NETWORK_CHANGED',
    'ECONNREFUSED',
    'ETIMEDOUT',
    'ENOTFOUND',
    'Network Error'
  ],
  showToast: true // Show toasts by default
};

/**
 * Check if an error is retryable based on error code or message
 */
function isRetryableError(error: any, retryableErrors: string[]): boolean {
  // Handle axios errors
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;

    // Check error code
    if (axiosError.code && retryableErrors.includes(axiosError.code)) {
      return true;
    }

    // Check error message
    if (axiosError.message && retryableErrors.some(e => axiosError.message.includes(e))) {
      return true;
    }

    // Retry on 502, 503, 504 status codes (temporary server errors)
    if (axiosError.response?.status && [502, 503, 504].includes(axiosError.response.status)) {
      return true;
    }
  }

  // Check generic error message
  if (error?.message && retryableErrors.some(e => error.message.includes(e))) {
    return true;
  }

  return false;
}

/**
 * Calculate delay with exponential backoff and jitter
 */
function calculateDelay(attempt: number, baseDelay: number, maxDelay: number): number {
  // Exponential backoff: 2^attempt * baseDelay
  const exponentialDelay = Math.min(Math.pow(2, attempt) * baseDelay, maxDelay);

  // Add jitter (±20%) to prevent thundering herd
  const jitter = exponentialDelay * 0.2 * (Math.random() - 0.5);

  return Math.floor(exponentialDelay + jitter);
}

/**
 * Retry a function with exponential backoff
 *
 * @param fn - Async function to retry
 * @param options - Retry configuration options
 * @returns Result of the successful function call
 * @throws Last error if all retries fail
 *
 * @example
 * ```typescript
 * const data = await retryWithBackoff(
 *   async () => axios.get('/api/data'),
 *   { maxRetries: 3, baseDelay: 1000 }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  let lastError: any;
  let toastId: string | undefined;

  for (let attempt = 0; attempt < opts.maxRetries; attempt++) {
    try {
      const result = await fn();

      // Show success toast if we recovered from a previous error
      if (attempt > 0 && opts.showToast) {
        toast({
          title: '✓ Connection restored',
          description: 'Successfully reconnected to server',
          variant: 'default'
        });
      }

      return result;
    } catch (error: any) {
      lastError = error;

      // Don't retry if error is not retryable
      if (!isRetryableError(error, opts.retryableErrors)) {
        throw error;
      }

      // Don't retry on last attempt
      if (attempt === opts.maxRetries - 1) {
        break;
      }

      const delay = calculateDelay(attempt, opts.baseDelay, opts.maxDelay);

      // Show toast notification on first retry attempt
      if (attempt === 0 && opts.showToast) {
        toast({
          title: '⚠️ Connection issue detected',
          description: `Retrying... (attempt ${attempt + 1}/${opts.maxRetries})`,
          variant: 'destructive'
        });
      }

      console.warn(
        `[RetryBackoff] Attempt ${attempt + 1}/${opts.maxRetries} failed. ` +
        `Retrying in ${delay}ms...`,
        {
          error: error?.message || error,
          code: error?.code,
          attempt: attempt + 1,
          maxRetries: opts.maxRetries
        }
      );

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  // All retries exhausted - show final error toast
  if (opts.showToast) {
    toast({
      title: '✗ Connection failed',
      description: 'Unable to connect after multiple attempts. Please refresh the page.',
      variant: 'destructive'
    });
  }

  console.error(
    `[RetryBackoff] All ${opts.maxRetries} retry attempts failed.`,
    { lastError: lastError?.message || lastError }
  );

  throw lastError;
}

/**
 * Higher-order function to wrap an async function with retry logic
 *
 * @example
 * ```typescript
 * const fetchWithRetry = withRetry(fetchData, { maxRetries: 3 });
 * const data = await fetchWithRetry(params);
 * ```
 */
export function withRetry<TArgs extends any[], TReturn>(
  fn: (...args: TArgs) => Promise<TReturn>,
  options: RetryOptions = {}
): (...args: TArgs) => Promise<TReturn> {
  return async (...args: TArgs) => {
    return retryWithBackoff(() => fn(...args), options);
  };
}
