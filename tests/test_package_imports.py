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


def test_polars_imports_without_data_files() -> None:
    import polars as pl

    frame = pl.DataFrame({"x": [1, 2]})
    assert frame.columns == ["x"]
    assert frame.height == 2


def test_runtime_dep_is_polars_not_pandas() -> None:
    """Hamid lock: tabular work is Polars. pandas must not be a runtime dep."""
    import tomllib
    from pathlib import Path

    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text())
    deps = pyproject["project"]["dependencies"]
    assert any(dep.startswith("polars") for dep in deps)
    assert not any(dep.startswith("pandas") for dep in deps)


def test_ingest_melt_imports_polars_not_pandas() -> None:
    import scada_harmonizer.datagen.ingestion.melt as melt

    assert melt.pl.__name__ == "polars"
    assert not hasattr(melt, "pd")


def test_tests_and_datagen_do_not_import_pandas() -> None:
    import ast
    from pathlib import Path

    roots = (
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parents[1] / "src" / "scada_harmonizer",
    )
    offenders: list[str] = []
    for root in roots:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".", 1)[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".", 1)[0]]
                if "pandas" in names:
                    offenders.append(str(path))
    assert offenders == []
