# -*- coding: utf-8 -*-
"""Charts for the parking slides in the final ADB mission presentation.

Renders PNGs consumed by gen_parking_final_slides.py. Data is read live from
app/static/data/wgs84/field-surveys.geojson (the single source of truth per
CLAUDE.md) so the charts cannot drift from the app or the reports.

Palette is NOT hand-picked. It was validated with the dataviz skill's
validate_palette.js against a white slide surface:

  blue    #1565C0  on-street / primary series
  violet  #7C4DFF  off-street / yards   (matches the app's own yard colour)
  red     #C62828  emphasis: over capacity / displaced
    -> 3-series all-pairs: CVD ΔE 9.1 (protan), normal-vision 15.6, contrast all >=3:1  PASS

  ordinal blue ramp for the duration bins (short->long = light->dark):
  #86b6ef #3987e5 #1c5cab #0d366b
    -> monotone L, adjacent ΔL >= 0.06, light end 2.11:1, single hue  PASS

Deliberately NOT used: the April deck's red/green status pair (#C62828 vs
#2E7D32) fails CVD separation at ΔE 4.2 (deuteranopia, floor 6) — a red-green
colourblind viewer cannot tell "over capacity" from "healthy". Occupancy
therefore uses EMPHASIS (accent red vs blue) rather than a red/green scale.
"""

import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = "C:/Users/user/Yerevan-Parking"
GEO = ROOT + "/app/static/data/wgs84/field-surveys.geojson"
OUT = ROOT + "/Final Presentation/.slide-assets"

BLUE = "#1565C0"
VIOLET = "#7C4DFF"
RED = "#C62828"
MUTED_BAR = "#D6D6D6"
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
INK = "#0b0b0b"
SECOND = "#52514e"
AXIS = "#898781"
GRID = "#e1e0d9"

FONT = "Calibri"
plt.rcParams.update({
    "font.family": FONT,
    "font.size": 9,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.edgecolor": AXIS,
    "text.color": INK,
})

AREA_LABEL = {"kentron": "Kentron", "komitas": "Komitas", "mega": "Gai Avenue",
              "garegin": "Garegin Nzhdeh", "shiraz": "Shiraz / Hasratyan",
              "malatia": "Malatia-Sebastia"}


def load():
    d = json.load(open(GEO, encoding="utf-8"))
    return d["areaStats"], d["displacement"]


def val(block, label):
    for x in block:
        if x["label"] == label:
            return x["value"]
    return None


def bare(ax):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def chart_occupancy(stats, path):
    """Peak occupancy by area. Emphasis: over-capacity in red, rest in blue."""
    rows = [(AREA_LABEL[k], val(v["occupancy"], "Peak Occupancy % (cap-weighted)"))
            for k, v in stats.items() if k != "all"]
    rows.sort(key=lambda r: r[1], reverse=True)
    names = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    colors = [RED if v >= 100 else BLUE for v in vals]

    fig, ax = plt.subplots(figsize=(4.8, 2.55))
    y = range(len(rows))
    ax.barh(list(y), vals, color=colors, height=0.62, zorder=3)
    ax.axvline(100, color="#b0b0b0", lw=1, zorder=2)

    for i, v in enumerate(vals):
        ax.text(v + 2, i, "%d%%" % v, va="center", ha="left", fontsize=9,
                fontweight="bold", color=RED if v >= 100 else BLUE)
    ax.set_yticks(list(y))
    ax.set_yticklabels(names, fontsize=8.5, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 158)
    ax.set_xticks([0, 50, 100, 150])
    ax.set_xticklabels(["0", "50", "100", "150%"], fontsize=7.5, color=AXIS)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    bare(ax)
    # legend: identity never by colour alone
    ax.barh([0], [0], color=RED, label="Above capacity")
    ax.barh([0], [0], color=BLUE, label="Within capacity")
    ax.legend(loc="lower right", fontsize=7.5, frameon=False,
              handlelength=0.9, handleheight=0.9, borderpad=0.1)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def chart_hourly(stats, path):
    """Vehicles present by clock hour — a single series, so no legend.

    The peak is emphasised with a darker step of the SAME hue, not with red:
    red is reserved here for "over capacity / displaced", and a peak is not a
    fault state. Reusing it would make one colour mean two things in one deck.
    """
    vap = stats["all"]["profile"]["vap"]
    hours = [h for h, _ in vap]
    cars = [c for _, c in vap]
    peak = max(range(len(cars)), key=lambda i: cars[i])
    colors = [RAMP[3] if i == peak else BLUE for i in range(len(cars))]

    fig, ax = plt.subplots(figsize=(4.8, 1.85))
    ax.bar(hours, cars, color=colors, width=0.74, zorder=3)
    ax.annotate("peak %02d:00 · %s cars" % (hours[peak], "{:,}".format(cars[peak])),
                xy=(hours[peak], cars[peak]), xytext=(hours[peak] + 1.5, cars[peak] + 230),
                fontsize=8, color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=1))
    ax.set_ylim(0, 1780)
    ax.set_xticks([7, 10, 13, 16, 19, 23])
    ax.set_xticklabels(["07:00", "10:00", "13:00", "16:00", "19:00", "23:00"],
                       fontsize=7.5, color=AXIS)
    ax.set_yticks([0, 700, 1400])
    ax.set_yticklabels(["0", "700", "1,400"], fontsize=7.5, color=AXIS)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    bare(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def chart_stay(stats, path):
    """Stay-length split — ordinal ramp, short->long = light->dark."""
    d = stats["all"]["profile"]["duration"]
    segs = [("≤1h short visit", d["shortPct"], RAMP[0]),
            ("2–4h errand", d["errandPct"], RAMP[1]),
            ("5–8h worker", d["workerPct"], RAMP[2]),
            (">8h all-day", d["alldayPct"], RAMP[3])]
    fig, ax = plt.subplots(figsize=(4.8, 1.15))
    x = 0.0
    for name, pct, col in segs:
        ax.barh([0], [pct], left=[x], color=col, height=0.5, zorder=3)
        ax.text(x + pct / 2.0, 0, "%d%%" % pct, va="center", ha="center",
                fontsize=9, fontweight="bold",
                color="white" if col != RAMP[0] else INK)
        x += pct + 0.55                    # ~2px surface gap between fills
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in segs]
    ax.legend(handles, ["%s · %d%%" % (n, p) for n, p, _ in segs],
              loc="lower left", bbox_to_anchor=(0, -0.72), ncol=2, fontsize=7.5,
              frameon=False, handlelength=0.9, handleheight=0.9,
              columnspacing=1.2, borderpad=0)
    ax.set_xlim(0, 102)
    ax.set_ylim(-0.45, 0.45)
    ax.set_xticks([]), ax.set_yticks([])
    bare(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def chart_displacement(disp, path):
    """1,643 spaces removed vs 908 cars actually displaced at the peak."""
    fig, ax = plt.subplots(figsize=(4.8, 1.35))
    rows = [("Spaces removed", disp["removed_supply"], MUTED_BAR, SECOND),
            ("Cars displaced\nat the peak hour", disp["removed_demand"], RED, RED)]
    for i, (name, v, col, tcol) in enumerate(rows):
        ax.barh([i], [v], color=col, height=0.46, zorder=3)
        ax.text(v + 30, i, "{:,}".format(v), va="center", ha="left",
                fontsize=13, fontweight="bold", color=tcol)
    ax.set_yticks([0, 1])
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5, color=INK)
    ax.invert_yaxis()
    # derived, not fixed: the headroom has to keep the value label inside the axes,
    # and these figures move whenever the conceptual design is revised
    ax.set_xlim(0, max(r[1] for r in rows) * 1.18)
    ax.set_xticks([])
    bare(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def chart_absorption(disp, path):
    """Where the 908 displaced cars can go: on-street vs off-street."""
    on = disp["absorb_onstreet"]                 # 391 surviving on-street spaces
    need_off = disp["removed_demand"] - on       # 517 must find off-street
    fig, ax = plt.subplots(figsize=(4.8, 1.25))
    ax.barh([0], [on], color=BLUE, height=0.5, zorder=3)
    ax.barh([0], [need_off], left=[on + 6], color=VIOLET, height=0.5, zorder=3)
    ax.text(on / 2.0, 0, "{:,}".format(on), va="center", ha="center", fontsize=10,
            fontweight="bold", color="white")
    ax.text(on + 6 + need_off / 2.0, 0, "{:,}".format(need_off), va="center",
            ha="center", fontsize=10, fontweight="bold", color="white")
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE),
               plt.Rectangle((0, 0), 1, 1, color=VIOLET)]
    ax.legend(handles, ["Absorbed on nearby streets · %d%%"
                        % round(100.0 * on / disp["removed_demand"]),
                        "Must find off-street · %d%%"
                        % round(100.0 * need_off / disp["removed_demand"])],
              loc="lower left", bbox_to_anchor=(0, -0.85), ncol=1, fontsize=7.5,
              frameon=False, handlelength=0.9, handleheight=0.9, borderpad=0)
    # the two segments span the whole displaced-demand figure, so the limit must
    # follow it — a fixed value silently clips the bar when demand rises
    ax.set_xlim(0, (on + 6 + need_off) * 1.02)
    ax.set_ylim(-0.45, 0.45)
    ax.set_xticks([]), ax.set_yticks([])
    bare(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def build():
    os.makedirs(OUT, exist_ok=True)
    stats, disp = load()
    chart_occupancy(stats, OUT + "/chart_occupancy.png")
    chart_hourly(stats, OUT + "/chart_hourly.png")
    chart_stay(stats, OUT + "/chart_stay.png")
    chart_displacement(disp, OUT + "/chart_displacement.png")
    chart_absorption(disp, OUT + "/chart_absorption.png")
    print("charts ->", OUT)
    for f in sorted(os.listdir(OUT)):
        if f.startswith("chart"):
            print("   ", f)


if __name__ == "__main__":
    build()
