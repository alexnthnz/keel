#!/usr/bin/env bash
# Show how upstream pstack changed since keel's base commit, or apply that
# change to this checkout. Sparse, blob-less clone of cursor/plugins into a
# temp dir, then a diff of pstack/ between the base commit and upstream.
#
# Usage: bin/upstream-diff.sh [upstream-ref]           log and stat (default ref: main)
#        bin/upstream-diff.sh --apply [upstream-ref]   3-way apply onto this checkout
#        KEEP=1 bin/upstream-diff.sh ...               keep the clone to read full diffs
#        CLONE=<dir> bin/upstream-diff.sh ...          reuse a kept clone
#        BASE=<commit> bin/upstream-diff.sh ...        diff from another upstream commit
set -euo pipefail

base="${BASE:-ce649c03ac3b75b6ae80cbd15b7e2c536caedb5a}"
removed=(.cursor-plugin assets docs/guide/images automations/benny skills/make-bot-ui skills/poteto-help plugin.json)
apply=
if [ "${1:-}" = --apply ]; then
	apply=1
	shift
fi
ref="${1:-main}"
repo=https://github.com/cursor/plugins.git
root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/pstack-upstream.XXXXXX")"
clone="${CLONE:-$tmp/clone}"
if [ -n "${KEEP:-}" ]; then
	echo "clone kept at $clone" >&2
else
	trap 'rm -rf "$tmp"' EXIT
fi

if [ -z "${CLONE:-}" ]; then
	git clone --quiet --filter=blob:none --no-checkout --sparse "$repo" "$clone"
	git -C "$clone" sparse-checkout set pstack
fi
git -C "$clone" fetch --quiet origin "$ref"
head="$(git -C "$clone" rev-parse FETCH_HEAD)"

echo "cursor/plugins pstack/ changes, ${base:0:7}..$ref (${head:0:7})"
if [ -z "$apply" ]; then
	git -C "$clone" log --oneline "$base..$head" -- pstack/
	echo
	git -C "$clone" diff --stat "$base" "$head" -- pstack/
	exit
fi

patch="$tmp/pstack.patch"
git -C "$clone" diff --binary --full-index --no-renames --no-prefix --relative=pstack \
	"$base" "$head" -- pstack "${removed[@]/#/:(exclude)pstack/}" |
	awk '
		/^diff --git / { header = 1 }
		/^@@ / || /^GIT binary patch/ { header = 0 }
		header {
			gsub(/ skills\/poteto-mode\//, " skills/lead/")
			gsub(/ skills\/setup-pstack\//, " skills/setup/")
			gsub(/ agents\/poteto-agent\.md/, " agents/ponytail.md")
			gsub(/ agents\/comment-sicko\.md/, " agents/critic.md")
			gsub(/ docs\/guide\/02-poteto-mode\.md/, " docs/guide/02-lead.md")
		}
		{ print }
	' >"$patch"
if [ ! -s "$patch" ]; then
	echo "nothing to apply"
	exit 0
fi

# A 3-way apply merges against the base blob named in each index line.
# keel's history holds only the blobs of its own base, so copy in the rest.
awk '/^index / { split($2, ids, /\.\./); if (ids[1] !~ /^0+$/) print ids[1] }' "$patch" |
	while read -r blob; do
		git -C "$root" cat-file -e "$blob" 2>/dev/null ||
			git -C "$clone" cat-file blob "$blob" | git -C "$root" hash-object -w --stdin >/dev/null
	done
git -C "$root" apply --3way -p0 "$patch"
