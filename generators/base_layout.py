"""Clean Metal1 base layout: N parallel wires that satisfy all Metal1 rules by design."""
import argparse
import klayout.db as db

METAL1 = (8, 0)   # confirmed in layers_def.drc
DBU = 0.001       # 1 nm database unit
GRID_NM = 5       # manufacturing grid; verified by the Offgrid rules reporting 0


def to_dbu(value_um):
    v = round(value_um / DBU)
    if v % GRID_NM:
        raise ValueError(f"{value_um} um is not on the {GRID_NM} nm grid")
    return v


def build(wires, width, length, space, top_name):
    layout = db.Layout()
    layout.dbu = DBU
    top = layout.create_cell(top_name)
    m1 = layout.layer(*METAL1)
    w, l, s = to_dbu(width), to_dbu(length), to_dbu(space)
    for i in range(wires):
        x = i * (w + s)
        top.shapes(m1).insert(db.Box(x, 0, x + w, l))
    return layout


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--top", default="base")
    p.add_argument("--wires", type=int, default=5)
    p.add_argument("--width", type=float, default=0.5)
    p.add_argument("--length", type=float, default=10.0)
    p.add_argument("--space", type=float, default=2.0)
    a = p.parse_args()
    build(a.wires, a.width, a.length, a.space, a.top).write(a.out)
    print(f"Wrote {a.out}")
