# -*- coding: utf-8 -*-
"""Re-scope the red in the Output 10 revision so it marks only what actually changed.

The revision scripts mark a whole paragraph red whenever they touch it, because
docx_edit.sub() flattens the paragraph to a single run in order to substitute across
run boundaries. That is fine for generating the file but useless for reviewing it: a
two-word number refresh looks identical to a page of new prose.

This pass compares each red paragraph against its counterpart in the June file and
re-marks it:

  TIER 1  >= 95% carried over  -> all black (accept-on-sight; the figure is the change)
  TIER 2  60-95% carried over  -> red on the changed words only, black on the rest
  TIER 3  < 60% carried over   -> left fully red (genuinely new or rewritten)

Text is never altered — only run boundaries and colour. Paragraphs carrying a field
(captions hold a SEQ field), a hyperlink, or whose runs do not reconcile with the
paragraph text are recoloured wholesale rather than rebuilt, because splitting them
would destroy the field or the link.
"""
import copy
import difflib
import re
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import RGBColor

FP = "Final Presentation/"
JUNE = FP + "Output 10 - Parking Analysis Report - 23062026 (rev).docx"
TARGET = FP + "Output 10 - Parking Analysis Report - 13082026 (rev).docx"

RED = RGBColor(0xC0, 0x00, 0x00)
REDS = ("FF0000", "C00000")


def is_red(run):
    c = run.font.color
    return c is not None and c.rgb is not None and str(c.rgb).upper() in REDS


def strip_colour(run):
    """Remove w:color so the run inherits the style's colour (black body text)."""
    rpr = run._r.find(qn("w:rPr"))
    if rpr is None:
        return
    for el in rpr.findall(qn("w:color")):
        rpr.remove(el)


def has_field_or_link(par):
    p = par._p
    return (p.find(qn("w:hyperlink")) is not None
            or len(list(p.iter(qn("w:fldChar")))) > 0
            or len(list(p.iter(qn("w:instrText")))) > 0)


def _norm(tok):
    """Token key for comparison: dashes and quotes unified, edge punctuation dropped.

    Without this a comma lost from the end of a word marks the whole word as
    changed, which fills the review queue with false positives.
    """
    tok = (tok.replace("–", "-").replace("—", "-").replace("−", "-")
              .replace("’", "'").replace("‘", "'")
              .replace("“", '"').replace("”", '"'))
    return tok.strip(".,;:()[]'\"-…").lower()


def changed_spans(old_text, new_text):
    """Character spans of new_text that have no counterpart in old_text.

    Matching is done on normalised tokens so that punctuation, dash style and
    capitalisation changes do not register as content changes; the spans returned
    still index the raw text.
    """
    otok = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", old_text)]
    ntok = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", new_text)]
    sm = difflib.SequenceMatcher(None, [_norm(t[0]) for t in otok],
                                 [_norm(t[0]) for t in ntok])
    spans = []
    for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert") and j2 > j1:
            # a run of tokens that normalise to nothing (stray punctuation) is not a change
            if all(_norm(ntok[j][0]) == "" for j in range(j1, j2)):
                continue
            spans.append((ntok[j1][1], ntok[j2 - 1][2]))
    merged = []
    for s, e in spans:
        if merged and new_text[merged[-1][1]:s].strip() == "":
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged


def rebuild(par, spans):
    """Rewrite the paragraph's runs so only `spans` are red. Text is preserved
    exactly; per-character bold/italic/font is carried over from the run that
    currently covers each offset."""
    runs = par.runs
    text = "".join(r.text for r in runs)
    if text != par.text:
        return False  # something other than plain runs in here; caller falls back

    # offset -> source run, so a bold lead-in ("Field-survey verdict.") stays bold
    owners, pos = [], 0
    for r in runs:
        owners.append((pos, pos + len(r.text), r))
        pos += len(r.text)

    def owner_at(i):
        for s, e, r in owners:
            if s <= i < e:
                return r
        return runs[-1] if runs else None

    # cut points: span boundaries plus every source-run boundary
    cuts = {0, len(text)}
    for s, e in spans:
        cuts.update((s, e))
    for s, e, _r in owners:
        cuts.update((s, e))
    cuts = sorted(c for c in cuts if 0 <= c <= len(text))

    segments = []
    for a, b in zip(cuts, cuts[1:]):
        if b <= a:
            continue
        red = any(s <= a and b <= e for s, e in spans)
        segments.append((text[a:b], red, owner_at(a)))

    p = par._p
    for r in list(runs):
        p.remove(r._r)
    for seg_text, red, src in segments:
        r = OxmlElement("w:r")
        if src is not None:
            src_rpr = src._r.find(qn("w:rPr"))
            if src_rpr is not None:
                r.append(copy.deepcopy(src_rpr))
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = seg_text
        r.append(t)
        p.append(r)
        # colour after the rPr is in place
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr")
            r.insert(0, rpr)
        for el in rpr.findall(qn("w:color")):
            rpr.remove(el)
        if red:
            col = OxmlElement("w:color")
            col.set(qn("w:val"), "C00000")
            rpr.append(col)
    return True


def main():
    june = [p.text.strip() for p in Document(JUNE).paragraphs if p.text.strip()]
    doc = Document(TARGET)

    t1 = t2_rebuilt = t2_flat = t3 = 0
    report = []
    head = ""
    for par in doc.paragraphs:
        if par.style.name.startswith("Heading"):
            head = par.text.strip()[:40]
        if not any(is_red(r) for r in par.runs):
            continue
        text = par.text.strip()
        if not text:
            continue
        m = difflib.get_close_matches(text, june, n=1, cutoff=0.55)
        sim = difflib.SequenceMatcher(None, m[0], text).ratio() * 100 if m else 0.0

        if sim >= 95:
            for r in par.runs:
                strip_colour(r)
            t1 += 1
            report.append(("T1-black", sim, head, text[:70]))
        elif sim >= 60:
            spans = changed_spans(m[0], text)
            protected = has_field_or_link(par) or par.style.name in ("Caption",)
            if not protected and spans and rebuild(par, spans):
                t2_rebuilt += 1
                marked = sum(e - s for s, e in spans)
                report.append(("T2-diff", sim, head,
                               "%s  [%d red chars of %d]" % (text[:50], marked, len(text))))
            else:
                for r in par.runs:
                    strip_colour(r)
                t2_flat += 1
                why = "field/link" if protected else "runs unreconcilable"
                report.append(("T2-black(%s)" % why, sim, head, text[:60]))
        else:
            t3 += 1

    doc.save(TARGET)
    for kind, sim, h, t in report:
        print(("%-22s %3.0f%%  [%s] %s" % (kind, sim, h, t)).encode("ascii", "replace").decode())
    print()
    print("TIER 1 -> black                 : %d" % t1)
    print("TIER 2 -> word-level red        : %d" % t2_rebuilt)
    print("TIER 2 -> black (field/link)    : %d" % t2_flat)
    print("TIER 3 -> left fully red        : %d" % t3)
    print("saved:", TARGET)


if __name__ == "__main__":
    main()
