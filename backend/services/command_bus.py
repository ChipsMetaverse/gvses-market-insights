# backend/services/command_bus.py
from __future__ import annotations
import time
from typing import Deque, Dict, List, Optional, Tuple
from collections import deque, defaultdict
from threading import RLock
from pydantic import BaseModel
from models.chart_command import ChartCommand  # existing


class ChartCommandEnvelope(BaseModel):
    seq: int
    timestamp: float
    command: ChartCommand


class _ChannelState:
    __slots__ = ("seq", "queue")

    def __init__(self):
        self.seq = 0
        self.queue: Deque[Tuple[int, float, ChartCommand]] = deque()


class CommandBus:
    """In-memory, per-channel FIFO with TTL; fine for single Fly.io instance."""

    def __init__(self, ttl_seconds: int = 600, max_items: int = 1000):
        self._ttl = ttl_seconds
        self._max = max_items
        self._channels: Dict[str, _ChannelState] = defaultdict(_ChannelState)
        self._lock = RLock()

    def publish(self, channel: str, cmd: ChartCommand) -> ChartCommandEnvelope:
        now = time.time()
        with self._lock:
            st = self._channels[channel]
            st.seq += 1
            st.queue.append((st.seq, now, cmd))
            self._purge(st)
            return ChartCommandEnvelope(seq=st.seq, timestamp=now, command=cmd)

    def fetch(self, channel: str, after_seq: Optional[int] = None, limit: int = 50) -> Tuple[List[ChartCommandEnvelope], int]:
        with self._lock:
            st = self._channels[channel]
            self._purge(st)
            items: List[ChartCommandEnvelope] = []
            last_seq = after_seq or 0
            for seq, ts, cmd in st.queue:
                if seq > (after_seq or 0):
                    items.append(ChartCommandEnvelope(seq=seq, timestamp=ts, command=cmd))
                    last_seq = seq
                    if len(items) >= limit:
                        break
            if not items:
                last_seq = st.seq
            return items, last_seq

    def _purge(self, st: _ChannelState):
        cutoff = time.time() - self._ttl
        while st.queue and (st.queue[0][1] < cutoff or len(st.queue) > self._max):
            st.queue.popleft()
