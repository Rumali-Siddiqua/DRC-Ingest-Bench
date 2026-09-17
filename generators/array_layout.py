"""Repeat a layout N x N times to create a larger test case with known violations."""
import math
import sys
import klayout.db as db

src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])

layout = db.Layout()
layout.read(src)
top = layout.top_cell()
box = top.bbox()

# Step size: 20% gap, rounded up to a whole micrometre so every copy stays on grid.
um = int(round(1.0 / layout.dbu))
dx = math.ceil(box.width() * 1.2 / um) * um
dy = math.ceil(box.height() * 1.2 / um) * um

grid = layout.create_cell(f"array_{n}x{n}")
grid.insert(db.CellInstArray(
    top.cell_index(), db.Trans(),
    db.Vector(dx, 0), db.Vector(0, dy), n, n))

layout.write(out)
print(f"Wrote {out}: {n}x{n} copies of {top.name}, step {dx*layout.dbu} x {dy*layout.dbu} um")
