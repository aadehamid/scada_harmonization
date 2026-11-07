#!/usr/bin/env bash
# Keep this repo's stable engine separate from other projects' Dagger versions.
set -euo pipefail

version=v0.21.11
engine=scada-dagger-engine-$version
cli="${DAGGER_BIN:-$HOME/.local/share/dagger/$version/dagger}"
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"

if [[ ! -x "$cli" ]]; then
  printf 'Install Dagger %s at %s, or set DAGGER_BIN to that release.\n' "$version" "$cli" >&2
  exit 1
fi
if [[ "$("$cli" version)" != "dagger $version "* ]]; then
  printf 'This project requires Dagger %s.\n' "$version" >&2
  exit 1
fi

if ! docker container inspect "$engine" >/dev/null 2>&1; then
  docker run --name "$engine" --detach --restart unless-stopped --privileged \
    --volume "scada-dagger-cache-$version:/var/lib/dagger" \
    "registry.dagger.io/engine:$version" >/dev/null
elif [[ "$(docker inspect --format '{{.State.Running}}' "$engine")" != true ]]; then
  docker start "$engine" >/dev/null
fi

export _EXPERIMENTAL_DAGGER_RUNNER_HOST="docker-container://$engine"

# Dagger's Ignore filter does not inherit Git's ignore rules. Filter before upload.
snapshot="$(mktemp -d "${TMPDIR:-/tmp}/scada-dagger.XXXXXX")"
trap 'rm -rf -- "$snapshot"' EXIT
git -C "$repo" ls-files -z --cached --others --exclude-standard |
  while IFS= read -r -d '' path; do
    if [[ -e "$repo/$path" || -L "$repo/$path" ]]; then
      printf '%s\0' "$path"
    fi
  done |
  tar -C "$repo" --null --no-recursion --files-from - -cf - |
  tar -C "$snapshot" -xf -
"$cli" --mod "$snapshot" "$@"
