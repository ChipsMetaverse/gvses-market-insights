import { useEffect, useRef } from 'react';

interface TouchGestureOptions {
  enabled?: boolean;
  swipeThreshold?: number;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onPinch?: (direction: 'in' | 'out') => void;
}

const DEFAULT_THRESHOLD = 40;

export const useTouchGestures = <T extends HTMLElement>({
  enabled = true,
  swipeThreshold = DEFAULT_THRESHOLD,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onPinch,
}: TouchGestureOptions = {}) => {
  const elementRef = useRef<T | null>(null);
  const touchStartRef = useRef<{ x: number; y: number; distance?: number } | null>(null);

  useEffect(() => {
    const target = elementRef.current;
    if (!enabled || !target) {
      return;
    }

    const getDistance = (touches: TouchList) => {
      if (touches.length < 2) return undefined;
      const [t1, t2] = [touches[0], touches[1]];
      const dx = t2.clientX - t1.clientX;
      const dy = t2.clientY - t1.clientY;
      return Math.hypot(dx, dy);
    };

    const handleTouchStart = (event: TouchEvent) => {
      const touch = event.touches[0];
      touchStartRef.current = {
        x: touch.clientX,
        y: touch.clientY,
        distance: getDistance(event.touches),
      };
    };

    const handleTouchMove = (event: TouchEvent) => {
      if (!touchStartRef.current) return;

      if (event.touches.length === 2 && onPinch) {
        const currentDistance = getDistance(event.touches);
        if (typeof currentDistance === 'number' && typeof touchStartRef.current.distance === 'number') {
          const delta = currentDistance - touchStartRef.current.distance;
          if (Math.abs(delta) > swipeThreshold / 2) {
            onPinch(delta < 0 ? 'in' : 'out');
            touchStartRef.current.distance = currentDistance;
          }
        }
      }
    };

    const handleTouchEnd = (event: TouchEvent) => {
      if (!touchStartRef.current || event.changedTouches.length === 0) {
        touchStartRef.current = null;
        return;
      }

      const touch = event.changedTouches[0];
      const { x, y } = touchStartRef.current;
      const deltaX = touch.clientX - x;
      const deltaY = touch.clientY - y;

      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        if (deltaX > swipeThreshold) {
          onSwipeRight?.();
        } else if (deltaX < -swipeThreshold) {
          onSwipeLeft?.();
        }
      } else {
        if (deltaY > swipeThreshold) {
          onSwipeDown?.();
        } else if (deltaY < -swipeThreshold) {
          onSwipeUp?.();
        }
      }

      touchStartRef.current = null;
    };

    target.addEventListener('touchstart', handleTouchStart, { passive: true });
    target.addEventListener('touchmove', handleTouchMove, { passive: true });
    target.addEventListener('touchend', handleTouchEnd);
    target.addEventListener('touchcancel', handleTouchEnd);

    return () => {
      target.removeEventListener('touchstart', handleTouchStart);
      target.removeEventListener('touchmove', handleTouchMove);
      target.removeEventListener('touchend', handleTouchEnd);
      target.removeEventListener('touchcancel', handleTouchEnd);
    };
  }, [enabled, swipeThreshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, onPinch]);

  return elementRef;
};
