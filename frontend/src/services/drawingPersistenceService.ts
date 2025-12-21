/**
 * Drawing Persistence Service
 * Handles saving/loading drawings to/from the database
 * Transforms between frontend format (kind) and API format (type)
 */

import type { AnyDrawing, Trendline, Ray, Horizontal } from '../drawings/types';

// Use dedicated drawing API URL if provided, otherwise fall back to standalone server on 8001
const API_BASE = import.meta.env.VITE_DRAWING_API_URL || 'http://localhost:8001';
const DRAWING_API = `${API_BASE}/api/drawings`;

// API format (what the database expects)
interface ApiDrawingData {
  name?: string;
  visible?: boolean;
  selected?: boolean;
  color?: string;
  width?: number;
  style?: 'solid' | 'dashed' | 'dotted';
  coordinates?: Record<string, any>;
  price?: number;
  t0?: number;
  t1?: number;
  rotation?: number;
  draggable?: boolean;
  direction?: string;
}

interface ApiDrawing {
  id?: string;
  symbol: string;
  type: 'trendline' | 'ray' | 'horizontal' | 'fibonacci' | 'support' | 'resistance';
  data: ApiDrawingData;
  conversation_id?: string | null;
  user_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

/**
 * Transform frontend drawing to API format
 */
function toApiFormat(drawing: AnyDrawing, symbol: string): ApiDrawing {
  const base: ApiDrawing = {
    symbol: symbol.toUpperCase(),
    type: drawing.kind, // 'kind' becomes 'type'
    data: {
      name: drawing.name,
      visible: drawing.visible,
      selected: drawing.selected,
      color: drawing.color,
      width: drawing.width,
      style: drawing.style,
    }
  };

  // Add kind-specific data
  switch (drawing.kind) {
    case 'trendline':
      base.data.coordinates = {
        a: { time: drawing.a.time, price: drawing.a.price },
        b: { time: drawing.b.time, price: drawing.b.price }
      };
      break;

    case 'ray':
      base.data.coordinates = {
        a: { time: drawing.a.time, price: drawing.a.price },
        b: { time: drawing.b.time, price: drawing.b.price },
        direction: drawing.direction || 'right'
      };
      break;

    case 'horizontal':
      base.data.price = drawing.price;
      base.data.t0 = drawing.t0 as number | undefined;
      base.data.t1 = drawing.t1 as number | undefined;
      base.data.rotation = drawing.rotation;
      base.data.draggable = drawing.draggable;
      break;
  }

  return base;
}

/**
 * Transform API format to frontend drawing
 */
function fromApiFormat(apiDrawing: ApiDrawing): AnyDrawing {
  const base = {
    id: apiDrawing.id || '',
    kind: apiDrawing.type as 'trendline' | 'ray' | 'horizontal',
    name: apiDrawing.data.name,
    visible: apiDrawing.data.visible,
    selected: apiDrawing.data.selected,
    color: apiDrawing.data.color,
    width: apiDrawing.data.width,
    style: apiDrawing.data.style,
  };

  // Add kind-specific data
  switch (apiDrawing.type) {
    case 'trendline': {
      const coords = apiDrawing.data.coordinates as { a: { time: number; price: number }; b: { time: number; price: number } };
      return {
        ...base,
        kind: 'trendline',
        a: coords.a,
        b: coords.b,
      } as Trendline;
    }

    case 'ray': {
      const coords = apiDrawing.data.coordinates as { a: { time: number; price: number }; b: { time: number; price: number }; direction?: string };
      return {
        ...base,
        kind: 'ray',
        a: coords.a,
        b: coords.b,
        direction: coords.direction as 'right' | 'left' | 'both' | undefined,
      } as Ray;
    }

    case 'horizontal':
      return {
        ...base,
        kind: 'horizontal',
        price: apiDrawing.data.price || 0,
        t0: apiDrawing.data.t0 as any,
        t1: apiDrawing.data.t1 as any,
        rotation: apiDrawing.data.rotation,
        draggable: apiDrawing.data.draggable,
      } as Horizontal;

    default:
      throw new Error(`Unknown drawing type: ${apiDrawing.type}`);
  }
}

/**
 * Drawing Persistence Service
 */
export const drawingPersistenceService = {
  /**
   * Load all drawings for a symbol
   */
  async loadDrawings(symbol: string): Promise<AnyDrawing[]> {
    try {
      const response = await fetch(`${DRAWING_API}?symbol=${symbol.toUpperCase()}`);

      if (!response.ok) {
        throw new Error(`Failed to load drawings: ${response.statusText}`);
      }

      const data = await response.json();
      return data.drawings.map((d: ApiDrawing) => fromApiFormat(d));
    } catch (error) {
      console.error('Error loading drawings:', error);
      return []; // Return empty array on error, don't break the UI
    }
  },

  /**
   * Save a single drawing
   */
  async saveDrawing(drawing: AnyDrawing, symbol: string): Promise<string | null> {
    try {
      const apiDrawing = toApiFormat(drawing, symbol);

      const response = await fetch(DRAWING_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiDrawing)
      });

      if (!response.ok) {
        throw new Error(`Failed to save drawing: ${response.statusText}`);
      }

      const saved = await response.json();
      return saved.id;
    } catch (error) {
      console.error('Error saving drawing:', error);
      return null;
    }
  },

  /**
   * Save multiple drawings (batch)
   */
  async saveDrawings(drawings: AnyDrawing[], symbol: string): Promise<boolean> {
    try {
      const apiDrawings = drawings.map(d => toApiFormat(d, symbol));

      const response = await fetch(`${DRAWING_API}/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(apiDrawings)
      });

      return response.ok;
    } catch (error) {
      console.error('Error saving drawings:', error);
      return false;
    }
  },

  /**
   * Delete a drawing
   */
  async deleteDrawing(id: string): Promise<boolean> {
    try {
      const response = await fetch(`${DRAWING_API}/${id}`, {
        method: 'DELETE'
      });

      return response.ok;
    } catch (error) {
      console.error('Error deleting drawing:', error);
      return false;
    }
  },

  /**
   * Clear all drawings for a symbol
   */
  async clearAllDrawings(symbol: string): Promise<boolean> {
    try {
      const response = await fetch(`${DRAWING_API}?symbol=${symbol.toUpperCase()}`, {
        method: 'DELETE'
      });

      return response.ok;
    } catch (error) {
      console.error('Error clearing drawings:', error);
      return false;
    }
  }
};
