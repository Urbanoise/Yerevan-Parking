# -*- coding: utf-8 -*-
"""Remove the residential-yard-opening measure from Output 10 entirely.

Reviewer comment, 14 Aug 2026: "Disregard the alternative of using yard parking
spaces." The measure therefore comes out of the measure chapter, the sensitivity-zone
package, the further-studies list and the two mitigation figures, and every statement
that leaned on yard capacity as a mitigation resource is restated without it.

Works on a COPY, so the 14/08 revision that the comment was raised against stays
intact for comparison.

Two classes of yard reference are deliberately NOT touched, because they are survey
findings rather than the measure: descriptions of where parking currently stands
(sheds and lock-up garages between the Corridor 2 blocks, demand spreading onto
courtyards and green space) and the off-street inventory scope. Removing those would
delete measured facts, not a recommendation.

The absorption arithmetic is the one place where this is more than deletion. The
displacement block in field-surveys.geojson carries two rates: nearby ON-STREET
capacity alone (35% of peak displaced demand citywide) and on-street plus off-street
yards (100%). The report already quotes the on-street figures in the places where it
gives numbers (10% Kentron, 0% Komitas), so those stand unchanged; only the caveat
that described the figures as counting "yards as if already open" had to be rewritten,
and it now states the real remaining best-case assumption — gross, not spare, capacity
on streets that were never occupancy-surveyed.
"""
import os
import re
import shutil

from docx import Document

import docx_edit as dx
import report_figures as rf

PRES = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(PRES, "Output 10 - Parking Analysis Report - 14082026 (rev).docx")
DST = os.path.join(PRES, "Output 10 - Parking Analysis Report - 14082026 (rev 2).docx")


def span_sub(par, pattern, repl):
    """Regex-replace inside a paragraph even when Word has split the match over
    several runs; the first touched run keeps its formatting, so the edit inherits
    the surrounding text's colour rather than being marked as an addition."""
    m = re.search(pattern, par.text)
    if not m:
        raise LookupError(f"no match for {pattern[:60]!r} in: {par.text[:80]!r}")
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
    return par


def main():
    shutil.copyfile(SRC, DST)
    doc = Document(DST)

    # 1. the whole "Open Residential yards" measure in chapter 5 — heading, the two
    #    descriptive paragraphs, the international precedents, the organisational
    #    options and the dedicated-study paragraph.
    dx.drop_range(dx.find(doc, "Open Residential yards"),
                  dx.find(doc, "A dedicated implementation study"))

    # 2. the high-sensitivity package in "Mitigation Measure Packages by Sensitivity
    #    Zones" — the yard pill and its block-by-block feasibility qualifier.
    span_sub(dx.find(doc, "the recommended measures are the strongest ones"),
             r"extending paid zones, opening residential yards where feasible \(courtyard "
             r"layout, resolved land ownership and the consent of the building association "
             r"all may vary block by block\), charged",
             "extending paid zones, charged")

    # 3. further studies — drop it from the supporting-studies list, and with it the
    #    closing sentence that asked for a dedicated study on who should administer it.
    fs = dx.find(doc, "Supporting studies on residential yard opening")
    span_sub(fs, r"Supporting studies on residential yard opening, the legal basis of the "
                 r"resident permit scheme, and willingness-to-pay",
             "Supporting studies on the legal basis of the resident permit scheme and "
             "willingness-to-pay")
    span_sub(fs, r"\s*The administration of residential-yard opening in particular [-–—] "
                 r"who should lead it and under what organisational and legal arrangement [-–—] "
                 r"warrants a dedicated study before any roll-out\.", "")

    # 4. the survey-caveat in "Limitations and Residual Risks". The old parenthesis
    #    described the absorption figures as counting yards as if already open; with
    #    the yards disregarded the remaining best-case assumption is gross capacity on
    #    streets that were never occupancy-surveyed, which is what it now says.
    span_sub(dx.find(doc, "the absorption figures are gross best-case"),
             r"and the absorption figures are gross best-case \(yards counted as if already "
             r"open\)\.",
             "and the absorption figures are gross best-case, counting the total capacity "
             "of the nearby streets rather than the share of it actually free at the peak "
             "hour, because those streets were not themselves occupancy-surveyed.")

    # 5. the measured recalibration paragraph: Kentron's constraint no longer reads as
    #    off-street-led, and the Gai residual is stated against nearby capacity as a
    #    whole instead of against filling every yard. Gai holds either way — nearby
    #    on-street capacity covers 68% of its peak displaced demand.
    rec = dx.find(doc, "Measured recalibration (field survey)")
    span_sub(rec, r"Kentron is confirmed high-sensitivity \(138% peak\) but for an "
                  r"off-street-led reason: only",
             "Kentron is confirmed high-sensitivity (138% peak), and the constraint is "
             "acute: only")
    span_sub(rec, r"even filling every nearby off-street yard to capacity leaves a residual",
             "even the whole of the nearby capacity, counted at its theoretical maximum, "
             "leaves a residual")

    # 6. the two survey-chapter sentences that offered yards as a basis for mitigation.
    span_sub(dx.find(doc, "the cross-street and yard inventory demonstrates"),
             r"the cross-street and yard inventory demonstrates",
             "the cross-street inventory demonstrates")
    span_sub(dx.find(doc, "the surrounding street network and off-street yards may provide"),
             r"the surrounding street network and off-street yards may provide",
             "the surrounding street network may provide")

    doc.save(DST)
    print("saved:", os.path.basename(DST))


if __name__ == "__main__":
    main()
