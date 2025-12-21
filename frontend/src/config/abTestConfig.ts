/**
 * A/B Test Configuration - Stub
 * Always returns variant 'A' (default/only variant)
 */

export type ABTestVariant = 'A' | 'B' | 'C' | 'D';

export function getCurrentVariant(): ABTestVariant {
  return 'A';
}
