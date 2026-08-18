"""Skeleton smoke test: the package installs and imports under the uv-managed environment."""

import scada_harmonizer
import scada_harmonizer.datagen
import scada_harmonizer.datagen.augmentation
import scada_harmonizer.datagen.ingestion
import scada_harmonizer.datagen.replay


def test_package_imports() -> None:
    assert scada_harmonizer.__doc__ is not None


def test_phase1_datagen_packages_import() -> None:
    """Phase 1 subpackages are regular packages so SDG can add modules later."""
    for module in (
        scada_harmonizer.datagen,
        scada_harmonizer.datagen.ingestion,
        scada_harmonizer.datagen.augmentation,
        scada_harmonizer.datagen.replay,
    ):
        assert module.__file__ is not None
        assert module.__file__.endswith("__init__.py")


def test_pandas_imports_without_data_files() -> None:
    import pandas as pd

    frame = pd.DataFrame({"x": [1, 2]})
    assert list(frame.columns) == ["x"]
    assert len(frame) == 2
