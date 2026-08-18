"""Sim-time rules for TEP and IIoT (charter §14 N8, Phase 1 L0 contract).

TEP is a 3-minute sample index, not UTC. Do not interpolate it to 1 s.
IIoT uses native UTC when present; otherwise epoch + i * 1 s.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

SIM_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
TEP_SAMPLE_PERIOD_S = 180
IIOT_FALLBACK_PERIOD_S = 1
TEP_SAMPLE_PERIOD = timedelta(seconds=TEP_SAMPLE_PERIOD_S)
IIOT_FALLBACK_PERIOD = timedelta(seconds=IIOT_FALLBACK_PERIOD_S)


def tep_sim_time(sample_index: int) -> datetime:
    """Pre-rebase sim-time for TEP sample ``i``: epoch + i * 180s."""
    return SIM_EPOCH + sample_index * TEP_SAMPLE_PERIOD


def iiot_fallback_sim_time(sample_index: int) -> datetime:
    """IIoT sim-time when the file has no native UTC column."""
    return SIM_EPOCH + sample_index * IIOT_FALLBACK_PERIOD
