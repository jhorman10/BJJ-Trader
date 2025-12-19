/**
 * Utility functions for frontend performance optimization
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyFunction = (...args: any[]) => void;

/**
 * Creates a throttled version of a function that only invokes it at most once
 * per specified wait period. This is more efficient than lodash for our use case.
 */
export function throttle<T extends AnyFunction>(func: T, wait: number): T {
  let lastTime = 0;
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return ((...args: Parameters<T>) => {
    const now = Date.now();
    const remaining = wait - (now - lastTime);

    if (remaining <= 0 || remaining > wait) {
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
      lastTime = now;
      func(...args);
    } else if (!timeoutId) {
      timeoutId = setTimeout(() => {
        lastTime = Date.now();
        timeoutId = null;
        func(...args);
      }, remaining);
    }
  }) as T;
}

/**
 * Creates a debounced version of a function that delays invoking until after
 * wait milliseconds have elapsed since the last call.
 */
export function debounce<T extends AnyFunction>(func: T, wait: number): T {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return ((...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      func(...args);
    }, wait);
  }) as T;
}
