#!/usr/bin/env bash
# Stop hook: refresh the complete, machine-generated backup transcript for the
# current session at ai-chats/_auto/<session-id>.md. This is the safety net that
# makes the ai-chats requirement robust even if a turn is never hand-curated.
#
# It must never block the session: any failure exits 0.

set -uo pipefail

payload=$(cat)
get() { printf '%s' "$payload" | jq -r "$1 // \"\"" 2>/dev/null; }

transcript=$(get '.transcript_path')
session=$(get '.session_id')
proj="${CLAUDE_PROJECT_DIR:-$(get '.cwd')}"

[ -z "$transcript" ] && exit 0
[ -f "$transcript" ] || exit 0
[ -n "$session" ] || session=$(basename "$transcript" .jsonl)
[ -n "$proj" ] || exit 0

out="$proj/ai-chats/_auto/${session}.md"
python3 "$proj/scripts/session_to_md.py" "$transcript" -o "$out" 2>/dev/null || true
exit 0
