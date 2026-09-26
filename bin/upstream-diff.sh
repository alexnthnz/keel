#!/usr/bin/env bash
# Show how upstream pstack changed since this port's base commit.
# Sparse, blob-less clone of cursor/plugins into a temp dir, then
# `git diff --stat` of pstack/ between the base commit and upstream.
#
# Usage: bin/upstream-diff.sh [upstream-ref]   (default: main)
#        KEEP=1 bin/upstream-diff.sh           (keep the clone to read full diffs)
set -euo pipefail

base=12d587d
ref="${1:-main}"
repo=https://github.com/cursor/plugins.git
tmp="$(mktemp -d "${TMPDIR:-/tmp}/pstack-upstream.XXXXXX")"
if [ -n "${KEEP:-}" ]; then
	echo "clone kept at $tmp" >&2
else
	trap 'rm -rf "$tmp"' EXIT
fi

git clone --quiet --filter=blob:none --no-checkout --sparse "$repo" "$tmp"
git -C "$tmp" sparse-checkout set pstack
git -C "$tmp" fetch --quiet origin "$ref"
head="$(git -C "$tmp" rev-parse --short FETCH_HEAD)"

echo "cursor/plugins pstack/ changes, $base..$ref ($head)"
git -C "$tmp" log --oneline "$base..FETCH_HEAD" -- pstack/
echo
git -C "$tmp" diff --stat "$base" FETCH_HEAD -- pstack/
