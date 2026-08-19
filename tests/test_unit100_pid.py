"""Unit 100 Rev B one-pager + 59-name tag list. No network. No second factory."""

from __future__ import annotations

import hashlib
from pathlib import Path

import polars as pl

from scada_harmonizer.datagen.augmentation.extras import DEFAULT_EXTRAS
from scada_harmonizer.datagen.generation.machine_stream import (
    DEFAULT_MACHINES,
    MACHINE_STREAM_PVS,
)

PID_DIR = Path(__file__).resolve().parent / "fixtures" / "datagen" / "pid"
PID_PDF = PID_DIR / "LSC-U100-PID-001_revB.pdf"
TAG_SCHEDULE = PID_DIR / "tag_schedule.csv"
PID_PDF_SHA256 = "dd75cc078110e1f5b519dcf3024832d932d996daa14d0e4607d8ac6d2276179f"

PLANT_DATA_NAMES: frozenset[str] = frozenset(
    [f"xmeas_{i}" for i in range(1, 42)]
    + [f"xmv_{i}" for i in range(1, 12)]
    + [
        f"{machine.machine_id}/{pv}"
        for machine in DEFAULT_MACHINES
        for pv in MACHINE_STREAM_PVS
    ]
    + ["xv_feed"]
)


def _schedule() -> pl.DataFrame:
    return pl.read_csv(TAG_SCHEDULE, infer_schema_length=0)


def test_unit100_pdf_is_the_uploaded_rev_b() -> None:
    assert PID_PDF.is_file()
    digest = hashlib.sha256(PID_PDF.read_bytes()).hexdigest()
    assert digest == PID_PDF_SHA256


def test_tag_schedule_has_exactly_the_59_l0_names() -> None:
    frame = _schedule()
    names = set(frame["plant_data_name"].to_list())
    assert len(PLANT_DATA_NAMES) == 59
    assert names == PLANT_DATA_NAMES
    assert frame.height == 59


def test_drawing_name_is_one_to_one() -> None:
    frame = _schedule()
    assert frame["drawing_name"].n_unique() == frame.height
    assert frame["plant_data_name"].n_unique() == frame.height


def test_controllers_and_hold_are_not_rows() -> None:
    names = _schedule()["drawing_name"].to_list()
    assert not any(name.startswith(("FC-", "LC-", "TC-")) for name in names)
    assert "HOLD" not in names


def test_no_lots_or_business_ids() -> None:
    blob = TAG_SCHEDULE.read_text(encoding="utf-8").lower()
    for forbidden in ("lot", "work_order", "workorder", "material_id"):
        assert forbidden not in blob


def test_printed_analyzer_and_machine_join() -> None:
    frame = _schedule()
    by_drawing = dict(zip(frame["drawing_name"], frame["plant_data_name"], strict=True))
    assert by_drawing["AT-201"] == "xmeas_23"
    assert by_drawing["AT-219"] == "xmeas_41"
    assert by_drawing["VI-101"] == "P-101/vibration_rms"
    assert by_drawing["SI-201"] == "K-201/shaft_speed_rpm"
    assert by_drawing["XV-101"] == "xv_feed"
    assert "xv_feed" in {spec.friendly_name for spec in DEFAULT_EXTRAS}


def test_xv_feed_and_machines_match_generators() -> None:
    assert {m.machine_id for m in DEFAULT_MACHINES} == {"P-101", "K-201"}
    assert MACHINE_STREAM_PVS == ("vibration_rms", "motor_current_a", "shaft_speed_rpm")
