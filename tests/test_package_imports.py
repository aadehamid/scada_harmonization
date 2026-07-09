"""Skeleton smoke test: the package installs and imports under the uv-managed environment."""

import scada_harmonizer


def test_package_imports() -> None:
    assert scada_harmonizer.__doc__ is not None
