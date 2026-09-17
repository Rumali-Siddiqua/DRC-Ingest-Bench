"""Split a .lyrdb into header tokens and per-item tokens."""
import sys
import re
from pathlib import Path
import tiktoken

enc = tiktoken.get_encoding("cl100k_base")
text = Path(sys.argv[1]).read_text(encoding="utf-8")

items = re.findall(r"<item>.*?</item>", text, flags=re.S)
values = re.findall(r"<value>(.*?)</value>", text, flags=re.S)
items_start = text.find("<items>")
header = text[:items_start] if items_start != -1 else text

header_tok = len(enc.encode(header))
item_tok = sum(len(enc.encode(i)) for i in items)
value_tok = sum(len(enc.encode(v)) for v in values)

print(f"Header tokens:            {header_tok:,}")
print(f"Item tokens (total):      {item_tok:,}")
print(f"Items:                    {len(items)}")
if items:
    print(f"Tokens per item:          {item_tok / len(items):.1f}")
    print(f"Geometry tokens per item: {value_tok / len(items):.1f}")
    print(f"Overhead share of items:  {100 * (1 - value_tok / item_tok):.0f}%")
