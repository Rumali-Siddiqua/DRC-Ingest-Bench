"""Deliberately off-grid array: copies at 1.2x cell pitch trigger Offgrid markers (one root cause)."""
import sys
import klayout.db as db

src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])

layout = db.Layout()
layout.read(src)
top = layout.top_cell()

box = top.bbox()
dx = int(box.width() * 1.2)   # 20% gap so copies don't interact
dy = int(box.height() * 1.2)

grid = layout.create_cell(f"array_{n}x{n}")
grid.insert(db.CellInstArray(
    top.cell_index(), db.Trans(),
    db.Vector(dx, 0), db.Vector(0, dy), n, n))

layout.write(out)
print(f"Wrote {out}: {n}x{n} copies of {top.name}")
