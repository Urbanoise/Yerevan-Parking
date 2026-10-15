"""Swap a re-rendered Figure 22 (on-street absorptive capacity) into the saved 15 Oct
Output 8, in place. apply_o8_oct_edits.py re-rendered every other chart but left this
one at the pre-Bagratunyats retained total (1,220); report_figures now gives 1,252.

Edits the saved file directly so hand edits survive; only the picture changes.

Usage: python fix_o8_fig22.py
"""
import os

from docx import Document

import docx_edit as dx
import gen_o8_report_figures as g
import report_figures as rf

OCT = os.path.join(rf.ROOT, "Final Presentation", "OCT'26")
DOC = os.path.join(OCT, "Output 8 - Parking Surveys and Analysis Report 15102026 (rev).docx")
g.OUT = os.path.join(OCT, "charts")


def main():
    s = rf.supply()
    assert s["retained"] == 1252, s["retained"]
    path = g.fig8_onstreet(s)
    doc = Document(DOC)
    dx.swap_figure_above(doc, "Available absorptive capacity (on-street)", path)
    doc.save(DOC)
    print("swapped", os.path.basename(path), "| retained", s["retained"],
          "| cross-street", s["cross_street"])


if __name__ == "__main__":
    main()
