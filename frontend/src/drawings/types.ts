import type { Time } from 'lightweight-charts';

export type LineStyle = 'solid' | 'dashed' | 'dotted';
export type DrawingKind = 'trendline' | 'ray' | 'horizontal';

export interface Tp {
  time: Time;
  price: number;
}

export interface BaseDrawing {
  id: string;
  kind: DrawingKind;
  color?: string;
  width?: number; // px
  style?: LineStyle;
  selected?: boolean;
  name?: string; // optional legend label
  visible?: boolean;
}

export interface Trendline extends BaseDrawing {
  kind: 'trendline';
  a: Tp;
  b: Tp;
}

export interface Ray extends BaseDrawing {
  kind: 'ray';
  a: Tp;
  b: Tp; // slope from a->b; render extends to edge
  direction?: 'right' | 'left' | 'both';
}

export interface Horizontal extends BaseDrawing {
  kind: 'horizontal';
  price: number; // y
  t0?: Time;
  t1?: Time; // optional visible bounds (else full width)
  draggable?: boolean; // enable drag-move
  rotation?: number; // rotation angle in degrees (0-360), default 0
}

export type AnyDrawing = Trendline | Ray | Horizontal;

export function uid(prefix = 'drw'): string {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

export function normalizeStyle(d: Partial<AnyDrawing>) {
  return {
    color: d.color ?? '#ffa500',
    width: d.width ?? 2,
    style: (d.style ?? 'solid') as LineStyle
  };
}
