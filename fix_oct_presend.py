# -*- coding: utf-8 -*-
"""OCT'26 copies of Output 8 / Output 10: pre-send consistency fixes (15 Oct 2026).

Text, in black (no red), at the user's request:
  * O10: no mention of a third corridor ("three priority corridors" -> "the two
    priority corridors"; the Corridor 3 / 896-space sentence removed).
  * O8: Gai Avenue no longer described as "near Mega Mall".
  * O8: "the full 34 km" -> "the full 30 km" (11.66 + 19.19 km; the exec summary says 30).
  * Both: "mid-week" dropped - Komitas was surveyed on a Friday and Shiraz on a Monday.
Figure 6 of O10 re-rendered: the Gai Avenue "kerb parking stays for now" exception box
is gone (Output 8 removes all 132 Gai spaces), and the high band gains the charged
resident permit that the text assigns to it.

Edits the saved files in place; replaced text takes the formatting of the run it
lands in, so hand edits and existing colours are kept.

Usage: python fix_oct_presend.py
"""
import os

from docx import Document

import docx_edit as dx
import gen_o10_figures_13082026 as fig
import report_figures as rf

OCT = os.path.join(rf.ROOT, "Final Presentation", "OCT'26")
O8 = os.path.join(OCT, "Output 8 - Parking Surveys and Analysis Report 15102026 (rev).docx")
O10 = os.path.join(OCT, "Output 10 - Parking Analysis Report 15102026 (rev).docx")
FIG6 = os.path.join(OCT, "charts", "o10_fig6_sensitivity_packages_15102026.png")


def replace_plain(par, old, new):
    """Replace the first `old` in a paragraph with `new`, written into the run where
    the match starts (so it keeps that run's formatting); other runs only lose the
    characters of `old` they held."""
    runs = par.runs
    text = "".join(r.text for r in runs)
    start = text.find(old)
    if start < 0:
        raise ValueError(f"not found: {old!r}")
    end = start + len(old)
    pos, first = 0, True
    for run in runs:
        r0, r1 = pos, pos + len(run.text)
        pos = r1
        if r1 <= start or r0 >= end:
            continue
        t = run.text
        a, b = max(start, r0) - r0, min(end, r1) - r0
        run.text = t[:a] + (new if first else "") + t[b:]
        first = False
    after = "".join(r.text for r in par.runs)
    assert after == text[:start] + new + text[end:], (old, after[:120])


def output8():
    doc = Document(O8)
    replace_plain(dx.find(doc, "rather than the full 34 km"), "the full 34 km", "the full 30 km")
    replace_plain(dx.find(doc, "(Gai Avenue near Mega Mall)"), " near Mega Mall", "")
    replace_plain(dx.find(doc, "four separate ordinary mid-week working days"),
                  "ordinary mid-week working days", "ordinary working days")
    doc.save(O8)
    print("saved", O8)


def output10():
    doc = Document(O10)
    replace_plain(dx.find(doc, "along three priority corridors"),
                  "along three priority corridors", "along the two priority corridors")
    replace_plain(dx.find(doc, "Corridor 3 is withheld from the assessment"),
                  " Corridor 3 is withheld from the assessment pending its conceptual design; "
                  "for the record the inventory found a further 896 on-corridor spaces along it.",
                  "")
    replace_plain(dx.find(doc, "on ordinary mid-week working days"),
                  "on ordinary mid-week working days", "on ordinary working days")

    fig.OUT6 = FIG6
    fig.PANELS = [
        dict(title="High sensitivity", accent="#d32f2f", bg="#fdecea", ink="#b71c1c",
             streets="Kentron CBD: Nalbandyan, Amiryan, Tigran Mets  ·  Komitas Avenue",
             pills=["Extend paid zones", "Resident permits (1 per household)",
                    "Visitor caps", "Organise free parking"]),
        dict(title="Medium sensitivity", accent="#f57c00", bg="#fff7e8", ink="#8a5300",
             streets="Arshakunyats, Kievyan, Garegin Nzhdeh",
             pills=["Extend paid zones", "Organise free parking"]),
        dict(title="Lower sensitivity", accent="#2e7d32", bg="#e9f5ea", ink="#1b5e20",
             streets="Bagratunyats, Sebastia, Raffi, Rubinyants, Nor Nork, Sasna Tsrer",
             pills=["Organise free parking"]),
    ]
    os.makedirs(os.path.dirname(FIG6), exist_ok=True)
    fig.draw_panels()
    dx.swap_figure_above(doc, "Mitigation measures grouped by sensitivity zones", FIG6)

    for needle in ("Corridor 3", "three priority", "mid-week", "Mega Mall"):
        if dx.find_all(doc, needle):
            print("O10 CHECK", needle)
    doc.save(O10)
    print("saved", O10)


if __name__ == "__main__":
    output8()
    output10()
