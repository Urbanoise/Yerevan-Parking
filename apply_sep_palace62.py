# -*- coding: utf-8 -*-
"""Palace lot capacity 32 -> 62 (user, 30 Sep 2026; Livia Delgado's comment on the
Palace lot's 115% average occupancy, Output 8).

The 32 was an area estimate (962 m2 at 30 m2 per car); the survey found 62 cars on the
lot at 16:00 and 50-62 on eight of the ten rounds between 10:00 and 19:00. The lot is
both the Gai Avenue surveyed facility and one of the 239 inventory facilities, so the
change runs through both (convert_field_surveys.mjs KML_YARDS + parking-areas.geojson,
then the full regeneration chain):

  off-street supply  6,732 -> 6,762     impact-area total 14,557 -> 14,587
  surveyed facilities  427 -> 457       weighted average  52% -> 48%
  Palace  avg 115% -> 59%, busiest hour 194% -> 100%
  unchanged at the precision quoted: 33% removed of all parking, courtyards 83%,
  displacement and absorption (surveyed facilities are excluded from absorption).

Edits both STS response copies in place; changed numbers only, in red. Re-renders the
two affected charts (removal share of the impact area; off-street absorptive capacity)
and swaps them in above their captions. Adds the reply under Livia's comment.

Run:  python apply_sep_palace62.py            (dry run)
      python apply_sep_palace62.py --apply
"""
import copy
import sys

from docx import Document
from docx.text.run import Run

import gen_o8_figures_24082026 as g24
import gen_o8_report_figures as g
import report_figures as rf
from apply_o8_sep_comments import DST as O8
from apply_o8_sep_zone_table import comment_id
from docx_edit import RED, find_styled

import build_o10_logit_responses as o10

O10 = o10.DST
REPLY = ("Agreed. The 32 spaces were an estimate from the lot's mapped area; the survey "
         "found 62 cars there at 16:00. Capacity corrected to 62: average 59%, busiest "
         "hour 100%. Supply totals updated accordingly (off-street 6,762, total 14,587).")


def red_replace(par, old, new):
    """Replace `old` with red `new` inside `par`, splitting only the run that holds it."""
    for run in par.runs:
        if old in run.text:
            before, after = run.text.split(old, 1)
            run.text = before
            red = copy.deepcopy(run._r)
            run._r.addnext(red)
            rr = Run(red, par)
            rr.text = new
            rr.font.color.rgb = RED
            tail = copy.deepcopy(run._r)
            red.addnext(tail)
            Run(tail, par).text = after
            return True
    if old in par.text:
        raise SystemExit(f"{old!r} straddles runs in: {par.text[:80]!r}")
    return False


def replace_all(pars, old, new, expect):
    n = 0
    for p in pars:
        while red_replace(p, old, new):
            n += 1
    if n != expect:
        raise SystemExit(f"{old!r}: replaced {n}, expected {expect}")


def cell_pars(doc):
    for t in doc.tables:
        for row in t.rows:
            seen = set()
            for c in row.cells:
                if id(c._tc) in seen:
                    continue
                seen.add(id(c._tc))
                yield from c.paragraphs


def row_of(doc, first_cell):
    hits = [r for t in doc.tables for r in t.rows if r.cells[0].text.strip() == first_cell]
    if len(hits) != 1:
        raise SystemExit(f"{len(hits)} rows start with {first_cell!r}")
    return hits[0]


def edit_o8(doc):
    body = doc.paragraphs
    replace_all(body, "14,557", "14,587", 4)          # 108, 194, 312, 315
    replace_all(body, "6,732", "6,762", 6)            # 108, 194, 290 x2, 313, 316
    replace_all(list(cell_pars(doc)), "14,557", "14,587", 1)   # Table 1 total
    replace_all(list(cell_pars(doc)), "6,732", "6,762", 3)     # Table 1 total + yards row

    p = next(p for p in body if p.text.startswith("Measured off-street occupancy (field survey)"))
    red_replace(p, "427", "457")
    red_replace(p, "about 52% full", "about 48% full")
    red_replace(p, "(Palace 194%, Nalbandyan 142%, Komitas City 101%)",
                "(Nalbandyan 142%, Komitas City 101%, Palace 100%)")

    rows = [r for t in doc.tables for r in t.rows if len(r.cells) > 1
            and r.cells[1].text.strip() == "Palace lot"]
    if len(rows) != 1:
        raise SystemExit("Palace row not found")
    cells = rows[0].cells
    for c, old, new in ((cells[2], "32", "62"), (cells[3], "115%", "59%"), (cells[4], "194%", "100%")):
        if not red_replace(c.paragraphs[0], old, new):
            raise SystemExit(f"Palace cell {old!r} not found")
    tot = row_of(doc, "All six (total / weighted avg.)").cells
    for c, old, new in ((tot[2], "427", "457"), (tot[3], "52%", "48%")):
        if not red_replace(c.paragraphs[0], old, new):
            raise SystemExit(f"total cell {old!r} not found")

    s = rf.supply()
    assert (s["off_street"], s["total"]) == (6762, 14587), s
    assert rf.yards()["total_spaces"] == 457 and rf.yards()["weighted_avg_pct"] == 48
    g24.swap(doc, "parking removed as a share of the impact area", g24.fig_removal_share(s))
    g24.swap(doc, "available absorptive capacity (off-street)", g.fig7_offstreet(s))


def edit_o10(doc):
    replace_all(doc.paragraphs, "14,557", "14,587", 1)
    replace_all(doc.paragraphs, "6,732", "6,762", 1)


def main(apply):
    d8, d10 = Document(O8), Document(O10)
    edit_o8(d8)
    edit_o10(d10)
    if not apply:
        print("dry run OK - nothing saved")
        return
    d8.save(O8)
    d10.save(O10)
    o10.REPLIES = {comment_id(O8, "Livia Delgado", "Palace lot's average occupancy"): REPLY}
    o10.add_replies(O8)
    print("saved", O8, "\nsaved", O10)


if __name__ == "__main__":
    main("--apply" in sys.argv)
