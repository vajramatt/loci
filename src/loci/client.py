"""Thin wrapper around the official Anthropic SDK.

The API key is read from the environment ONLY, at runtime — never written to disk,
never logged. loci prefers its OWN variable, LOCI_ANTHROPIC_KEY, so it is isolated
from the shared ANTHROPIC_API_KEY that other tools read and sometimes clobber; it
falls back to ANTHROPIC_API_KEY for convenience. The `anthropic` import is local
to the functions so the rest of loci (and the test suite) does not require the SDK.
"""

from __future__ import annotations

import os
from typing import List, Optional

MAX_TOKENS = 4096

# Checked in order; the first non-empty one wins.
API_KEY_ENV_VARS = ("LOCI_ANTHROPIC_KEY", "ANTHROPIC_API_KEY")


class MissingKeyError(Exception):
    pass


def get_api_key() -> str:
    for var in API_KEY_ENV_VARS:
        key = os.environ.get(var)
        if key:
            return key
    raise MissingKeyError(
        "No API key found. loci reads it from the environment (never stored).\n"
        "  Preferred — loci's own variable, isolated from other tools:\n"
        '    export LOCI_ANTHROPIC_KEY="sk-ant-..."\n'
        "  Fallback — the shared Anthropic variable:\n"
        '    export ANTHROPIC_API_KEY="sk-ant-..."'
    )


def make_client():
    import anthropic  # local import: keeps the SDK optional for non-API code paths
    return anthropic.Anthropic(api_key=get_api_key())


def stream_assistant(client, model: str, system: str, messages: List[dict],
                     tools: List[dict], ui, max_tokens: int = MAX_TOKENS) -> List[dict]:
    """Stream one assistant message; print its text; return its content blocks
    as plain JSON-serializable dicts (text and tool_use)."""
    blocks: List[dict] = []
    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
        tools=tools,
    ) as stream:
        for text in stream.text_stream:
            ui.agent(text)
        final = stream.get_final_message()

    printed_text = False
    for block in final.content:
        if block.type == "text":
            blocks.append({"type": "text", "text": block.text})
            printed_text = True
        elif block.type == "tool_use":
            blocks.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    if printed_text:
        ui.line("")  # newline after streamed speech
    return blocks
