#!/usr/bin/env python3
"""Five Seconds to Explain the Glass (make.fun program/v1).

Writes the one sentence a house cat would say in its own defence after
sweeping a glass off the table, to /output/entry.txt.

Stdlib only: no network, no file reads, no local imports, no fonts.
The sentence is a constant: the program's only job is to validate it
against the gate (1-200 characters, one sentence, not whitespace-only)
and write it atomically.
"""
from __future__ import annotations

import os
import sys

SENTENCE = (
    "The glass spent all morning hogging my sunbeam and judging my naps, "
    "so I evicted it \u2014 the floor has no opinions and plenty of room."
)
MAX_CHARS = 200


def validate(text: str) -> str:
    """Enforce the gate: 1-200 characters, one sentence, not blank."""
    if not text or not text.strip():
        raise ValueError("sentence must not be empty or whitespace-only")
    if len(text) > MAX_CHARS:
        raise ValueError(
            f"sentence is {len(text)} chars, over the {MAX_CHARS} limit"
        )
    if "\n" in text or "\r" in text:
        raise ValueError("sentence must be a single line")
    if text.count(".") != 1 or not text.endswith("."):
        raise ValueError("sentence must be exactly one sentence")
    if "?" in text or "!" in text:
        raise ValueError("sentence must be one flat statement, no ? or !")
    return text


def output_path() -> str:
    """Where the sentence goes: argv[1], $MAKEFUN_OUTPUT_DIR, or /output."""
    if len(sys.argv) > 1:
        return os.path.join(sys.argv[1], "entry.txt")
    base = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(base, "entry.txt")


def main() -> int:
    text = validate(SENTENCE)
    path = output_path()
    data = text.encode("utf-8")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Write atomically: temp file in the same directory, then rename, so a
    # reader never sees a half-written sentence. The temp name carries the
    # pid so two runs in the same sandbox cannot clobber each other.
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)
    with open(path, "rb") as fh:
        back = fh.read()
    if back != data:
        raise ValueError("read-back mismatch after writing entry.txt")
    print(f"wrote {len(text)} chars to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
