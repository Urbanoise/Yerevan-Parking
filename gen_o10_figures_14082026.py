# -*- coding: utf-8 -*-
"""Re-render Figures 5 and 6 of Output 10 without the residential-yard measure and
swap them into the 14/08 rev 2 document.

Reviewer comment, 14 Aug 2026: "Disregard the alternative of using yard parking
spaces." The measure card comes out of the summary figure and the yard pill out of
the high-sensitivity band of the packages figure. remove_yard_measure.py takes it out
of the text; this takes it out of the graphics.

The drawing code is reused from gen_o10_figures_13082026 rather than copied — only
the card set, the pill set and the output paths differ. With four cards left the
summary grid goes to 2x2, which keeps the cards at a readable size on the page; at
three columns the fourth card would sit alone on a second row.
"""
import os

import gen_o10_figures_13082026 as g
import report_figures as rf
from docx import Document

CHARTS = g.CHARTS
OUT5 = os.path.join(CHARTS, "fig5_measure_summary_14082026.png")
OUT6 = os.path.join(CHARTS, "fig10_sensitivity_packages_14082026.png")
DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 14082026 (rev 2).docx")


def main():
    # Figure 5 — drop the "Open residential yards" card, re-grid to 2x2.
    g.CARDS = [c for c in g.CARDS if "residential yards" not in c[1]]
    g.COLS = 2
    g.ROWS = -(-len(g.CARDS) // g.COLS)
    g.CARD_H = max(g.card_height(t, b) for _, t, b in g.CARDS)
    g.OUT5 = OUT5

    # Figure 6 — drop the yard pill from the high-sensitivity band. It appears in no
    # other band: the 13/08 revision had already removed it from the lower band.
    for p in g.PANELS:
        if p.get("pills"):
            p["pills"] = [x for x in p["pills"] if "residential yards" not in x]
    g.OUT6 = OUT6

    g.draw_cards()
    g.draw_panels()

    doc = Document(DOC)
    g.swap(doc, "summary of the mitigation measures", OUT5)
    g.swap(doc, "grouped by sensitivity zones", OUT6)
    doc.save(DOC)
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
