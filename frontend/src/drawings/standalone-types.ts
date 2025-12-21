export interface TrendlineCoordinates {
  a: { time: number; price: number };
  b: { time: number; price: number };
}

export interface TrendlineOptions {
  name?: string;
  color?: string;
  width?: number;
}

export interface Trendline {
  id: string;
  symbol: string;
  type: 'trendline';
  data: {
    name: string;
    color: string;
    width: number;
    style: 'solid' | 'dashed' | 'dotted';
    visible: boolean;
    coordinates: TrendlineCoordinates;
  };
}

export interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}
