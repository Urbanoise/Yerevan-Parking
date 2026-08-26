# -*- coding: utf-8 -*-
"""python-docx surgery helpers shared by the Output 8 / Output 10 revision scripts.

House convention, carried over from the June round (see port_edits_to_23.py): new
and changed text is marked RED so the reviewer can see at a glance what moved.
Deletions are simply removed — the reports are re-issued as a new dated file, and
the previous dated file remains the record of what the text used to say.
"""
import copy
import re

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

RED = RGBColor(0xC0, 0x00, 0x00)
GREY = RGBColor(0x55, 0x55, 0x55)


# ---------------------------------------------------------------------------
# finding things
# ---------------------------------------------------------------------------
def find(doc, needle, start=0):
    """First paragraph at or after `start` containing `needle`. Raises rather than
    returning None: a missed anchor means the document moved under the script and
    the edit must not be silently skipped."""
    for i, p in enumerate(doc.paragraphs):
        if i >= start and needle in p.text:
            return p
    raise LookupError(f"anchor not found: {needle!r}")


def find_styled(doc, needle, *styles):
    """First paragraph containing `needle` whose style is one of `styles`.

    Necessary because the Lists of Figures and Tables repeat every caption verbatim
    at the front of the document, so a plain text search for a caption or a heading
    finds the table-of-figures entry first. Anchoring on the style avoids editing —
    or worse, deleting from — the front matter.
    """
    for p in doc.paragraphs:
        if needle in p.text and p.style.name in styles:
            return p
    raise LookupError(f"anchor not found in styles {styles}: {needle!r}")


def find_all(doc, needle):
    return [p for p in doc.paragraphs if needle in p.text]


def maybe(doc, needle):
    for p in doc.paragraphs:
        if needle in p.text:
            return p
    return None


def find_table(doc, *cell_texts):
    """The table whose flattened cell text contains all of `cell_texts`."""
    for t in doc.tables:
        flat = " | ".join(c.text for row in t.rows for c in row.cells)
        if all(s in flat for s in cell_texts):
            return t
    raise LookupError(f"table not found: {cell_texts}")


# ---------------------------------------------------------------------------
# editing paragraph text
# ---------------------------------------------------------------------------
def _copy_font(src_run, dst_run):
    if src_run is None:
        return
    dst_run.font.name = src_run.font.name
    dst_run.font.size = src_run.font.size
    dst_run.bold = src_run.bold
    dst_run.italic = src_run.italic


def set_text(par, text, red=True, keep_lead_bold=False):
    """Replace a paragraph's whole text with one run, inheriting the paragraph's
    existing character formatting so the rewrite still looks like the report."""
    model = par.runs[0] if par.runs else None
    for r in list(par.runs):
        r._element.getparent().remove(r._element)
    if keep_lead_bold and ". " in text[:90]:
        head, tail = text.split(". ", 1)
        lead = par.add_run(head + ". ")
        _copy_font(model, lead)
        lead.bold = True
        if red:
            lead.font.color.rgb = RED
        run = par.add_run(tail)
    else:
        run = par.add_run(text)
    _copy_font(model, run)
    if red:
        run.font.color.rgb = RED
    return par


def sub(par, pattern, repl, red=True, count=0):
    """Regex-substitute inside a paragraph, marking only the touched runs red.

    Word splits a sentence across arbitrary runs, so a naive per-run replace misses
    any match that straddles a boundary. This flattens to text, substitutes, and
    rewrites the paragraph as a single run when a change actually happened.
    """
    old = par.text
    new = re.sub(pattern, repl, old, count=count)
    if new == old:
        return False
    set_text(par, new, red=red)
    return True


def sub_doc(doc, pattern, repl, red=True, limit=None):
    """Substitute across every paragraph and table cell. Returns the hit count."""
    n = 0
    for p in doc.paragraphs:
        if re.search(pattern, p.text) and sub(p, pattern, repl, red=red):
            n += 1
            if limit and n >= limit:
                return n
    for t in doc.tables:
        for row in t.rows:
            for c in row.cells:
                for p in c.paragraphs:
                    if re.search(pattern, p.text) and sub(p, pattern, repl, red=red):
                        n += 1
    return n


def copy_numbering(target, reference):
    """Give `target` the same list numbering as `reference`.

    Output 10's headings are numbered by an explicit `numPr` (numId 30), not by the
    style, so a heading created by changing a paragraph's style gets the right look
    and no number — it renders as "1.1" or as nothing at all. Two headings in the
    Conclusions chapter also carried numId 0 (numbering suppressed) because their
    numbers used to be typed into the text by hand.
    """
    ref_pr = reference._p.pPr
    if ref_pr is None or ref_pr.find(qn("w:numPr")) is None:
        return False
    tgt_pr = target._p.get_or_add_pPr()
    existing = tgt_pr.find(qn("w:numPr"))
    if existing is not None:
        tgt_pr.remove(existing)
    tgt_pr.append(copy.deepcopy(ref_pr.find(qn("w:numPr"))))
    return True


def set_caption(par, kind, title, red=True, number=1):
    """Rewrite a caption as "Figure <SEQ field> - title".

    Captions in these reports carry a `SEQ Figure \\* ARABIC` field, and the Lists of
    Figures and Tables are TOC fields with the `\\c "Figure"` switch, which collects
    ONLY paragraphs containing that field. Replacing a caption with plain text
    therefore empties the list — which is exactly what happened on the first pass. The
    field is rebuilt here, so Word both renumbers and re-lists the captions itself.
    """
    from docx.oxml import OxmlElement

    model = par.runs[0] if par.runs else None
    for r in list(par.runs):
        r._element.getparent().remove(r._element)

    def add(text=None, tag=None, attrs=None):
        run = OxmlElement("w:r")
        if red or model is not None:
            rpr = OxmlElement("w:rPr")
            if red:
                col = OxmlElement("w:color")
                col.set(qn("w:val"), "C00000")
                rpr.append(col)
            run.append(rpr)
        if tag:
            el = OxmlElement(tag)
            for k, v in (attrs or {}).items():
                el.set(qn(k), v)
            if text is not None:
                el.text = text
                el.set(qn("xml:space"), "preserve")
            run.append(el)
        par._p.append(run)
        return run

    add(f"{kind} ", "w:t")
    add(tag="w:fldChar", attrs={"w:fldCharType": "begin"})
    add(f" SEQ {kind} \\* ARABIC ", "w:instrText")
    add(tag="w:fldChar", attrs={"w:fldCharType": "separate"})
    add(str(number), "w:t")
    add(tag="w:fldChar", attrs={"w:fldCharType": "end"})
    add(f" - {title}", "w:t")
    return par


# ---------------------------------------------------------------------------
# inserting and removing blocks
# ---------------------------------------------------------------------------
def insert_after(par, text, style=None, red=True, bold_lead=False):
    """Add a new paragraph immediately after `par` and return it, so a caller can
    chain inserts down the document."""
    new_p = copy.deepcopy(par._p)
    for child in list(new_p):
        if child.tag in (qn("w:r"), qn("w:hyperlink"), qn("w:bookmarkStart"),
                         qn("w:bookmarkEnd")):
            new_p.remove(child)
    par._p.addnext(new_p)
    from docx.text.paragraph import Paragraph
    out = Paragraph(new_p, par._parent)
    if style:
        out.style = style
    if text:
        set_text(out, text, red=red, keep_lead_bold=bold_lead)
    return out


def insert_block(par, items, red=True):
    """Insert a list of (style, text) after `par`; returns the last paragraph.
    `style=None` keeps the anchor's style. Use bold_lead by prefixing text with
    "**" to mark a run-in heading sentence."""
    cur = par
    for style, text in items:
        bold_lead = text.startswith("**")
        cur = insert_after(cur, text.lstrip("*"), style=style, red=red,
                           bold_lead=bold_lead)
    return cur


def drop(par):
    par._p.getparent().remove(par._p)


def drop_range(first, last):
    """Remove every block element from `first` to `last` inclusive — used to delete
    a whole subsection (heading, paragraphs and any table between them)."""
    el, stop = first._p, last._p
    while el is not None:
        nxt = el.getnext()
        parent = el.getparent()
        parent.remove(el)
        if el is stop:
            return
        el = nxt
    raise LookupError("drop_range: end element never reached")


def move_after(par_or_el, anchor):
    """Move an existing block (e.g. a picture paragraph) to sit after `anchor`."""
    el = getattr(par_or_el, "_p", par_or_el)
    el.getparent().remove(el)
    anchor._p.addnext(el)


# ---------------------------------------------------------------------------
# tables
# ---------------------------------------------------------------------------
def set_cell(cell, text, red=True, bold=False):
    par = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        drop(extra)
    model = par.runs[0] if par.runs else None
    for r in list(par.runs):
        r._element.getparent().remove(r._element)
    run = par.add_run(text)
    _copy_font(model, run)
    run.bold = bold or (model.bold if model is not None else False)
    if red:
        run.font.color.rgb = RED
    return cell


def rewrite_table(table, rows, red=True, header=True):
    """Rewrite a table's contents in place, growing or shrinking the row count.

    In-place beats delete-and-rebuild because the table keeps its style, column
    widths and caption bookmarks — rebuilt tables come out looking foreign.
    """
    while len(table.rows) > len(rows):
        tr = table.rows[-1]._tr
        tr.getparent().remove(tr)
    while len(table.rows) < len(rows):
        table._tbl.append(copy.deepcopy(table.rows[-1]._tr))
    for r, values in enumerate(rows):
        cells = table.rows[r].cells
        for c, value in enumerate(values):
            if c < len(cells):
                set_cell(cells[c], str(value), red=red,
                         bold=(header and r == 0))
    return table


# ---------------------------------------------------------------------------
# pictures
# ---------------------------------------------------------------------------
def picture_paragraphs(doc):
    return [p for p in doc.paragraphs if "graphic" in p._p.xml]


def replace_image(doc, par, path):
    """Swap the image bytes behind the picture in `par`, keeping the original
    drawing (and therefore its size and anchoring) untouched."""
    rids = [e.get(qn("r:embed")) for e in par._p.iter() if e.get(qn("r:embed"))]
    if not rids:
        raise LookupError("no image in paragraph")
    part = doc.part.related_parts[rids[0]]
    with open(path, "rb") as fh:
        part._blob = fh.read()
    return rids[0]


def set_picture_width(par, inches):
    """Rescale the inline picture in `par` to `inches` wide, preserving its aspect
    ratio, so a swapped-in image of a different shape is not stretched."""
    from docx.shared import Inches, Emu
    for shape in par._p.iter(qn("wp:extent")):
        cx, cy = int(shape.get("cx")), int(shape.get("cy"))
        target = Emu(Inches(inches))
        shape.set("cx", str(int(target)))
        shape.set("cy", str(int(cy * (int(target) / cx))))
    for ext in par._p.iter(qn("a:ext")):
        if ext.get("cx") and ext.getparent().tag == qn("a:xfrm"):
            cx, cy = int(ext.get("cx")), int(ext.get("cy"))
            target = Emu(Inches(inches))
            ext.set("cx", str(int(target)))
            ext.set("cy", str(int(cy * (int(target) / cx))))


def add_picture_after(par, path, inches=6.1, caption=None, caption_style="Caption"):
    """Insert a new centred picture (and optional caption) after `par`."""
    holder = insert_after(par, "", style="Normal", red=False)
    holder.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = holder.add_run()
    from docx.shared import Inches
    run.add_picture(path, width=Inches(inches))
    out = holder
    if caption:
        out = insert_after(holder, caption, style=caption_style, red=True)
        out.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return out


def add_table_after(doc, par, rows, style="Table Grid", widths=None, red=True):
    """Build a new table after `par`. Returns the table."""
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    try:
        table.style = style
    except KeyError:
        pass
    for r, values in enumerate(rows):
        for c, value in enumerate(values):
            set_cell(table.rows[r].cells[c], str(value), red=red, bold=(r == 0))
    par._p.addnext(table._tbl)
    if widths:
        from docx.shared import Inches
        for row in table.rows:
            for c, w in enumerate(widths):
                if c < len(row.cells):
                    row.cells[c].width = Inches(w)
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(8.5)
    return table
