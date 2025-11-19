import { AnyDrawing, uid } from './types';

type Listener = () => void;

export class DrawingStore {
  private map = new Map<string, AnyDrawing>();
  private subs = new Set<Listener>();

  subscribe(fn: Listener) { this.subs.add(fn); return () => this.subs.delete(fn); }
  private emit() { for (const fn of this.subs) fn(); }

  all(): AnyDrawing[] { return [...this.map.values()]; }
  get(id: string) { return this.map.get(id); }

  upsert(d: AnyDrawing) {
    if (!d.id) d.id = uid();
    // clone to avoid accidental external mutation
    this.map.set(d.id, JSON.parse(JSON.stringify(d)));
    this.emit();
    return d.id;
  }

  remove(id: string) {
    this.map.delete(id);
    this.emit();
  }

  clear() { this.map.clear(); this.emit(); }

  select(id?: string) {
    for (const d of this.map.values()) d.selected = !!id && d.id === id;
    this.emit();
  }

  import(list: AnyDrawing[]) {
    this.map.clear();
    for (const d of list) this.map.set(d.id, d);
    this.emit();
  }

  export(): AnyDrawing[] { return this.all(); }
}
