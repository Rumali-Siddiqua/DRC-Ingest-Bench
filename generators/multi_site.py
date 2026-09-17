"""Many independent Metal1 spacing sites. Each site: a wide wire (0.5 um) plus a second
wire at a given gap and width. Sites are far enough apart not to interact."""
import argparse
import klayout.db as db

from generators.base_layout import METAL1, DBU, to_dbu

WIDE = 0.5      # um
LENGTH = 10.0   # um, parallel run
PITCH_X = 5.0   # um; widest site is ~1.2 um, so >= 3.7 um clearance
PITCH_Y = 12.0  # um; 2 um between rows


def build(top_name, gaps, width1s, cols=10):
    if len(gaps) != len(width1s):
        raise ValueError("gaps and width1s must have the same length")
    layout = db.Layout()
    layout.dbu = DBU
    top = layout.create_cell(top_name)
    m1 = layout.layer(*METAL1)
    w, l = to_dbu(WIDE), to_dbu(LENGTH)
    px, py = to_dbu(PITCH_X), to_dbu(PITCH_Y)
    for i, (g, w1) in enumerate(zip(gaps, width1s)):
        x0, y0 = (i % cols) * px, (i // cols) * py
        top.shapes(m1).insert(db.Box(x0, y0, x0 + w, y0 + l))
        x1 = x0 + w + to_dbu(g)
        top.shapes(m1).insert(db.Box(x1, y0, x1 + to_dbu(w1), y0 + l))
    return layout


def floats(s):
    return [float(x) for x in s.split(",")]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--top", required=True)
    p.add_argument("--gaps", type=floats, required=True)
    p.add_argument("--width1s", type=floats, required=True)
    a = p.parse_args()
    build(a.top, a.gaps, a.width1s).write(a.out)
    print(f"Wrote {a.out}: {len(a.gaps)} sites")
