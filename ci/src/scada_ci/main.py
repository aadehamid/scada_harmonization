from typing import Annotated

import dagger
from dagger import DefaultPath, Ignore, check, dag, function, object_type

# Allow project inputs, not the host checkout's Git history or local agent state.
SOURCE_FILTER = [
    "**",
    "!.github/",
    "!.github/**",
    "!.gitignore",
    "!.python-version",
    "!AGENTS.md",
    "!HANDOFF.md",
    "!LICENSE",
    "!README.md",
    "!REVIEW_STANDARDS.md",
    "!dagger.json",
    "!dagger.toml",
    "!pyproject.toml",
    "!ty.toml",
    "!uv.lock",
    "!ci/",
    "!ci/**",
    "!config/",
    "!config/**",
    "!docker/",
    "!docker/**",
    "!docs/",
    "!docs/**",
    "!notebooks/",
    "!notebooks/**",
    "!scripts/",
    "!scripts/**",
    "!src/",
    "!src/**",
    "!tests/",
    "!tests/**",
    "!data/",
    "!data/README.md",
    "!data/cache/",
    "!data/cache/README.md",
    "!data/raw/",
    "!data/raw/README.md",
    "!reference/",
    "!reference/README.md",
    "**/.git",
    "**/.venv",
    "**/__pycache__",
    "**/.pytest_cache",
    "**/.ruff_cache",
    "**/.env",
    "**/.env.*",
    "ci/sdk",
    "reference/**",
    "!reference/README.md",
    "data/**",
    "!data/README.md",
    "!data/cache/README.md",
    "!data/raw/README.md",
]


@object_type
class ScadaCi:
    @function
    @check
    async def project(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Ignore(SOURCE_FILTER)],
    ) -> None:
        """Run scripts/check.sh with locked dependencies and an isolated Git index."""
        uv = dag.container().from_("ghcr.io/astral-sh/uv:0.13.7")
        dependencies = (
            dag.container()
            .from_("python:3.13.9-slim-bookworm")
            .with_exec(
                ["sh", "-c", "apt-get update && apt-get install -y --no-install-recommends git"]
            )
            .with_file("/usr/local/bin/uv", uv.file("/uv"))
            .with_workdir("/work")
            .with_file("pyproject.toml", source.file("pyproject.toml"))
            .with_file("uv.lock", source.file("uv.lock"))
            .with_file(".python-version", source.file(".python-version"))
            .with_exec(["uv", "sync", "--frozen", "--group", "dev", "--no-install-project"])
        )
        await (
            dependencies.with_directory("/work", source)
            .with_exec(["uv", "sync", "--frozen", "--group", "dev"])
            .with_exec(["git", "init", "--initial-branch=main"])
            .with_exec(["git", "add", "--all"])
            .with_exec(["bash", "scripts/check.sh"])
            .sync()
        )
