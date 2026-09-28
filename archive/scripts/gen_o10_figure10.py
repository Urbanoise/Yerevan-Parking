# -*- coding: utf-8 -*-
"""Re-render Output 10's Figure 10 (mitigation measures by sensitivity zone) and swap
it into the 30072026 revision.

Two changes the reviewer asked for:
  * Park & Ride is removed from every package — the conceptual design does not include
    it and it is not recommended.
  * Komitas sits in the High package (123% peak, no on-street absorption), which is
    where the body text now lists it too.
And three measures added in this revision appear in the packages that carry them:
occupancy-based pricing, withdrawal of the flat annual permit, and derelict-vehicle
removal.

This is a standalone renderer rather than an edit to gen_output10_figures.py: that
script targets the April file, renders Figure 11 as well, and does its work at import
time, so it cannot be reused against a different document without running all of it.
The panel layout here reproduces its visual language.
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import report_figures as rf

RPT = os.path.join(rf.ROOT, "Field Surveys/Field Surveys Report")
OUT = os.path.join(RPT, "Charts", "fig10_sensitivity_packages_30072026.png")
DOCS = [
    os.path.join(rf.ROOT, "Final Presentation",
                 "Output 10 - Parking Analysis Report - 30072026 (rev).docx"),
    os.path.join(RPT, "Output 10 - Parking Analysis Report - 30072026 (rev).docx"),
]

F = rf.survey()

PANELS = [
    dict(title="High sensitivity", accent="#d32f2f", bg="#fdecea", ink="#b71c1c",
         streets="Kentron CBD: Nalbandyan, Amiryan, Tigran Mets  ·  Komitas Avenue",
         pills=["Extend paid zones", "Occupancy-based pricing",
                "Open residential yards (prerequisite)", "Delivery spaces",
                "Resident permits (charged, 1 per household)",
                "Withdraw flat annual permit", "Visitor caps (targeted)",
                "Organise free parking"]),
    dict(title="Medium sensitivity", accent="#f57c00", bg="#fff7e8", ink="#8a5300",
         streets="Arshakunyats, Kievyan, Garegin Nzhdeh",
         pills=["Extend paid zones", "Occupancy-based pricing", "Delivery spaces",
                "Withdraw flat annual permit", "Organise free parking"]),
    dict(title="Lower sensitivity", accent="#2e7d32", bg="#e9f5ea", ink="#1b5e20",
         streets="Bagratunyats, Sebastia, Raffi, Rubinyan, Nor Nork",
         pills=["Organise free parking", "Open residential yards (where feasible)",
                "Delivery spaces (freight pockets)"]),
    dict(title="Exception — Gai Avenue (Mega Mall)", accent="#607d8b",
         bg="#eef1f3", ink="#37474f", streets=None,
         notes=["Kerb parking stays for now; revisit as the area changes — "
                "mall parking or the planned BRT."]),
]

# layout constants (x range 0..100; y accumulates downward in 'units')
LEFT, RIGHT = 4.0, 96.0
TXT = LEFT + 2.0
CHARW = 0.78
PILL_H, PILL_GAP, ROW_GAP = 4.4, 1.4, 1.4
PADTOP, AFTER_TITLE, AFTER_STREETS, PADBOT, PANEL_GAP = 3.6, 5.0, 4.4, 3.0, 2.2
NOTE_LH = 3.4

plt.rcParams.update({"font.family": "Calibri", "figure.facecolor": "white",
                     "savefig.facecolor": "white"})


def pill_width(text):
    return len(text) * CHARW + 3.2


def wrap_pills(pills):
    """Greedy row packing, so the panel height can be computed before drawing."""
    rows, cur, x = [], [], TXT
    for t in pills:
        w = pill_width(t)
        if x + w > RIGHT and cur:
            rows.append(cur)
            cur, x = [], TXT
        cur.append(t)
        x += w + PILL_GAP
    if cur:
        rows.append(cur)
    return rows


def panel_height(p):
    h = PADTOP + AFTER_TITLE
    if p.get("streets"):
        h += AFTER_STREETS
    if p.get("pills"):
        rows = wrap_pills(p["pills"])
        h += len(rows) * PILL_H + (len(rows) - 1) * ROW_GAP
    for note in p.get("notes", []):
        h += NOTE_LH * len(textwrap.wrap(note, 96))
    return h + PADBOT


total = sum(panel_height(p) for p in PANELS) + PANEL_GAP * (len(PANELS) - 1)
fig_h = total * 0.075
fig, ax = plt.subplots(figsize=(7.4, fig_h))
ax.set_xlim(0, 100)
ax.set_ylim(total, 0)
ax.axis("off")

y = 0.0
for p in PANELS:
    h = panel_height(p)
    ax.add_patch(FancyBboxPatch((LEFT, y + 0.5), RIGHT - LEFT, h - 1.0,
                                boxstyle="round,pad=0,rounding_size=1.6",
                                linewidth=1.1, edgecolor=p["accent"],
                                facecolor=p["bg"], zorder=1))
    ax.add_patch(plt.Rectangle((LEFT, y + 0.5), 0.9, h - 1.0, color=p["accent"],
                               zorder=2))
    cy = y + PADTOP
    ax.text(TXT, cy, p["title"], fontsize=11, fontweight="bold", color=p["ink"],
            va="center", zorder=3)
    cy += AFTER_TITLE
    if p.get("streets"):
        ax.text(TXT, cy, p["streets"], fontsize=8.2, color="#4a4a4a", va="center",
                zorder=3)
        cy += AFTER_STREETS
    for row in wrap_pills(p.get("pills", [])):
        x = TXT
        for t in row:
            w = pill_width(t)
            ax.add_patch(FancyBboxPatch((x, cy - PILL_H / 2), w, PILL_H,
                                        boxstyle="round,pad=0,rounding_size=1.4",
                                        linewidth=0.9, edgecolor=p["accent"],
                                        facecolor="white", zorder=3))
            ax.text(x + w / 2, cy, t, fontsize=8.4, color=p["ink"], ha="center",
                    va="center", zorder=4)
            x += w + PILL_GAP
        cy += PILL_H + ROW_GAP
    for note in p.get("notes", []):
        for line in textwrap.wrap(note, 96):
            ax.text(TXT, cy, line, fontsize=8.6, color=p["ink"], va="center", zorder=3)
            cy += NOTE_LH
    y += h + PANEL_GAP

fig.tight_layout(pad=0.2)
fig.savefig(OUT, dpi=200)
plt.close(fig)
print("WROTE", OUT)


# ----------------------------------------------------------------------------
# swap into both copies of the 30072026 revision
# ----------------------------------------------------------------------------
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

for path in DOCS:
    if not os.path.exists(path):
        print("SKIP (not found):", path)
        continue
    doc = Document(path)
    paras = doc.paragraphs

    def rid_of(par):
        bl = par._p.findall(".//" + qn("a:blip"))
        return bl[0].get(qn("r:embed")) if bl else None

    cap_i = next(i for i, p in enumerate(paras)
                 if "grouped by sensitivity zones" in p.text.lower())
    rid = next(rid_of(paras[j]) for j in range(cap_i, max(cap_i - 8, -1), -1)
               if rid_of(paras[j]))

    doc.part.related_parts[rid]._blob = open(OUT, "rb").read()
    nw, nh = Image.open(OUT).size
    for blip in doc.element.body.iter(qn("a:blip")):
        if blip.get(qn("r:embed")) != rid:
            continue
        node = blip
        while node is not None and node.tag != qn("w:drawing"):
            node = node.getparent()
        if node is None:
            continue
        for ext in list(node.iter(qn("wp:extent"))) + list(node.iter(qn("a:ext"))):
            cx = ext.get("cx")
            if cx:
                ext.set("cy", str(int(int(cx) * nh / nw)))
    doc.save(path)
    print("SWAPPED Figure 10 into:", os.path.basename(path))
