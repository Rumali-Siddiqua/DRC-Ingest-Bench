"""Run the IHP SG13G2 KLayout DRC on a GDS file and return marker counts per rule."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import klayout.rdb as rdb

PDK_ROOT = Path(os.environ.get("IHP_PDK_ROOT", Path.home() / "pdks" / "IHP-Open-PDK"))
DRC_SCRIPT = PDK_ROOT / "ihp-sg13g2/libs.tech/klayout/tech/drc/run_drc.py"

# Fixed deck options: every task records and reuses exactly these.
DECK_OPTIONS = ["--no_density", "--run_mode=flat"]


def run_drc(gds, topcell, run_dir):
    """Run DRC and return ({rule: count}, report_path). Only rules with markers are listed."""
    run_dir = Path(run_dir)
    shutil.rmtree(run_dir, ignore_errors=True)
    cmd = [sys.executable, str(DRC_SCRIPT), f"--path={gds}", f"--topcell={topcell}",
           f"--run_dir={run_dir}", *DECK_OPTIONS]
    # run_drc.py exits non-zero when violations exist, so the exit code is not checked.
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "drc_stdout.txt", "w") as out, open(run_dir / "drc_stderr.txt", "w") as err:
        subprocess.run(cmd, stdout=out, stderr=err)

    reports = sorted(run_dir.glob("*.lyrdb"))
    if not reports:
        raise RuntimeError(f"No report produced in {run_dir}. Run the command by hand to see the error:\n"
                           + " ".join(cmd))

    db = rdb.ReportDatabase("")
    db.load(str(reports[0]))
    counts = {c.name(): c.num_items() for c in db.each_category() if c.num_items()}
    return counts, reports[0]


if __name__ == "__main__":
    gds, topcell, run_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    counts, report = run_drc(gds, topcell, run_dir)
    for rule, n in sorted(counts.items()):
        print(f"  {rule:25s} {n}")
    print(f"TOTAL: {sum(counts.values())}  ({report})")
