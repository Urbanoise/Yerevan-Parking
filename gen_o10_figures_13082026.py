# -*- coding: utf-8 -*-
"""Re-render the two mitigation figures of Output 10 for the 13/08 revision and swap
them into the document.

Figure 5 (summary of the measures) had no generator: it was a hand-made graphic
carried over from an early draft, still showing Park & ride and Delivery spaces and
still missing the three measures added in the July revision. It is rebuilt here as a
generated figure, so it can be regenerated in future.

The card set is the five measures the client asked the summary graphic to carry: the
occupancy-based charge, the withdrawal of the flat annual permit and derelict-vehicle
removal are held back from this figure. Chapter 5 still sets all three out in the text.

Figure 6 (measures by sensitivity zone) is the fig10 renderer with the delivery pills
removed, the yard-opening pill no longer labelled a prerequisite and that pill gone
altogether from the lower band, where the kerb is under too little pressure to
generate paying demand for brokered courtyard access. Like figure 5 it
carries only the geographically varying measures: the pricing, permit and derelict
measures apply across the programme rather than by zone, so they are set out in the
text instead of being pinned to a sensitivity band.

Supersedes gen_o10_figure10.py, which targets the 30/07 revision.
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
from docx import Document
from docx.oxml.ns import qn

import report_figures as rf

RPT = os.path.join(rf.ROOT, "Field Surveys/Field Surveys Report")
CHARTS = os.path.join(RPT, "Charts")
OUT5 = os.path.join(CHARTS, "fig5_measure_summary_13082026.png")
OUT6 = os.path.join(CHARTS, "fig10_sensitivity_packages_13082026.png")
DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 13082026 (rev).docx")

plt.rcParams.update({"font.family": "Calibri", "figure.facecolor": "white",
                     "savefig.facecolor": "white"})

# ---------------------------------------------------------------------------
# Figure 5 - the measure cards, one per measure in chapter 5
# ---------------------------------------------------------------------------
CARDS = [
    ("#1565c0", "Extend paid zones",
     "Roll out the red/blue-line system — markings, hourly pricing, ANPR — "
     "onto side streets within 100 m of the corridor."),
    ("#c62828", "Resident permits",
     "One per household, charged at a modest annual fee, issued against a verified "
     "address and vehicle ownership."),
    ("#ef6c00", "Visitor caps",
     "Maximum stay durations for non-resident vehicles, targeted at genuinely "
     "low-turnover spots rather than applied everywhere."),
    ("#2e7d32", "Organise free parking",
     "Delineate and sign currently informal parking — paint bays, add signage. "
     "No pricing yet; just structure."),
    ("#283593", "Open residential yards",
     "Gated courtyards sit empty while residents commute; controlled daytime access "
     "creates supply where the corridor removes it."),
]

COLS = 3
ROWS = -(-len(CARDS) // COLS)
CARD_W, GAP = 24.0, 1.6
UNIT = 0.0932  # inches per layout unit — keeps a card the same size on any grid
TITLE_WRAP, BODY_WRAP = 22, 34
TITLE_LH, BODY_LH, TITLE_TOP, TITLE_GAP, CARD_BOT = 3.0, 2.5, 4.2, 1.2, 3.4


def card_height(title, body):
    return (TITLE_TOP + TITLE_LH * len(textwrap.wrap(title, TITLE_WRAP)) + TITLE_GAP
            + BODY_LH * (len(textwrap.wrap(body, BODY_WRAP)) - 1) + CARD_BOT)


# every card is as tall as the wordiest one, so the grid stays even
CARD_H = max(card_height(t, b) for _, t, b in CARDS)


def draw_cards():
    total_w = COLS * CARD_W + (COLS - 1) * GAP
    total_h = ROWS * CARD_H + (ROWS - 1) * GAP
    fig, ax = plt.subplots(figsize=(total_w * UNIT, total_h * UNIT))
    ax.set_xlim(0, total_w)
    ax.set_ylim(total_h, 0)
    ax.axis("off")

    for n, (accent, title, body) in enumerate(CARDS):
        cx = (n % COLS) * (CARD_W + GAP)
        cy = (n // COLS) * (CARD_H + GAP)
        ax.add_patch(FancyBboxPatch((cx, cy), CARD_W, CARD_H,
                                    boxstyle="round,pad=0,rounding_size=0.9",
                                    linewidth=0.9, edgecolor="#dcdcdc",
                                    facecolor="#fbfbfb", zorder=1))
        ax.add_patch(plt.Rectangle((cx, cy), CARD_W, 1.1, color=accent, zorder=2))

        y = cy + TITLE_TOP
        for line in textwrap.wrap(title, TITLE_WRAP):
            ax.text(cx + 1.8, y, line, fontsize=11.5, fontweight="bold",
                    color="#1a1a1a", va="center", zorder=3)
            y += TITLE_LH
        y += TITLE_GAP
        for line in textwrap.wrap(body, BODY_WRAP):
            ax.text(cx + 1.8, y, line, fontsize=8.6, color="#4a4a4a", va="center",
                    zorder=3)
            y += BODY_LH

    fig.tight_layout(pad=0.2)
    fig.savefig(OUT5, dpi=200)
    plt.close(fig)
    print("WROTE", OUT5)


# ---------------------------------------------------------------------------
# Figure 6 - packages by sensitivity zone
# ---------------------------------------------------------------------------
PANELS = [
    dict(title="High sensitivity", accent="#d32f2f", bg="#fdecea", ink="#b71c1c",
         streets="Kentron CBD: Nalbandyan, Amiryan, Tigran Mets  ·  Komitas Avenue",
         pills=["Extend paid zones", "Open residential yards (where feasible)",
                "Visitor caps", "Organise free parking"]),
    dict(title="Medium sensitivity", accent="#f57c00", bg="#fff7e8", ink="#8a5300",
         streets="Arshakunyats, Kievyan, Garegin Nzhdeh",
         pills=["Extend paid zones", "Organise free parking"]),
    dict(title="Lower sensitivity", accent="#2e7d32", bg="#e9f5ea", ink="#1b5e20",
         streets="Bagratunyats, Sebastia, Raffi, Rubinyan, Nor Nork",
         pills=["Organise free parking"]),
    dict(title="Exception — Gai Avenue (Mega Mall)", accent="#607d8b",
         bg="#eef1f3", ink="#37474f", streets=None,
         notes=["Kerb parking stays for now; revisit as the area changes — "
                "mall parking or the planned BRT."]),
]

LEFT, RIGHT = 4.0, 96.0
TXT = LEFT + 2.0
CHARW = 0.78
PILL_H, PILL_GAP, ROW_GAP = 4.4, 1.4, 1.4
PADTOP, AFTER_TITLE, AFTER_STREETS, PADBOT, PANEL_GAP = 3.6, 5.0, 4.4, 3.0, 2.2
NOTE_LH = 3.4


def pill_width(text):
    return len(text) * CHARW + 3.2


def wrap_pills(pills):
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


def draw_panels():
    total = sum(panel_height(p) for p in PANELS) + PANEL_GAP * (len(PANELS) - 1)
    fig, ax = plt.subplots(figsize=(7.4, total * 0.075))
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
                ax.text(TXT, cy, line, fontsize=8.6, color=p["ink"], va="center",
                        zorder=3)
                cy += NOTE_LH
        y += h + PANEL_GAP

    fig.tight_layout(pad=0.2)
    fig.savefig(OUT6, dpi=200)
    plt.close(fig)
    print("WROTE", OUT6)


# ---------------------------------------------------------------------------
def swap(doc, caption_needle, png):
    """Replace the image sitting above `caption_needle`, keeping its width and
    correcting its height for the new aspect ratio."""
    paras = doc.paragraphs

    def rid_of(par):
        bl = par._p.findall(".//" + qn("a:blip"))
        return bl[0].get(qn("r:embed")) if bl else None

    cap_i = next(i for i, p in enumerate(paras) if caption_needle in p.text.lower())
    rid = next(rid_of(paras[j]) for j in range(cap_i, max(cap_i - 8, -1), -1)
               if rid_of(paras[j]))

    doc.part.related_parts[rid]._blob = open(png, "rb").read()
    nw, nh = Image.open(png).size
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
    print("SWAPPED:", caption_needle)


def main():
    os.makedirs(CHARTS, exist_ok=True)
    draw_cards()
    draw_panels()
    doc = Document(DOC)
    swap(doc, "summary of the mitigation measures", OUT5)
    swap(doc, "grouped by sensitivity zones", OUT6)
    doc.save(DOC)
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
