# -*- coding: utf-8 -*-
"""Qualify the residential-yard measure in the sensitivity-zone paragraphs.

Figure 6 labels the yard-opening pill "(where feasible)" in both the high and lower
sensitivity bands, and the measure section itself says the idea needs piloting and a
dedicated feasibility study before roll-out. The zone paragraphs did not carry that
qualification: the high-sensitivity one listed yard opening flatly among "the
strongest" measures, and the lower-sensitivity one did not mention yards at all even
though the figure showed a pill for them.

The two bands are qualified on their own terms rather than with one shared formula.
In the centre the courtyards are load-bearing - Kentron and Komitas can re-absorb only
8% and 0% of their displaced demand on nearby streets - so the constraint is whether a
given courtyard can be opened at all. The outer segments have on-street headroom and
do not depend on the yards to balance, and the brokered-access model needs paying
demand that a kerb peaking in the fifties does not generate, so the measure is no
longer put forward for that band at all - in the text or on the figure.

Each addition is written as a unit that can be deleted whole - a clause inside the
existing list item for the high band, a single sentence for the lower one - so that if
the yard measure is dropped from the programme nothing is left stranded.

Edits the 13/08 revision in place (it carries hand edits made after the
reviewer-comment scripts ran, so it is not regenerated). Backup alongside.
"""
import copy
import os
import shutil

from docx import Document
from docx.oxml.ns import qn
from docx.shared import RGBColor

import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 13082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-yard-feasibility).docx")

EDITS = [
    # paragraph opener, anchor run, runs to skip past, stable lead, text to add
    ("The high-sensitivity zone covers", " opening residential yards", 0,
     " where feasible (",
     " where feasible (courtyard layout, resolved land ownership and the consent "
     "of the building association all vary block by block),"),
]


# The lower-sensitivity band carried a courtyard sentence for a while. It came out
# again: with the kerb there under little pressure there is no paying demand for
# brokered courtyard access, so the measure has no purchase in those segments.
WITHDRAWN = [("The lower-sensitivity zone includes",
              " The opening of residential courtyards applies here as well,")]


def insert_red_after(par, anchor, skip, text):
    """Add `text` as a new red run just after the run holding `anchor` (plus `skip`
    further runs), so the surrounding wording keeps the colour the redline pass gave
    it."""
    runs = par.runs
    ref = runs[next(i for i, r in enumerate(runs) if r.text == anchor) + skip]
    new = copy.deepcopy(ref._r)
    ref._r.addnext(new)
    for t in new.findall(qn("w:t")):
        new.remove(t)
    el = new.makeelement(qn("w:t"), {})
    el.set(qn("xml:space"), "preserve")
    el.text = text
    new.append(el)
    next(r for r in par.runs if r._r is new).font.color.rgb = RGBColor(0xC0, 0x00, 0x00)


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)

    for opener, anchor, skip, lead, text in EDITS:
        par = next(p for p in doc.paragraphs if p.text.startswith(opener))
        # `lead` identifies a run this script added on an earlier run, so re-running
        # after a wording change rewrites that sentence instead of adding a second one
        existing = next((r for r in par.runs if r.text.startswith(lead)), None)
        if existing is None and not any(r.text == anchor for r in par.runs):
            # neither the addition nor its anchor survives: the passage has been
            # edited by hand in Word, so leave it exactly as the author left it
            print("HAND-EDITED, skipped:", opener)
        elif existing is None:
            insert_red_after(par, anchor, skip, text)
            print("ADDED:  ", opener)
        elif existing.text == text:
            print("CURRENT:", opener)
        else:
            existing.text = text
            print("REWROTE:", opener)

    for opener, lead in WITHDRAWN:
        par = next(p for p in doc.paragraphs if p.text.startswith(opener))
        gone = next((r for r in par.runs if r.text.startswith(lead)), None)
        if gone is None:
            print("ABSENT: ", lead[:40])
        else:
            gone._r.getparent().remove(gone._r)
            print("REMOVED:", lead[:40])

    doc.save(DOC)
    print("backup:", os.path.basename(BAK))


if __name__ == "__main__":
    main()
