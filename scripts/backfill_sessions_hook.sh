#!/usr/bin/env bash
# SessionStart hook: ensure every past session in this project's transcript
# directory has a backup under ai-chats/_auto/. This is the "reach back and save
# earlier sessions" guarantee. It only fills gaps; the Stop hook keeps the live
# session current.
#
# It must never block the session: any failure exits 0.

set -uo pipefail

payload=$(cat)
get() { printf '%s' "$payload" | jq -r "$1 // \"\"" 2>/dev/null; }

transcript=$(get '.transcript_path')
proj="${CLAUDE_PROJECT_DIR:-$(get '.cwd')}"

[ -z "$transcript" ] && exit 0
[ -n "$proj" ] || exit 0

dir=$(dirname "$transcript")
mkdir -p "$proj/ai-chats/_auto"

shopt -s nullglob
for f in "$dir"/*.jsonl; do
  id=$(basename "$f" .jsonl)
  out="$proj/ai-chats/_auto/${id}.md"
  [ -f "$out" ] && continue
  python3 "$proj/scripts/session_to_md.py" "$f" -o "$out" 2>/dev/null || true
done
exit 0
