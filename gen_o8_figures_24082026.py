# -*- coding: utf-8 -*-
"""Re-render the peak-occupancy figure of Output 8 on the area-wide peak-hour basis
and swap it into the 24/08 revision.

gen_o8_report_figures.fig10_peak_occupancy now draws the new basis; this renders that
one figure and replaces the image sitting above its caption, leaving every other
figure in the document untouched.
"""
import os

from PIL import Image
from docx import Document
from docx.oxml.ns import qn

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import docx_edit as dx
import gen_o8_report_figures as g
import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")
PNG = os.path.join(g.OUT, "fig10_peak_occupancy_by_area.png")


def swap(doc, caption_needle, png):
    """Replace the image above `caption_needle`, keeping its width and correcting the
    height for the new aspect ratio."""
    paras = doc.paragraphs

    def rid_of(par):
        bl = par._p.findall(".//" + qn("a:blip"))
        return bl[0].get(qn("r:embed")) if bl else None

    # Anchor on the Caption style: the List of Figures repeats every caption verbatim
    # at the front of the document, and those entries have no image above them.
    cap_i = next(i for i, p in enumerate(paras)
                 if caption_needle in p.text.lower() and p.style.name == "Caption")
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


def fig_removal_share(s):
    """Figure 6, rebuilt: removal against the impact area rather than the corridor.

    The previous version measured the corridor against itself (4,875 of 6,095 = 80%),
    which is the framing the 12 Aug review asked us to drop. Same 4,875 spaces, shown
    against the two denominators that survive: all on-street parking within the
    corridors and their 100-metre influence area, and all parking within it.
    """
    removed = s["removed"]
    segs = [("Removed", removed, g.RED),
            ("Retained or re-established on the corridors", s["retained"], g.BLUE),
            ("Cross-streets within 100 m", s["cross_street"], g.RAMP[0]),
            ("Off-street", s["off_street"], g.VIOLET)]

    bars = [("All on-street parking\nin the impact area", segs[:3], s["on_street"]),
            ("All parking\nin the impact area", segs, s["total"])]

    fig, ax = plt.subplots(figsize=(6.4, 2.45))
    for i, (_, parts, total) in enumerate(bars):
        left = 0
        for label, value, colour in parts:
            ax.barh(i, value, left=left, color=colour, height=0.5, zorder=3,
                    label=label if i == 1 else None)
            if value / s["total"] > 0.075:
                ax.text(left + value / 2, i, f"{value:,}", va="center", ha="center",
                        fontsize=8.3, fontweight="bold", color="white", zorder=4)
            left += value
        ax.text(total + s["total"] * 0.015, i,
                f"{100.0 * removed / total:.0f}% removed", va="center", fontsize=9,
                fontweight="bold", color=g.RED)

    ax.set_yticks(range(len(bars)))
    ax.set_yticklabels([b[0] for b in bars], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, s["total"] * 1.17)
    ax.set_xticks([])
    g.bare(ax)
    g.title(ax, f"Parking removed as a share of the impact area — the same {removed:,} "
                f"spaces against two denominators")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, fontsize=7.6,
              frameon=False, handlelength=0.9, handleheight=0.9)
    return g.save(fig, "fig09_removal_share_impact_area.png", legend_below=True,
                  note="Impact area = Corridors 1 and 2 and their 100-metre influence "
                       "area. Basis: v2 conceptual design; Corridor 3 is withheld "
                       "pending its design.")


def fig_displacement_vs_capacity(f):
    """Figure 13, rebuilt: capacity removed and how much of it was actually in use.

    The old version paired spaces removed against displaced demand with nothing to
    scale them by. This sets both against the on-street kerb each area has - the
    surveyed corridor kerb plus the cross-streets within 100 m - and splits the removal
    into the part that carried a vehicle at the area's busiest hour and the part that
    stood empty. The pale segment is the report's central demand-side finding made
    visible: 1,886 spaces go, but only 1,123 of them were in use when the area was at
    its fullest.

    Off-street is excluded. The residential yards are no longer a recommended measure,
    so counting them would rest the picture on capacity the ADB has ruled out.

    No percentages are printed. The kerb bar contains the spaces being removed, so any
    share taken against it would describe how much of the area's kerb is affected rather
    than how much room remains - a distinction too easily misread. The quantities are
    left to speak for themselves.
    """
    A, ALL = f["areas"], f["all"]
    order = ["kentron", "komitas", "mega", "garegin", "shiraz", "malatia"]
    rows = []
    for k in order:
        a = A[k]
        kerb = a["spaces"] + a["absorb_onstreet"]
        rows.append((g.SHORT[k], a["spaces"], a["absorb_onstreet"], kerb,
                     a["removed"], a["displaced"]))

    fig, ax = plt.subplots(figsize=(6.4, 3.15))
    y = list(range(len(rows)))
    h = 0.34
    mx = max(r[3] for r in rows)
    ax.barh([i - h / 2 - 0.03 for i in y], [r[1] for r in rows], color=g.MUTED,
            height=h, zorder=3, label="Kerb on the corridors (surveyed)")
    ax.barh([i - h / 2 - 0.03 for i in y], [r[2] for r in rows],
            left=[r[1] for r in rows], color=g.RAMP[0], height=h, zorder=3,
            label="Cross-streets within 100 m")
    ax.barh([i + h / 2 + 0.03 for i in y], [r[5] for r in rows], color=g.RED,
            height=h, zorder=3, label="Removed AND occupied at the peak hour")
    ax.barh([i + h / 2 + 0.03 for i in y], [r[4] - r[5] for r in rows],
            left=[r[5] for r in rows], color="#f0b9b4", height=h, zorder=3,
            label="Removed but empty at the peak hour")

    for i, r in enumerate(rows):
        ax.text(r[3] + mx * 0.015, i - h / 2 - 0.03, f"{r[3]:,}", va="center",
                fontsize=8, color="#6f6f6f")
        ax.text(r[4] + mx * 0.015, i + h / 2 + 0.03,
                f"{r[4]:,} removed - {r[5]:,} in use",
                va="center", fontsize=8.1, fontweight="bold", color=g.RED)

    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, mx * 1.42)
    ax.set_xticks([])
    g.bare(ax)
    tr = sum(r[4] for r in rows)
    td = sum(r[5] for r in rows)
    g.title(ax, f"Parking removed and demand displaced, against each area's on-street "
                f"kerb - {tr:,} spaces removed, {td:,} of them in use at the peak hour")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=2, fontsize=7.3,
              frameon=False, handlelength=0.9, handleheight=0.9)
    return g.save(fig, "fig16_displacement_both.png", legend_below=True,
                  note="On-street kerb is the parking surveyed in each area plus the "
                       "cross-streets within 100 metres. Off-street parking is excluded. "
                       "The paler segment is capacity removed that carried no vehicle at "
                       "the area's busiest hour.")


def swap_any(doc, needles, png):
    """Swap against whichever caption wording is currently in the document.

    These figures get retitled as part of the same pass, so a second run must match the
    new caption as well as the original one. Returns the caption paragraph so the caller
    can rename it.
    """
    for needle in needles:
        cap = next((p for p in doc.paragraphs
                    if needle in p.text.lower() and p.style.name == "Caption"), None)
        if cap is not None:
            swap(doc, needle, png)
            return cap
    raise LookupError(f"no caption matched any of {needles}")


def main():
    f = rf.survey()
    g.fig10_peak_occupancy(f)
    print("WROTE", os.path.basename(PNG))
    share_png = fig_removal_share(rf.supply())
    disp_png = fig_displacement_vs_capacity(f)

    doc = Document(DOC)
    swap_any(doc, ["peak-hour occupancy by surveyed area",
                   "occupancy at each area's busiest hour"], PNG)

    cap6 = swap_any(doc, ["parking removed and retained by corridor",
                          "parking removed as a share of the impact area"], share_png)
    dx.set_caption(cap6, "Figure", "Parking removed as a share of the impact area",
                   number=6)

    cap13 = swap_any(doc, ["measured displacement by area",
                           "parking removed and demand displaced"], disp_png)
    dx.set_caption(cap13, "Figure",
                   "Parking removed and demand displaced, by area", number=13)

    doc.save(DOC)
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
