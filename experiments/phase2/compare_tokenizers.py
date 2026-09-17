"""Count tokens in the same reports with three different tokenizers."""
import sys
from pathlib import Path

import tiktoken
from tokenizers import Tokenizer

cl100k = tiktoken.get_encoding("cl100k_base")
o200k = tiktoken.get_encoding("o200k_base")
qwen = Tokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

print(f"{'report':45s} {'cl100k':>12s} {'o200k':>12s} {'qwen2.5':>12s}")
for path in sys.argv[1:]:
    text = Path(path).read_text(encoding="utf-8")
    a = len(cl100k.encode(text))
    b = len(o200k.encode(text))
    c = len(qwen.encode(text).ids)
    print(f"{path[-45:]:45s} {a:12,d} {b:12,d} {c:12,d}")
