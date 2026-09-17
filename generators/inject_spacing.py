"""Inject one Metal1 spacing violation: wire 1 is moved so its gap to wire 0 equals --gap.
Optionally wire 1 gets its own width (--width1), e.g. to make it narrow."""
import argparse
import klayout.db as db

from generators.base_layout import METAL1, DBU, to_dbu


def build(gap, top_name, width1=0.5, wires=5, width=0.5, length=10.0, space=2.0):
    layout = db.Layout()
    layout.dbu = DBU
    top = layout.create_cell(top_name)
    m1 = layout.layer(*METAL1)
    w, w1, l, s, g = (to_dbu(v) for v in (width, width1, length, space, gap))
    xs = [i * (w + s) for i in range(wires)]
    widths = [w] * wires
    xs[1], widths[1] = w + g, w1   # the injected root cause
    for x, wd in zip(xs, widths):
        top.shapes(m1).insert(db.Box(x, 0, x + wd, l))
    return layout


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--top", required=True)
    p.add_argument("--gap", type=float, required=True)
    p.add_argument("--width1", type=float, default=0.5)
    a = p.parse_args()
    build(a.gap, a.top, a.width1).write(a.out)
    print(f"Wrote {a.out} (gap {a.gap} um, wire 1 width {a.width1} um)")
