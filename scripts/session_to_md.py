"""
Convert a Claude Code session transcript (JSONL) into a prose-only Markdown
chat log, matching the ai-chats format: alternating ``## User`` / ``## Assistant``
sections.

Only genuine human-typed prompts and the assistant's visible reply text are
kept. Thinking blocks, tool calls, tool results, and injected system records are
dropped, so the output reads as the conversation did.

This module is intentionally standard-library only: it is invoked from a
``Stop`` / ``SessionStart`` hook, which must run even when no virtualenv is
active. See ``ai-chats/README.md`` for how it fits the wider scheme.
"""

import json
from pathlib import Path
import sys
from typing import List, Tuple

Turn = Tuple[str, str]


def _is_typed_prompt(record: dict) -> bool:
    """
    Report whether a ``user`` record is a real human-typed prompt.
    Tool results and injected system messages are also ``type == "user"`` but
    carry a list ``content`` or a non-human origin, so they are excluded.
    """
    if record.get("type") != "user":
        return False
    content = record.get("message", {}).get("content")
    if not isinstance(content, str):
        return False
    if record.get("promptSource") == "typed":
        return True
    return record.get("origin", {}).get("kind") == "human"


def _assistant_text(record: dict) -> str:
    """
    Return the concatenated visible text of an ``assistant`` record, or "".
    Non-text blocks (thinking, tool_use) contribute nothing.
    """
    if record.get("type") != "assistant":
        return ""
    content = record.get("message", {}).get("content")
    if not isinstance(content, list):
        return ""
    texts = [
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    return "\n\n".join(text for text in texts if text)


def extract_turns(records: List[dict]) -> List[Turn]:
    """
    Reduce transcript records to an ordered list of ``(role, text)`` turns.
    Consecutive assistant text blocks (across interleaved tool calls) are merged
    into a single assistant turn, so one reply stays one section.
    """
    turns: List[Turn] = []
    assistant_buffer: List[str] = []

    def flush_assistant() -> None:
        if assistant_buffer:
            turns.append(("assistant", "\n\n".join(assistant_buffer)))
            assistant_buffer.clear()

    for record in records:
        if _is_typed_prompt(record):
            flush_assistant()
            turns.append(("user", record["message"]["content"]))
            continue
        text = _assistant_text(record)
        if text:
            assistant_buffer.append(text)

    flush_assistant()
    return turns


def render_markdown(turns: List[Turn]) -> str:
    """
    Render turns as ai-chats Markdown: a ``## Role`` heading, a blank line, the
    verbatim text, then a blank line before the next section.
    """
    sections = [f"## {role.capitalize()}\n\n{text}\n" for role, text in turns]
    return "\n".join(sections)


def transcript_to_markdown(jsonl_path: Path) -> str:
    """
    Read a session JSONL file and return its prose-only Markdown transcript.
    Malformed lines are skipped rather than aborting the whole conversion.
    """
    records: List[dict] = []
    with open(jsonl_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return render_markdown(extract_turns(records))


def _usage() -> str:
    return "usage: session_to_md.py <session.jsonl> [-o OUTPUT.md]"


def main(argv: List[str]) -> int:
    """
    CLI glue: convert a transcript path to Markdown, to a file or stdout.
    """
    if not argv or argv[0] in ("-h", "--help"):
        print(_usage())
        return 0 if argv else 2
    jsonl_path = Path(argv[0])
    output_path = None
    if len(argv) >= 3 and argv[1] == "-o":
        output_path = Path(argv[2])
    if not jsonl_path.exists():
        print(f"session_to_md.py: no such file: {jsonl_path}", file=sys.stderr)
        return 1
    markdown = transcript_to_markdown(jsonl_path)
    if output_path is None:
        sys.stdout.write(markdown)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
