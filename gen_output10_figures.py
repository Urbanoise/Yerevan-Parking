#!/usr/bin/env python
"""Regenerate Output 10 Figures 10 & 11 reflecting the field-survey recalibration,
then swap them into the redline working copy.

Figure 10 — "Mitigation measures grouped by sensitivity zones" (card graphic):
  Komitas moves Medium->High; Open Residential Yards elevated into the High package;
  Visitor caps marked targeted; a dedicated Gai Avenue (Mega Mall) panel notes
  that its kerb parking stays for now (revisit as the area changes).
Figure 11 — sensitivity map: the manually-refined "yerevan (2).png" placed in the
  report folder is swapped in (supersedes the matplotlib render).

Outputs PNG/JPEG beside the report and replaces word/media/image14.png (Fig 10) and
word/media/image15.jpeg (Fig 11) inside "...20260417 (rev).docx".
"""
import json
import math
import os
import shutil
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

ROOT = r"C:/Users/user/Yerevan-Parking"
RPT = os.path.join(ROOT, "Field Surveys/Field Surveys Report")
SZ = os.path.join(ROOT, "app/static/data/wgs84/sensitivity-zones.geojson")
REV = os.path.join(RPT, "Parking Analysis Report - 20260417 (rev).docx")
FIG10 = os.path.join(RPT, "Charts", "fig10_sensitivity_packages.png")
# Fig 11 swapped into the docx is the manually-refined map placed in the report
# folder. The matplotlib block below renders to FIG11_RENDER (its own, unused
# file) so it never overwrites the hand-made map that gets swapped in (FIG11).
FIG11_RENDER = os.path.join(RPT, "Charts", "fig11_sensitivity_map.jpg")
FIG11 = os.path.join(RPT, "Charts", "yerevan (2).png")

# ----------------------------------------------------------------------------
# FIGURE 10 — sensitivity-package cards
# ----------------------------------------------------------------------------
import textwrap

PANELS = [
    dict(title="High sensitivity", accent="#d32f2f", bg="#fdecea", ink="#b71c1c",
         streets="Kentron CBD: Nalbandyan, Amiryan, Tigran Mets  ·  Komitas",
         pills=["Extend paid zones", "Delivery spaces", "Visitor caps (targeted)",
                "Resident permits", "Open Residential Yards", "Park & Ride",
                "Organise free parking"]),
    dict(title="Medium sensitivity", accent="#f57c00", bg="#fff7e8", ink="#8a5300",
         streets="Arshakunyats, Kievyan",
         pills=["Extend paid zones", "Delivery spaces", "Park & Ride",
                "Organise free parking"]),
    dict(title="Lower sensitivity", accent="#2e7d32", bg="#e9f5ea", ink="#1b5e20",
         streets="Bagratunyats, Sebastia, Raffi, Nor Nork, Sasna Tsrer",
         pills=["Organise free parking", "Park & Ride"]),
    dict(title="Gai Avenue (Mega Mall)", accent="#607d8b",
         bg="#eef1f3", ink="#37474f", streets=None,
         notes=["Kerb parking stays for now; revisit as the area changes — "
                "mall parking or the planned BRT."]),
]

# layout constants (x range 0..100; y accumulates downward in 'units')
LEFT, RIGHT = 4.0, 96.0
TXT = LEFT + 2.0
CHARW = 0.78          # x-units per character at pill/note fontsize
PILL_H, PILL_GAP, ROW_GAP = 4.4, 1.4, 1.4
PADTOP, AFTER_TITLE, AFTER_STREETS, PADBOT, PANEL_GAP = 3.6, 5.0, 4.4, 3.0, 2.2
NOTE_LH = 3.4


def pill_width(text):
    return len(text) * CHARW + 3.2


def pill_rows(pills):
    rows, x = 1, TXT
    for t in pills:
        w = pill_width(t)
        if x + w > RIGHT and x > TXT:
            rows += 1; x = TXT
        x += w + PILL_GAP
    return rows


def panel_height(p):
    h = PADTOP + AFTER_TITLE
    if p.get("streets"):
        h += AFTER_STREETS
    if "pills" in p:
        h += pill_rows(p["pills"]) * (PILL_H + PILL_GAP)
    else:
        lines = sum(len(textwrap.wrap(n, width=int((RIGHT - TXT) / CHARW)))
                    for n in p["notes"])
        h += lines * NOTE_LH + (len(p["notes"]) - 1) * 1.2 + 2.0
    return h + PADBOT


heights = [panel_height(p) for p in PANELS]
total = sum(heights) + PANEL_GAP * (len(PANELS) - 1) + 2.0

fig = plt.figure(figsize=(9.2, total * 0.082), dpi=120)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(total, 0)
ax.axis("off")

y = 1.0
for p, h in zip(PANELS, heights):
    top, bottom = y, y + h
    ax.add_patch(FancyBboxPatch((LEFT - 1.2, top + 0.4), RIGHT - LEFT + 2.4, h - 0.8,
                 boxstyle="round,pad=0,rounding_size=1.2", linewidth=0,
                 facecolor=p["bg"], zorder=1, mutation_aspect=0.35))
    ax.add_patch(plt.Rectangle((LEFT - 1.2, top + 0.4), 1.0, h - 0.8,
                 color=p["accent"], zorder=2))
    cur = top + PADTOP
    ax.text(TXT, cur, p["title"], fontsize=16, fontweight="bold",
            color=p["accent"], va="center", zorder=4)
    cur += AFTER_TITLE
    if p.get("streets"):
        ax.text(TXT, cur, p["streets"], fontsize=10.5, color=p["ink"],
                va="center", zorder=4, style="italic")
        cur += AFTER_STREETS
    if "pills" in p:
        x = TXT
        for t in p["pills"]:
            w = pill_width(t)
            if x + w > RIGHT and x > TXT:
                x = TXT; cur += PILL_H + PILL_GAP
            ax.add_patch(FancyBboxPatch((x, cur - PILL_H / 2), w, PILL_H,
                         boxstyle="round,pad=0,rounding_size=1.5", linewidth=0,
                         facecolor=p["accent"], alpha=0.18, zorder=3,
                         mutation_aspect=0.4))
            ax.text(x + w / 2, cur, t, ha="center", va="center", fontsize=10.5,
                    color=p["ink"], zorder=4)
            x += w + PILL_GAP
    else:
        for n in p["notes"]:
            for ln in textwrap.wrap(n, width=int((RIGHT - TXT) / CHARW)):
                ax.text(TXT, cur, ln, fontsize=10.5, color=p["ink"], va="center",
                        zorder=4)
                cur += NOTE_LH
            cur += 1.2
    y = bottom + PANEL_GAP

fig.savefig(FIG10, dpi=120, facecolor="white", bbox_inches="tight", pad_inches=0.12)
plt.close(fig)
print("WROTE", FIG10)

# ----------------------------------------------------------------------------
# FIGURE 11 — sensitivity map (Komitas Medium -> High)
# ----------------------------------------------------------------------------
COLORS = {"No Parking": "#9e9e9e", "Low": "#66bb6a", "Moderate": "#ffee58",
          "Medium": "#f57c00", "High": "#d32f2f"}
sz = json.load(open(SZ, encoding="utf-8"))
KOMITAS_FEAT = 17                     # identified by exact overlap with the komitas survey cloud
sz["features"][KOMITAS_FEAT]["properties"]["sensitivity"] = "High"


def line_coords(f):
    out = []
    def walk(c):
        if isinstance(c[0], (int, float)):
            out.append(c)
        else:
            for x in c:
                walk(x)
    walk(f["geometry"]["coordinates"])
    return out


allpts = [pt for f in sz["features"] for pt in line_coords(f)]
lat0 = sum(p[1] for p in allpts) / len(allpts)

mfig, max_ = plt.subplots(figsize=(11.8, 8.6), dpi=120)
mfig.patch.set_facecolor("#141414")
max_.set_facecolor("#141414")
# draw lower-priority colours first so High/Medium sit on top
order = ["No Parking", "Low", "Moderate", "Medium", "High"]
for sev in order:
    for f in sz["features"]:
        if f["properties"]["sensitivity"] != sev:
            continue
        pts = line_coords(f)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        lw = 6.0 if sev in ("High", "Medium") else 4.5
        max_.plot(xs, ys, color=COLORS[sev], linewidth=lw, solid_capstyle="round",
                  solid_joinstyle="round", zorder={"No Parking": 1, "Low": 2,
                  "Moderate": 3, "Medium": 4, "High": 5}[sev])
max_.set_aspect(1.0 / math.cos(math.radians(lat0)))
max_.axis("off")
legend = [Line2D([0], [0], color=COLORS[s], lw=6, label=l) for s, l in
          [("High", "High sensitivity"), ("Medium", "Medium sensitivity"),
           ("Moderate", "Moderate"), ("Low", "Lower sensitivity"),
           ("No Parking", "No parking")]]
leg = max_.legend(handles=legend, loc="upper left", frameon=True, fontsize=11,
                  labelcolor="white")
leg.get_frame().set_facecolor("#222222"); leg.get_frame().set_edgecolor("#444444")
mfig.savefig(FIG11_RENDER, dpi=120, facecolor="#141414", bbox_inches="tight", pad_inches=0.15,
             pil_kwargs={"quality": 90})
plt.close(mfig)
print("WROTE", FIG11_RENDER)

# ----------------------------------------------------------------------------
# Swap both images into the rev docx via python-docx parts (robust to media
# renumbering), keeping each picture's display WIDTH and resetting HEIGHT to the
# new image's aspect ratio so nothing is stretched.
# ----------------------------------------------------------------------------
from docx import Document as _Doc
from docx.oxml.ns import qn as _qn
from PIL import Image as _Img

doc = _Doc(REV)
caps = doc.paragraphs


def _rid_of(par):
    bl = par._p.findall(".//" + _qn("a:blip"))
    return bl[0].get(_qn("r:embed")) if bl else None


# locate the "Figure 10" caption, then the picture before it (Fig 10) and the
# next picture after it (Fig 11, the sensitivity map).
# the real caption contains "grouped" — distinct from the inserted red note that
# also mentions "Figure 10".
cap_i = next(i for i, p in enumerate(caps)
             if "Figure 10" in p.text and "grouped" in p.text.lower())
fig10_rid = next(_rid_of(caps[j]) for j in range(cap_i, cap_i - 6, -1) if _rid_of(caps[j]))
fig11_rid = next(_rid_of(caps[j]) for j in range(cap_i + 1, cap_i + 25) if _rid_of(caps[j]))

def _blip_for(rid):
    for b in doc.element.body.iter(_qn("a:blip")):
        if b.get(_qn("r:embed")) == rid:
            return b
    return None


for rid, path in [(fig10_rid, FIG10), (fig11_rid, FIG11)]:
    doc.part.related_parts[rid]._blob = open(path, "rb").read()   # replace bytes
    nw, nh = _Img.open(path).size
    blip = _blip_for(rid)
    # walk up to the drawing wrapper, keep cx, reset cy to the new aspect
    node = blip
    while node is not None and node.tag not in (_qn("wp:inline"), _qn("wp:anchor")):
        node = node.getparent()
    if node is not None:
        ext = node.find(_qn("wp:extent"))
        cx = int(ext.get("cx"))
        ext.set("cy", str(int(cx * nh / nw)))
        for aext in node.iter(_qn("a:ext")):        # pic spPr xfrm ext
            aext.set("cx", str(cx)); aext.set("cy", str(int(cx * nh / nw)))

doc.save(REV)
print("SWAPPED Fig10 (rid %s) / Fig11 (rid %s) into %s" % (fig10_rid, fig11_rid, REV))
