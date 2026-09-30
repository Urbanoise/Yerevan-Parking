# -*- coding: utf-8 -*-
"""Output 10 - STS response copy: uniform caption separators (user, 30 Sep 2026).

Figures 1, 3 and 7 carry their captions inside floating text boxes and read
"Figure 1, ..." / "Figure 7. ..."; the other four read "Figure 2 - ...". The text
right after each SEQ field is changed to " - " (red), in both the DrawingML text box
and its VML fallback copy. The rest of each caption is untouched.

Run:  python fix_o10_caption_separators.py            (dry run)
      python fix_o10_caption_separators.py --apply
"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.text.run import Run

from docx_edit import RED

DOC = ("C:/Users/user/Yerevan-Parking/Final Presentation/SEP'26/"
       "Output 10_Parking Analysis Report_25082026_Logit comments - STS responses.docx")


def fix(q):
    """In caption paragraph q, rewrite the ", " / ". " after the SEQ field end."""
    runs = list(q.iter(qn("w:r")))
    ends = [i for i, r in enumerate(runs)
            if (fc := r.find(qn("w:fldChar"))) is not None and fc.get(qn("w:fldCharType")) == "end"]
    if not ends:
        return None
    nxt = runs[ends[0] + 1]
    t = nxt.find(qn("w:t"))
    m = re.match(r"\s*[,.]\s*", t.text or "")
    if not m:
        return None
    rest = t.text[m.end():]
    t.text = " - "
    t.set(qn("xml:space"), "preserve")
    Run(nxt, None).font.color.rgb = RED
    if rest:
        tail = copy.deepcopy(nxt)
        tail.find(qn("w:t")).text = rest
        rpr = tail.find(qn("w:rPr"))
        if rpr is not None and rpr.find(qn("w:color")) is not None:
            rpr.remove(rpr.find(qn("w:color")))
        nxt.addnext(tail)
    return "".join(x.text or "" for x in q.iter(qn("w:t")))


def main(apply):
    doc = Document(DOC)
    fixed = []
    for tb in doc.element.body.iter(qn("w:txbxContent")):
        for q in tb.iter(qn("w:p")):
            ps = q.find(qn("w:pPr"))
            sty = ps.find(qn("w:pStyle")) if ps is not None else None
            if sty is not None and sty.get(qn("w:val")) == "Caption":
                out = fix(q)
                if out:
                    fixed.append(out)
    for f in fixed:
        print(" ", f)
    if len(fixed) != 6:  # 3 captions x (text box + VML fallback)
        raise SystemExit(f"expected 6 caption copies, fixed {len(fixed)}")
    if apply:
        doc.save(DOC)
        print("saved", DOC)
    else:
        print("dry run OK - nothing saved")


if __name__ == "__main__":
    main("--apply" in sys.argv)
