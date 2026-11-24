"""
Tests for the session-transcript to Markdown converter.
"""

import json
from pathlib import Path

from scripts.session_to_md import extract_turns, render_markdown, transcript_to_markdown


def _typed_user(text: str) -> dict:
    """
    Build a transcript record for a human-typed prompt.
    """
    return {
        "type": "user",
        "promptSource": "typed",
        "origin": {"kind": "human"},
        "message": {"role": "user", "content": text},
    }


def _assistant_block(block_type: str, text: str) -> dict:
    """
    Build a single-block assistant record (text, thinking, or tool_use).
    """
    block = {"type": block_type}
    if block_type == "text":
        block["text"] = text
    elif block_type == "thinking":
        block["thinking"] = text
    else:
        block["name"] = text
    return {"type": "assistant", "message": {"role": "assistant", "content": [block]}}


def _tool_result() -> dict:
    """
    Build a user record that is actually a tool result, not a typed prompt.
    """
    return {
        "type": "user",
        "toolUseResult": {"ok": True},
        "message": {"role": "user", "content": [{"type": "tool_result"}]},
    }


def test_extract_turns_pairs_prompts_with_assistant_prose():
    records = [
        _typed_user("Hello"),
        _assistant_block("thinking", "hmm"),
        _assistant_block("text", "Hi there"),
        _assistant_block("tool_use", "Bash"),
        _tool_result(),
        _assistant_block("text", "Done."),
        _typed_user("Bye"),
    ]

    turns = extract_turns(records)

    assert turns == [
        ("user", "Hello"),
        ("assistant", "Hi there\n\nDone."),
        ("user", "Bye"),
    ]


def test_extract_turns_skips_injected_non_typed_user_records():
    records = [
        {
            "type": "user",
            "promptSource": "system",
            "origin": {"kind": "system"},
            "message": {
                "role": "user",
                "content": "<system-reminder>noise</system-reminder>",
            },
        },
        _typed_user("Real prompt"),
        _assistant_block("text", "Reply"),
    ]

    turns = extract_turns(records)

    assert turns == [("user", "Real prompt"), ("assistant", "Reply")]


def test_render_markdown_format():
    turns = [
        ("user", "Hello"),
        ("assistant", "Hi there\n\nDone."),
        ("user", "Bye"),
    ]

    md = render_markdown(turns)

    assert md == (
        "## User\n\nHello\n\n"
        "## Assistant\n\nHi there\n\nDone.\n\n"
        "## User\n\nBye\n"
    )


def test_transcript_to_markdown_reads_jsonl(tmp_path: Path):
    records = [_typed_user("Hi"), _assistant_block("text", "Hello back")]
    jsonl = tmp_path / "session.jsonl"
    jsonl.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")

    md = transcript_to_markdown(jsonl)

    assert md == "## User\n\nHi\n\n## Assistant\n\nHello back\n"
