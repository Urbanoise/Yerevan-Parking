# -*- coding: utf-8 -*-
r"""Bring the Output 10 body text and its figure captions into line with the figures.

Two unrelated-looking fixes, one concern - the document disagreeing with its own
graphics:

1. The high-sensitivity zone paragraph lists the package for that band but omits
   organised free parking, which figure 6 shows in all three bands. Added.

2. The street photograph in chapter 2 has no caption. Figures 1, 3 and 7 look
   uncaptioned to python-docx but are not: their captions sit in text boxes anchored to
   the floating images, inside w:txbxContent, which doc.paragraphs does not walk. Only
   the photograph is genuinely missing one, and its slot is already there - an empty
   Caption paragraph holding TWO `SEQ Figure` fields, which would have numbered every
   later figure wrongly the moment anyone pressed F9.

The caption is built by cloning an existing caption paragraph, which carries the Caption
style and a single `SEQ Figure \* ARABIC` field; only the cached number and the trailing
text are changed, and the double-field paragraph it replaces takes the duplicate away
with it. Verify with Word field update: the sequence must read 1-7, counting the text-box
captions.

Edits the 13/08 revision in place (it carries hand edits made after the
reviewer-comment scripts ran, so it is not regenerated). Backup alongside.
"""
import copy
import os
import shutil

from docx import Document
from docx.oxml.ns import qn
from docx.shared import RGBColor
from docx.text.paragraph import Paragraph

import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 13082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-captions).docx")

RED = RGBColor(0xC0, 0x00, 0x00)

# image index (into the floating-image list), caption number, caption text
CAPTIONS = [
    (1, "2", " - Zone A paid-parking signage and roadside information board, "
             "central Yerevan"),
]


def image_paragraphs(doc):
    return [p for p in doc.paragraphs if p._p.findall(".//" + qn("a:blip"))]


def clone_caption(template, number, text):
    """Copy a working caption paragraph, keeping its SEQ field, and set the cached
    figure number and the descriptive text."""
    el = copy.deepcopy(template._p)
    par = Paragraph(el, template._parent)
    digits = [r for r in par.runs if r.text.strip().isdigit()]
    tails = [r for r in par.runs if r.text.startswith(" - ")]
    assert len(digits) == 1 and len(tails) == 1, "unexpected caption layout"
    digits[0].text = number
    tails[0].text = text
    for r in par.runs:
        r.font.color.rgb = RED
    return el


def split_run(par, run, head, insert, tail):
    """Rewrite `run` as head + insert + tail, with `insert` marked as an addition."""
    run.text = head
    made = []
    for txt in (insert, tail):
        new = copy.deepcopy(run._r)
        for t in new.findall(qn("w:t")):
            new.remove(t)
        el = new.makeelement(qn("w:t"), {})
        el.set(qn("xml:space"), "preserve")
        el.text = txt
        new.append(el)
        run._r.addnext(new) if not made else made[-1].addnext(new)
        made.append(new)
    next(r for r in par.runs if r._r is made[0]).font.color.rgb = RED


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)

    # ---- 1. organised free parking into the high-sensitivity package -------------
    par = next(p for p in doc.paragraphs
               if p.text.startswith("The high-sensitivity zone covers"))
    if "organising free parking" in par.text:
        print("free parking: already present")
    else:
        run = next(r for r in par.runs
                   if r.text.startswith("and charged one-per-household"))
        head = "charged one-per-household resident permits"
        tail = run.text[len("and " + head):]
        split_run(par, run, head, " and organising free parking", tail)
        print("free parking: ADDED")

    # ---- 2. captions for figures 1-3 --------------------------------------------
    template = next(p for p in doc.paragraphs
                    if p.style.name == "Caption" and p.text.startswith("Figure 4"))
    imgs = image_paragraphs(doc)
    for img_i, number, text in CAPTIONS:
        anchor = imgs[img_i]
        nxt = anchor._p.getnext()
        follow = Paragraph(nxt, anchor._parent) if nxt is not None else None
        if follow is not None and follow.style.name == "Caption" and follow.text.strip():
            print(f"figure {number}: caption already present")
            continue
        new = clone_caption(template, number, text)
        # the photograph's slot is an empty Caption paragraph carrying two SEQ fields;
        # replacing it removes the duplicate that would corrupt the numbering
        stale = [Paragraph(e, anchor._parent) for e in anchor._p.itersiblings()][:3]
        stale = next((p for p in stale
                      if p.style.name == "Caption" and not p.text.strip()), None)
        if stale is not None:
            stale._p.addprevious(new)
            stale._p.getparent().remove(stale._p)
            print(f"figure {number}: REPLACED empty caption")
        else:
            anchor._p.addnext(new)
            print(f"figure {number}: ADDED")

    doc.save(DOC)
    print("backup:", os.path.basename(BAK))


if __name__ == "__main__":
    main()
