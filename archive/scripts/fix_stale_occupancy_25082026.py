# -*- coding: utf-8 -*-
"""Retire the last two survivals of the old sum-of-zone-peaks occupancy basis, IN PLACE.

Both reports now compute area occupancy at a single busiest clock hour. Two passages
were written against the superseded capacity-weighted basis (each zone at its OWN peak
hour, summed) and were missed when the basis changed:

  1. Output 8, Table 7 "Impact by Sensitivity Zone" - the Key Concern column still
     carries Kentron 138%, Komitas 123%, Garegin Nzhdeh 92%, Shiraz/Hasratyan 75% and
     Malatia-Sebastia 54%. That is the entire old series, and 138% is the specific
     figure the 12 August review could not replicate. Table 9, eleven pages later,
     gives 89 / 83 / 63 / 42 / 35 for the same six areas.
  2. Output 10, para 162 - "Malatia-Sebastia ... (54% peak)", contradicted two
     paragraphs later by "35% at its busiest hour".

Only the occupancy percentages are stale; the absorption percentages in the same cells
(10%, 0%, 30%, 69%, 97%) are current and are left alone.

Every replacement inherits the formatting of the run it lands in, so text already
accepted into black stays black. Values come from report_figures, not typed by hand.
Backups are written first, and each edit is checked before it is applied so the script
is safe to re-run.
"""
import os
import re
import shutil

from docx import Document

import report_figures as rf

A = rf.survey()["areas"]
P = {k: A[k]["peak_hour_pct"] for k in A}

O8 = os.path.join(rf.ROOT, "Final Presentation",
                  "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")
O10 = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 25082026 (rev).docx")
SUFFIX = " (pre-stale-occupancy-fix).docx"


def sub_in_place(par, pattern, repl):
    """Regex-replace across runs, keeping each touched run's own formatting."""
    m = re.search(pattern, par.text)
    if not m:
        return False
    i, j, first = m.start(), m.end(), True
    pos = 0
    for run in par.runs:
        s, e = pos, pos + len(run.text)
        pos = e
        if e <= i or s >= j:
            continue
        head = run.text[: max(0, i - s)]
        tail = run.text[max(0, j - s):] if j < e else ""
        run.text = head + (m.expand(repl) if first else "") + tail
        first = False
    return True


def cell_paragraphs(doc):
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def fix_o8():
    bak = O8.replace(".docx", SUFFIX)
    shutil.copyfile(O8, bak)
    doc = Document(O8)
    done, skipped = [], []

    # Table 7, three Key Concern cells. Anchored on the "Field survey:" lead-in that
    # only these cells carry, so the table index is never hard-coded.
    edits = [
        ("high",
         r"Kentron 138% peak with only 10% absorbable on-street; Komitas 123% peak "
         r"with 0% on-street absorption",
         "Kentron %d%% at its busiest hour with only 10%% absorbable on-street; "
         "Komitas %d%% with 0%% on-street absorption" % (P["kentron"], P["komitas"])),
        ("medium",
         r"Garegin Nzhdeh 92% peak / 30% absorption",
         "Garegin Nzhdeh %d%% at its busiest hour / 30%% absorption" % P["garegin"]),
        ("lower",
         r"Shiraz/Hasratyan 75% / 69%, Malatia-Sebastia 54% / 97%",
         "Shiraz/Hasratyan %d%% / 69%%, Malatia-Sebastia %d%% / 97%%"
         % (P["shiraz"], P["malatia"])),
    ]
    for label, pat, rep in edits:
        hit = False
        for p in cell_paragraphs(doc):
            if "Field survey:" in p.text and sub_in_place(p, re.escape(pat).replace(r"\ ", " "), rep):
                hit = True
                break
        (done if hit else skipped).append("Table 7, %s-sensitivity row" % label)

    doc.save(O8)
    return bak, done, skipped


def fix_o10():
    bak = O10.replace(".docx", SUFFIX)
    shutil.copyfile(O10, bak)
    doc = Document(O10)
    done, skipped = [], []

    p = next((x for x in doc.paragraphs
              if "records the lowest daytime kerb pressure" in x.text), None)
    if p is not None and sub_in_place(
            p, r"\(54% peak\)", "(%d%% at its busiest hour)" % P["malatia"]):
        done.append("para 162, Malatia-Sebastia peak figure")
    else:
        skipped.append("para 162, Malatia-Sebastia peak figure")

    doc.save(O10)
    return bak, done, skipped


def main():
    print("basis: single busiest clock hour per area")
    print("  " + ", ".join("%s %d%%" % (A[k]["label"], P[k]) for k in
                           ["kentron", "komitas", "garegin", "shiraz", "malatia"]))
    for name, fn in (("Output 8", fix_o8), ("Output 10", fix_o10)):
        bak, done, skipped = fn()
        print("\n%s  (backup: %s)" % (name, os.path.basename(bak)))
        for d in done:
            print("   applied:", d)
        for s in skipped:
            print("   SKIPPED (already fixed or wording moved):", s)


if __name__ == "__main__":
    main()
