"""Measure what an LLM would pay to read a DRC marker database and log."""
import sys
from pathlib import Path

import klayout.rdb as rdb
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return len(text), len(enc.encode(text))


def measure_report(path):
    db = rdb.ReportDatabase("")
    db.load(str(path))

    print(f"Report: {path}")
    total = 0
    for cat in db.each_category():
        n = cat.num_items()
        if n:
            print(f"  {cat.name():20s} {n:6d} markers")
            total += n

    chars, tokens = count_tokens(path)
    print(f"  Total markers:  {total:,}")
    print(f"  File size:      {chars / 1024:.1f} KB")
    print(f"  Tokens:         {tokens:,}")
    if total:
        print(f"  Tokens/marker:  {tokens / total:.1f}")


def measure_log(path):
    chars, tokens = count_tokens(path)
    print(f"\nLog: {path}")
    print(f"  File size:      {chars / 1024:.1f} KB")
    print(f"  Tokens:         {tokens:,}")


if __name__ == "__main__":
    measure_report(sys.argv[1])
    if len(sys.argv) > 2:
        measure_log(sys.argv[2])
