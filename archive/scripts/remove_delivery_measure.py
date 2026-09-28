"""Remove the delivery/loading-bay measure from Output 10 entirely.

The measure is dropped from the programme, so it comes out of the measure chapter,
the best-practice review, the phasing list, the conclusions and the institutional
responsibility table. The truck-share statistic goes with it: it existed only to
size the delivery bays and has no other home in the report.

Output 8 carries no delivery or loading references at all and is not touched.

Edits the 13/08 revision in place (it carries hand edits made after the
reviewer-comment scripts ran, so it is not regenerated). Backup alongside.
"""
import os
import shutil

from docx import Document

import docx_edit as dx
import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 13082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-delivery-removal).docx")


def span_sub(par, old, new):
    """Replace `old` with `new` inside a paragraph even when Word has split it over
    several runs; the first touched run keeps its formatting."""
    text = par.text
    i = text.find(old)
    if i < 0:
        raise LookupError(f"not found: {old[:60]!r}")
    j, pos, first = i + len(old), 0, True
    for run in par.runs:
        s, e = pos, pos + len(run.text)
        pos = e
        if e <= i or s >= j:
            continue
        head = run.text[: max(0, i - s)]
        tail = run.text[max(0, j - s):] if j < e else ""
        run.text = head + (new if first else "") + tail
        first = False
    return par


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)

    # 1. the whole "Delivery spaces" measure block in chapter 5, plus one of the two
    #    blank paragraphs that would otherwise be left stacked
    head = dx.find(doc, "Delivery spaces")
    tail = dx.find(doc, "Field-survey verdict: confirmed by the short-access dominance")
    prev = head._p.getprevious()
    dx.drop_range(head, tail)
    if prev is not None and not "".join(prev.itertext()).strip():
        prev.getparent().remove(prev)

    # 2. the loading-and-servicing-zones paragraph in the best-practice review
    dx.drop(dx.find(doc, "Designated loading and servicing zones must be integrated"))

    # 3. enforcement paragraph
    span_sub(dx.find(doc, "zoned parking controls and time-limited loading bays"),
             "zoned parking controls and time-limited loading bays",
             "zoned parking controls")

    # 4. phase 1 of the phasing list
    span_sub(dx.find(doc, "designate and sign loading and servicing zones"),
             "designate and sign loading and servicing zones, and launch public",
             "and launch public")

    # 5. + 6. the two conclusions bullets
    span_sub(dx.find(doc, "loading bays sized to the measured freight pockets"),
             "loading bays sized to the measured freight pockets, organised free parking",
             "organised free parking")
    span_sub(dx.find(doc, "Paid-zone expansion, resident permits, loading bays"),
             "Paid-zone expansion, resident permits, loading bays, visitor caps",
             "Paid-zone expansion, resident permits, visitor caps")

    # 7. institutional responsibility table row
    for t in doc.tables:
        for row in list(t.rows):
            if row.cells[0].text.strip().startswith("Delivery bays sized"):
                row._tr.getparent().remove(row._tr)

    # 8. visitor caps no longer follows the delivery measure
    span_sub(dx.find(doc, "Closely related to the previous point is the use of visitor caps"),
             "Closely related to the previous point is the use of visitor caps",
             "A second measure is the use of visitor caps")

    doc.save(DOC)
    print("backup:", os.path.basename(BAK))
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
