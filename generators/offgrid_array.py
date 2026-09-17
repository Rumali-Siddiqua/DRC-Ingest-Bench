"""Array of a clean Metal1 cell placed at an off-grid pitch.
One root cause (the array step) produces every marker in the report."""
import argparse
import klayout.db as db

from generators.base_layout import METAL1, DBU, GRID_NM, to_dbu

WIRES, WIDTH, LENGTH, SPACE = 5, 0.5, 10.0, 2.0


def build(top_name, n, step_x_um, step_y_um):
    """n x n copies of a clean cell at the given pitch. Off-grid pitch -> Offgrid markers."""
    layout = db.Layout()
    layout.dbu = DBU
    m1 = layout.layer(*METAL1)

    cell = layout.create_cell("clean_unit")
    w, l, s = to_dbu(WIDTH), to_dbu(LENGTH), to_dbu(SPACE)
    for i in range(WIRES):
        x = i * (w + s)
        cell.shapes(m1).insert(db.Box(x, 0, x + w, l))

    # Deliberately NOT snapped: to_dbu would reject an off-grid value.
    dx, dy = round(step_x_um / DBU), round(step_y_um / DBU)
    top = layout.create_cell(top_name)
    top.insert(db.CellInstArray(cell.cell_index(), db.Trans(),
                                db.Vector(dx, 0), db.Vector(0, dy), n, n))
    return layout


def on_grid(value_um):
    return round(value_um / DBU) % GRID_NM == 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--top", required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--step_x_um", type=float, required=True)
    p.add_argument("--step_y_um", type=float, required=True)
    a = p.parse_args()
    build(a.top, a.n, a.step_x_um, a.step_y_um).write(a.out)
    grid = "on grid" if on_grid(a.step_x_um) and on_grid(a.step_y_um) else "OFF GRID"
    print(f"Wrote {a.out}: {a.n}x{a.n} at {a.step_x_um} x {a.step_y_um} um ({grid})")
