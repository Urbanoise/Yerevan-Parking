# -*- coding: utf-8 -*-
"""Output 8 - Sep 2026 response copy: make the List of Figures a live field again.

The List of Figures in the reviewers' file (and the 25 Aug issue) is static text: the
entries keep their PAGEREF fields but the enclosing `TOC \\c "Figure"` field is gone,
so Word cannot regenerate it. It was already out of order (Figures 7-8 before 9) and
could not pick up the nine new maps. This wraps the existing entries in a TOC field
built like the List of Tables; update fields in Word (COM) afterwards to rebuild it.

Run:  python fix_o8_figure_list_field.py            (dry run)
      python fix_o8_figure_list_field.py --apply
"""
import copy
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from apply_o8_sep_comments import DST


def main(apply):
    doc = Document(DST)
    paras = doc.paragraphs
    head = next(i for i, p in enumerate(paras) if p.text.strip() == "List of Figures")
    entries = []
    for p in paras[head + 1:]:
        if p.style.name != "table of figures":
            break
        entries.append(p)
    if not entries or not entries[0].text.startswith("Figure 1"):
        raise SystemExit("List of Figures entries not found")
    if any("TOC" in (t.text or "") for p in entries for t in p._p.iter(qn("w:instrText"))):
        raise SystemExit("List of Figures already has a TOC field")

    # the List of Tables opens with begin / instr / separate runs: reuse them
    tables = next(p for p in paras if any('TOC \\h \\z \\c "Table"' in (t.text or "")
                                          for t in p._p.iter(qn("w:instrText"))))
    runs = tables._p.findall(qn("w:r"))
    opening = []
    for r in runs:
        opening.append(copy.deepcopy(r))
        if r.find(qn("w:fldChar")) is not None and \
                r.find(qn("w:fldChar")).get(qn("w:fldCharType")) == "separate":
            break
    for r in opening:
        for t in r.iter(qn("w:instrText")):
            t.text = t.text.replace('"Table"', '"Figure"')
    first = entries[0]._p
    anchor = first.find(qn("w:pPr"))
    for r in reversed(opening):
        anchor.addnext(r)

    end = OxmlElement("w:r")
    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), "end")
    end.append(fc)
    entries[-1]._p.append(end)

    if apply:
        doc.save(DST)
        print("saved", DST)
    else:
        print(f"dry run OK - would wrap {len(entries)} entries")


if __name__ == "__main__":
    main("--apply" in sys.argv)
