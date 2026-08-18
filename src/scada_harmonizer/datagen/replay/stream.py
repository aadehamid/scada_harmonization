"""Simulated replay clock: rebase, speed factor, pause/resume, backfill vs live.

N8 rebase is a single wall-clock offset at replay start. Backfill writes
historical sim timestamps (wall_time == record.ts_utc, speed ignored) and
never waits on the wall clock.
"""

from __future__ import annotations

import time
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta
from typing import NamedTuple, Protocol

from scada_harmonizer.datagen.records import L0Record
from scada_harmonizer.datagen.replay.identity import (
    ReplayIdentity,
    ReplayMode,
    ReplaySettings,
    assert_single_dataset,
    sort_records,
    to_identity,
)

PAUSE_POLL_S = 0.01


class WallClock(Protocol):
    def now(self) -> datetime: ...
    def sleep(self, seconds: float) -> None: ...


class SystemWallClock:
    def now(self) -> datetime:
        return datetime.now(UTC)

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class ReplayEvent(NamedTuple):
    identity: ReplayIdentity
    record: L0Record
    wall_time: datetime
    is_live: bool


class ReplayStream:
    """Time-ordered emitter for one dataset. Construction fails on mixed cadence."""

    def __init__(
        self,
        records: Sequence[L0Record],
        settings: ReplaySettings | None = None,
        clock: WallClock | None = None,
    ) -> None:
        assert_single_dataset(records)
        self._records = sort_records(records)
        self.settings = settings or ReplaySettings()
        self._clock = clock or SystemWallClock()
        self._paused = False

    @property
    def mode(self) -> ReplayMode:
        return self.settings.mode

    @property
    def is_live(self) -> bool:
        return self.settings.mode is ReplayMode.LIVE

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def identity_list(self) -> list[ReplayIdentity]:
        return [to_identity(row) for row in self._records]

    def emit(self) -> Iterator[ReplayEvent]:
        if not self._records:
            return
        first_sim = self._records[0].ts_utc
        if self.settings.mode is ReplayMode.BACKFILL:
            for record in self._records:
                yield ReplayEvent(
                    identity=to_identity(record),
                    record=record,
                    wall_time=record.ts_utc,
                    is_live=False,
                )
            return
        origin = self.settings.rebase_origin or self._clock.now()
        speed = self.settings.speed_factor
        for record in self._records:
            while self._paused:
                self._clock.sleep(PAUSE_POLL_S)
            sim_delta_s = (record.ts_utc - first_sim).total_seconds() / speed
            wall = origin + timedelta(seconds=sim_delta_s)
            delay = (wall - self._clock.now()).total_seconds()
            if delay > 0:
                self._clock.sleep(delay)
            yield ReplayEvent(
                identity=to_identity(record),
                record=record,
                wall_time=wall,
                is_live=True,
            )
