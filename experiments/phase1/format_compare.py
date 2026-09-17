"""Compare the same DRC violations as raw XML, compact JSON, and TOON."""
import json
import sys
from pathlib import Path

import klayout.rdb as rdb
import tiktoken
import toon

enc = tiktoken.get_encoding("cl100k_base")


def toon_encode(data):
    for name in ("encode", "dumps", "to_toon", "serialize"):
        fn = getattr(toon, name, None)
        if callable(fn):
            return fn(data)
    raise RuntimeError(f"no encoder found in toon: {[m for m in dir(toon) if not m.startswith('_')]}")


def records(path):
    db = rdb.ReportDatabase("")
    db.load(str(path))
    rows = []
    for cat in db.each_category():
        if not cat.num_items():
            continue
        for item in db.each_item_per_category(cat.rdb_id()):
            for v in item.each_value():
                rows.append({"rule": cat.name(), "cell": db.cell_by_id(item.cell_id()).name(),
                             "geometry": v.to_s()})
    return rows


path = Path(sys.argv[1])
rows = records(path)

raw_tok = len(enc.encode(path.read_text(encoding="utf-8")))
json_txt = json.dumps({"violations": rows}, separators=(",", ":"))
toon_txt = toon_encode({"violations": rows})
json_tok, toon_tok = len(enc.encode(json_txt)), len(enc.encode(toon_txt))

print(f"markers: {len(rows)}\n")
print(f"{'form':16s} {'tokens':>10s} {'% of raw':>9s} {'tok/marker':>11s}")
for name, tok in (("raw .lyrdb XML", raw_tok), ("compact JSON", json_tok), ("TOON", toon_tok)):
    per = f"{tok/len(rows):.1f}" if rows else "-"
    print(f"{name:16s} {tok:10,d} {100*tok/raw_tok:8.1f}% {per:>11s}")
print(f"\nTOON vs JSON: {100*(1-toon_tok/json_tok):.1f}% fewer tokens")
print("\n--- first 300 chars of TOON ---")
print(toon_txt[:300])
