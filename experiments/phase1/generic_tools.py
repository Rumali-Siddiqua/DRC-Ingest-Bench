"""Run generic LLM-transformation tools on a real DRC report and measure what they change."""
import sys
from pathlib import Path

import tiktoken
from markitdown import MarkItDown

enc = tiktoken.get_encoding("cl100k_base")
path = Path(sys.argv[1])
raw = path.read_text(encoding="utf-8")

out = MarkItDown().convert(str(path)).text_content
raw_tok, out_tok = len(enc.encode(raw)), len(enc.encode(out))

print(f"raw tokens:        {raw_tok:,}")
print(f"markitdown tokens: {out_tok:,}  ({100*out_tok/raw_tok:.0f}% of raw)")
print(f"still contains coordinates: {'edge-pair' in out}")
print("\n--- first 500 chars of output ---")
print(out[:500])
