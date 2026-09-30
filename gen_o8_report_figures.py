# -*- coding: utf-8 -*-
"""Figures for the Output 8 revision (30072026).

Replaces the eight figures embedded in the June draft. Those were screenshots of
the web app whose stat panels had gone badly stale (Figure 1 still showed 15,255
free spaces, Figure 7 showed 7,479 off-street) — the exact inconsistency the
reviewer's first comment is about. Rendering them from report_figures.py instead
means they cannot drift from the tables again, and re-running this script after any
GeoJSON change re-cuts every figure. The spatial view they used to carry is still
available to the reader: the report links the live interactive map.

Also renders the charts for the new occupancy chapter (methodology, locations and
results broken down by typology), which answers the reviewer's heaviest comment.

Palette is the one validated with the dataviz skill's validate_palette.js for
gen_parking_slide_charts.py — reused verbatim so the reports and the ADB deck read
as one system:
  blue   #1565C0  primary / on-street
  violet #7C4DFF  off-street / yards (the app's own yard colour)
  red    #C62828  emphasis: over capacity / removed / displaced
  ordinal blue ramp #86b6ef #3987e5 #1c5cab #0d366b for the duration bins
Red/green status pairs are deliberately avoided (they fail CVD separation), so
"over capacity" is carried by emphasis red against blue, never red against green.
"""
import os
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import report_figures as rf

OUT = os.path.join(rf.ROOT, "Field Surveys/Field Surveys Report/Charts/o8")

BLUE = "#1565C0"
VIOLET = "#7C4DFF"
RED = "#C62828"
MUTED = "#D6D6D6"
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
INK = "#0b0b0b"
AXIS = "#898781"
GRID = "#e1e0d9"

plt.rcParams.update({
    "font.family": "Calibri",
    "font.size": 9,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.edgecolor": AXIS,
    "text.color": INK,
})

AREA_ORDER = ["kentron", "komitas", "mega", "garegin", "shiraz", "malatia"]
SHORT = {"kentron": "Kentron", "komitas": "Komitas", "mega": "Gai Avenue",
         "garegin": "Garegin Nzhdeh", "shiraz": "Shiraz / Hasratyan",
         "malatia": "Malatia-Sebastia"}


def title(ax, text, pad=8, width=86):
    """Titles are wrapped rather than clipped — a long title silently running off
    the right edge is how Figure 1 lost its scope caveat in an earlier draft."""
    ax.set_title("\n".join(textwrap.wrap(text, width)), fontsize=9.5,
                 fontweight="bold", loc="left", pad=pad)


def bare(ax, keep=()):
    for s in ("top", "right", "left", "bottom"):
        if s not in keep:
            ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def save(fig, name, note=None, legend_below=False):
    """Lay out, optionally footnote, and write. The footnote is drawn only after
    tight_layout has reserved room for it — matplotlib does not account for
    fig.text, so drawing it first lands it on top of the axis labels."""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    h = fig.get_figheight()
    reserve = 0.0
    if note:
        reserve += (0.20 if len(note) < 110 else 0.32) / h
    if legend_below:
        reserve += 0.26 / h
    fig.tight_layout(pad=0.35, rect=(0, reserve, 1, 1))
    if note:
        fig.text(0.012, 0.012, note, fontsize=7.2, color=AXIS, va="bottom", wrap=True)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("wrote", os.path.basename(path))
    return path


def hbar(rows, name, head=None, unit="spaces", colors=None, width=6.4, height=None,
         note=None, total=None):
    """Horizontal labelled bar chart — the workhorse for the supply breakdowns.
    Every bar carries its own value and share, so the chart is readable without
    reference to the axis and cannot disagree with the table beside it."""
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    tot = total or sum(vals)
    colors = colors or [BLUE] * len(rows)
    fig, ax = plt.subplots(figsize=(width, height or (0.52 * len(rows) + 1.05)))
    y = list(range(len(rows)))
    ax.barh(y, vals, color=colors, height=0.6, zorder=3)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.015, i, f"{v:,}  ({100.0 * v / tot:.1f}%)",
                va="center", ha="left", fontsize=8.5, fontweight="bold",
                color=colors[i])
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, max(vals) * 1.34)
    ax.set_xticks([])
    bare(ax)
    if head:
        title(ax, head)
    return save(fig, name, note=note)


# ---------------------------------------------------------------------------
# Figures 1-8 — supply inventory and design impact
# ---------------------------------------------------------------------------
def fig1_aggregate(s):
    rows = [("On-street, on the corridors", s["on_corridor"]),
            ("On-street, cross-streets\n(100 m influence area)", s["cross_street"]),
            ("Off-street yards and lots", s["off_street"])]
    return hbar(rows, "fig01_aggregate_supply.png",
                head=f"Aggregate parking supply — {s['total']:,} spaces "
                      f"(Corridors 1 and 2 and their 100 m influence area)",
                colors=[BLUE, RAMP[0], VIOLET], height=2.15,
                note=f"{s['on_street_segments']} on-street segments and "
                     f"{s['off_street_facilities']} off-street facilities surveyed.")


def fig2_zones(s):
    z = s["zones"]
    rows = [("Free / unregulated", z["free"]), ("Zone B (blue) — paid", z["zone_b"]),
            ("Zone A (red) — paid", z["zone_a"]), ("Taxi", z["taxi"])]
    return hbar(rows, "fig02_regulatory_zone.png",
                head=f"On-corridor on-street supply by regulatory zone "
                      f"({s['on_corridor']:,} spaces)",
                colors=[MUTED, "#42a5f5", RED, "#888888"], height=2.3,
                note="Zone A concentrates in Kentron; Zone B is almost entirely "
                     "Komitas Avenue (522 of 534 spaces).")


def fig3_configuration(s):
    m = s["methods"]
    rows = [("Parallel", m["parallel"]), ("Perpendicular (90°)", m["90"])]
    return hbar(rows, "fig03_configuration.png",
                head=f"On-corridor on-street supply by marked configuration "
                      f"({s['on_corridor']:,} spaces)",
                colors=[BLUE, RAMP[0]], height=1.6,
                note="Marked configuration. How vehicles actually parked is a "
                     "different distribution — see the field survey chapter.")


def fig4_location(s):
    lo = s["locations"]
    rows = [("On-street (road edge)", lo["on-street"]),
            ("Pocket (inset into kerb)", lo["pocket"]),
            ("Set-back (separated from road)", lo["set-back"])]
    return hbar(rows, "fig04_location.png",
                head=f"On-corridor on-street supply by physical location "
                      f"({s['on_corridor']:,} spaces)",
                colors=[BLUE, RAMP[1], RAMP[0]], height=1.95)


def _yes_no(s, key_yes, key_no, name, head, note=None):
    rows = [("Present", s[key_yes]), ("Absent", s[key_no])]
    return hbar(rows, name, head=head, colors=[BLUE, MUTED], height=1.6, note=note)


def fig5_signage(s):
    return _yes_no(s, "signage_yes", "signage_no", "fig05_signage.png",
                   f"Parking signage on the {s['on_corridor']:,} on-corridor spaces",
                   note="Four fifths of corridor parking gives the driver no "
                        "regulatory indication at all.")


def fig6_marking(s):
    return _yes_no(s, "marking_yes", "marking_no", "fig06_marking.png",
                   f"Pavement marking on the {s['on_corridor']:,} on-corridor spaces")


def fig7_offstreet(s):
    rows = [("Gated residential courtyards", s["off_street_yards"]),
            ("Named commercial and\ninstitutional facilities", s["off_street_named"])]
    return hbar(rows, "fig07_absorptive_offstreet.png",
                head=f"Off-street absorptive capacity — {s['off_street']:,} spaces "
                      f"in {s['off_street_facilities']} facilities",
                colors=[VIOLET, RAMP[1]], height=1.85,
                note="The courtyard share is counted at gross capacity as if already "
                     "open — which is why opening the yards is a prerequisite, not an option.")


def fig8_onstreet(s):
    rows = [("Cross-street on-street spaces\nwithin 100 m of the corridors",
             s["cross_street"]),
            ("Retained or re-established\non the corridors", s["retained"])]
    return hbar(rows, "fig08_absorptive_onstreet.png",
                head="On-street absorptive capacity after the conceptual design",
                colors=[RAMP[0], BLUE], height=1.85, total=s["cross_street"] + s["retained"],
                note="Most cross-street capacity is currently unpriced and unmarked, "
                     "so it absorbs demand only once delineated and brought into the zone system.")


def fig9_impact(s):
    """Removal and retention per corridor — the figure the reviewer's first comment
    is really about, so it states the v2 basis on its face."""
    cors = list(s["corridors"].items())
    fig, ax = plt.subplots(figsize=(6.4, 2.3))
    y = list(range(len(cors)))
    removed = [c["removed"] for _, c in cors]
    retained = [c["retained"] for _, c in cors]
    ax.barh(y, removed, color=RED, height=0.55, zorder=3, label="Removed")
    ax.barh(y, retained, left=removed, color=BLUE, height=0.55, zorder=3,
            label="Retained or re-established")
    for i, (_, c) in enumerate(cors):
        ax.text(c["existing"] + 60, i, f"{c['existing']:,} existing", va="center",
                fontsize=8.5, color=INK)
        ax.text(c["removed"] / 2, i, f"{c['removed']:,}", va="center", ha="center",
                fontsize=8.5, fontweight="bold", color="white")
        if c["retained"] > 260:
            ax.text(c["removed"] + c["retained"] / 2, i, f"{c['retained']:,}",
                    va="center", ha="center", fontsize=8.5, fontweight="bold",
                    color="white")
    ax.set_yticks(y)
    ax.set_yticklabels([f"Corridor {k[-1]}  ({c['km']} km)" for k, c in cors], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, max(c["existing"] for _, c in cors) * 1.28)
    ax.set_xticks([])
    bare(ax)
    title(ax, f"Parking removed and retained by corridor — {s['removed']:,} of "
              f"{s['on_corridor']:,} on-corridor spaces removed ({s['removed_pct']:.0f}%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=7.8,
              frameon=False, handlelength=0.9, handleheight=0.9)
    return save(fig, "fig09_impact_by_corridor.png", legend_below=True,
                note="Basis: v2 conceptual design, Corridors 1 and 2. Corridor 3 is "
                     "withheld pending its design. Figures will be re-cut when the "
                     "design is final.")


# ---------------------------------------------------------------------------
# Field occupancy survey chapter
# ---------------------------------------------------------------------------
def fig10_peak_occupancy(f):
    # Area-wide busiest clock hour, not the sum of each zone's own peak. The ADB
    # review of 12 Aug 2026 could not reproduce the old basis from the raw data, and
    # was right: summing zone peaks that fall at different hours counts vehicles that
    # were never present together. Zone-level peaks still appear elsewhere, where the
    # question is which individual kerbs saturate.
    rows = [(SHORT[k], f["areas"][k]["peak_hour_pct"]) for k in AREA_ORDER]
    fig, ax = plt.subplots(figsize=(6.4, 2.5))
    y = list(range(len(rows)))
    vals = [r[1] for r in rows]
    colors = [RED if v >= 85 else BLUE for v in vals]
    ax.barh(y, vals, color=colors, height=0.6, zorder=3)
    ax.axvline(85, color="#6f6f6f", lw=1.1, ls="--", zorder=4)
    ax.text(85, -0.85, " 85% target", fontsize=7.5, color="#6f6f6f", va="bottom")
    for i, v in enumerate(vals):
        ax.text(v + 2, i, f"{v}%", va="center", fontsize=8.5, fontweight="bold",
                color=colors[i])
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xticks([0, 50, 85, 100])
    ax.set_xticklabels(["0", "50", "85", "100%"], fontsize=7.5, color=AXIS)
    ax.xaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    bare(ax)
    ax.barh([0], [0], color=RED, label="At or above the 85% target")
    ax.barh([0], [0], color=BLUE, label="Below the 85% target")
    ax.legend(loc="lower right", fontsize=7.5, frameon=False, handlelength=0.9,
              handleheight=0.9, borderpad=0.1)
    title(ax, f"Occupancy at each area's busiest hour (all six areas "
              f"{f['all']['peak_hour_pct']}%)", pad=14)
    return save(fig, "fig10_peak_occupancy_by_area.png",
                note="Distinct vehicles using the area's kerb during its busiest clock "
                     "hour, divided by its capacity. Areas peak at different times, so "
                     "each bar is read at its own hour; individual zones run higher.")


def fig11_hourly(f):
    vap = f["all"]["hourly"]
    hours = [h for h, _ in vap]
    cars = [c for _, c in vap]
    peak = max(range(len(cars)), key=lambda i: cars[i])
    colors = [RAMP[3] if i == peak else BLUE for i in range(len(cars))]
    fig, ax = plt.subplots(figsize=(6.4, 2.1))
    ax.bar(hours, cars, color=colors, width=0.74, zorder=3)
    ax.annotate(f"peak {hours[peak]:02d}:00 · {cars[peak]:,} vehicles",
                xy=(hours[peak], cars[peak]),
                xytext=(hours[peak] + 1.2, cars[peak] + 190),
                fontsize=8, color=INK, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=AXIS, lw=1))
    ax.set_ylim(0, max(cars) * 1.28)
    ax.set_xticks([7, 10, 13, 16, 19, 23])
    ax.set_xticklabels(["07:00", "10:00", "13:00", "16:00", "19:00", "23:00"],
                       fontsize=7.5, color=AXIS)
    ax.set_yticks([0, 700, 1400])
    ax.set_yticklabels(["0", "700", "1,400"], fontsize=7.5, color=AXIS)
    ax.yaxis.grid(True, color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    bare(ax)
    title(ax, "Vehicles present by clock hour, all six areas combined")
    return save(fig, "fig11_hourly_demand_profile.png")


def fig12_stay_mix(f):
    bins = [("1 hour or less", "shortPct"), ("1–2 hours", "errandPct"),
            ("2–8 hours", "workerPct"), ("8 hours or more", "alldayPct")]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    left = [0] * len(AREA_ORDER)
    y = list(range(len(AREA_ORDER)))
    for j, (label, key) in enumerate(bins):
        vals = [f["areas"][k]["stay"][key] for k in AREA_ORDER]
        ax.barh(y, vals, left=left, color=RAMP[j], height=0.62, zorder=3, label=label)
        for i, v in enumerate(vals):
            if v >= 8:
                ax.text(left[i] + v / 2, i, f"{v}%", va="center", ha="center",
                        fontsize=7.8, fontweight="bold",
                        color="white" if j >= 2 else INK)
        left = [left[i] + vals[i] for i in range(len(vals))]
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[k] for k in AREA_ORDER], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    bare(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=4, fontsize=7.6,
              frameon=False, handlelength=0.9, handleheight=0.9)
    title(ax, f"Duration of stay by area — {f['all']['stay']['shortPct']}% of all "
              f"stays are one hour or less")
    return save(fig, "fig12_duration_of_stay.png", legend_below=True)


def fig13_turnover(f):
    rows = [(SHORT[k], f["areas"][k]["turnover"], f["areas"][k]["avg_stay_h"])
            for k in AREA_ORDER]
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    y = list(range(len(rows)))
    ax.barh(y, [r[1] for r in rows], color=BLUE, height=0.58, zorder=3)
    for i, r in enumerate(rows):
        ax.text(r[1] + 0.08, i, f"{r[1]} per space   ·   avg stay {r[2]} h",
                va="center", fontsize=8.3, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, max(r[1] for r in rows) * 1.75)
    ax.set_xticks([])
    bare(ax)
    title(ax, "Turnover by area — vehicles per space per day")
    return save(fig, "fig13_turnover_by_area.png",
                note="Turnover = parking events divided by formal capacity, per area. A "
                     "parking event is one continuous run of hours a plate is present.")


def fig14_observed_method(s, v):
    """How vehicles actually parked, against how the kerb is marked — the typology
    breakdown the reviewer asked for, and the evidence that the marked inventory
    understates angled parking."""
    marked = s["methods"]
    tot_m = sum(marked.values())
    obs = v["all"]["shares"]["method"]
    cats = [("Parallel", 100.0 * marked["parallel"] / tot_m, obs.get("parallel", 0)),
            ("45° angled", 0.0, obs.get("angled45", 0)),
            ("Perpendicular (90°)", 100.0 * marked["90"] / tot_m,
             obs.get("perpendicular", 0))]
    fig, ax = plt.subplots(figsize=(6.4, 2.25))
    y = list(range(len(cats)))
    h = 0.34
    ax.barh([i - h / 2 - 0.02 for i in y], [c[1] for c in cats], color=MUTED, height=h,
            zorder=3, label="As marked (supply inventory)")
    ax.barh([i + h / 2 + 0.02 for i in y], [c[2] for c in cats], color=BLUE, height=h,
            zorder=3, label="As parked (field survey)")
    for i, c in enumerate(cats):
        ax.text(c[1] + 1, i - h / 2 - 0.02, f"{c[1]:.0f}%", va="center", fontsize=8,
                color="#6f6f6f")
        ax.text(c[2] + 1, i + h / 2 + 0.02, f"{c[2]:.0f}%", va="center", fontsize=8,
                fontweight="bold", color=BLUE)
    ax.set_yticks(y)
    ax.set_yticklabels([c[0] for c in cats], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 88)
    ax.set_xticks([])
    bare(ax)
    ax.legend(loc="lower right", fontsize=7.6, frameon=False, handlelength=0.9,
              handleheight=0.9, borderpad=0.1)
    title(ax, "Parking configuration: as marked against as actually parked")
    return save(fig, "fig14_configuration_observed.png",
                note="No 45° parking is marked anywhere on the corridors, yet "
                     f"{obs.get('angled45', 0):.0f}% of observed vehicles parked at 45°.")


def fig15_kerb_location(v):
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    y = list(range(len(AREA_ORDER)))
    cats = [("On the carriageway", "carriageway", BLUE),
            ("On the footpath", "footpath", RED),
            ("In a setback", "setback", RAMP[0])]
    left = [0] * len(AREA_ORDER)
    for label, key, colour in cats:
        vals = []
        for k in AREA_ORDER:
            a = v["areas"][k]
            n = sum(x for kk, x in a["location"].items() if kk)
            vals.append(100.0 * a["location"].get(key, 0) / n if n else 0)
        ax.barh(y, vals, left=left, color=colour, height=0.62, zorder=3, label=label)
        for i, val in enumerate(vals):
            if val >= 9:
                ax.text(left[i] + val / 2, i, f"{val:.0f}%", va="center", ha="center",
                        fontsize=7.8, fontweight="bold", color="white")
        left = [left[i] + vals[i] for i in range(len(vals))]
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[k] for k in AREA_ORDER], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    bare(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=3, fontsize=7.6,
              frameon=False, handlelength=0.9, handleheight=0.9)
    off = 100 - v["all"]["shares"]["location"].get("carriageway", 0)
    title(ax, f"Where vehicles actually stood — {off:.0f}% parked off the carriageway")
    return save(fig, "fig15_kerb_location_by_area.png", legend_below=True,
                note="Off-carriageway parking is informal encroachment the supply inventory "
                     "does not capture. It is not recorded as illegal: overt illegality was "
                     f"only {v['all']['shares']['legal'].get('illegal', 0):.1f}% of sightings.")


def fig16_displacement(f):
    fig, ax = plt.subplots(figsize=(6.4, 2.75))
    y = list(range(len(AREA_ORDER)))
    h = 0.36
    removed = [f["areas"][k]["removed"] for k in AREA_ORDER]
    displaced = [f["areas"][k]["displaced"] for k in AREA_ORDER]
    ax.barh([i - h / 2 - 0.02 for i in y], removed, color=MUTED, height=h, zorder=3,
            label="Spaces removed")
    ax.barh([i + h / 2 + 0.02 for i in y], displaced, color=RED, height=h, zorder=3,
            label="Vehicles needing re-homing (peak hour)")
    for i, k in enumerate(AREA_ORDER):
        a = f["areas"][k]
        ax.text(removed[i] + 12, i - h / 2 - 0.02, f"{removed[i]:,}", va="center",
                fontsize=8, color="#6f6f6f")
        ax.text(displaced[i] + 12, i + h / 2 + 0.02,
                f"{displaced[i]:,}  ({a['displaced_pct']:.0f}% of removed · "
                f"{a['absorbed_onstreet_pct']}% re-absorbed on-street)",
                va="center", fontsize=8, fontweight="bold", color=RED)
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[k] for k in AREA_ORDER], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, max(removed) * 2.5)
    ax.set_xticks([])
    bare(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=7.6,
              frameon=False, handlelength=0.9, handleheight=0.9)
    a = f["all"]
    title(ax, f"Measured displacement by area — {a['displaced']:,} vehicles against "
              f"{a['removed']:,} spaces removed ({a['displaced_pct']:.0f}%)")
    return save(fig, "fig16_displacement_by_area.png", legend_below=True,
                note="Displaced demand is counted at each area's own busiest hour and "
                     "summed. Fewer vehicles need re-homing than spaces are lost because "
                     "the kerb is not full everywhere at once.")


def fig17_truck_share(v):
    rows = sorted(((SHORT[k], v["areas"][k]["truck_pct"], v["areas"][k]["trucks"],
                    v["areas"][k]["classified"]) for k in AREA_ORDER),
                  key=lambda r: -r[1])
    city = v["all"]["truck_pct"]
    fig, ax = plt.subplots(figsize=(6.4, 2.4))
    y = list(range(len(rows)))
    colors = [RED if r[1] > city * 1.5 else BLUE for r in rows]
    ax.barh(y, [r[1] for r in rows], color=colors, height=0.58, zorder=3)
    ax.axvline(city, color="#6f6f6f", lw=1.1, ls="--", zorder=4)
    ax.text(city, -0.8, f" all areas {city}%", fontsize=7.5, color="#6f6f6f",
            va="bottom")
    for i, r in enumerate(rows):
        ax.text(r[1] + 0.2, i, f"{r[1]}%   ({r[2]:,} of {r[3]:,})", va="center",
                fontsize=8.3, fontweight="bold", color=colors[i])
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlim(0, max(r[1] for r in rows) * 1.95)
    ax.set_xticks([])
    bare(ax)
    title(ax, "Freight presence by area — truck share of classified vehicles", pad=14)
    return save(fig, "fig17_truck_share_by_area.png",
                note="Loading provision should be sized to these pockets rather than "
                     "distributed uniformly along the corridors.")


if __name__ == "__main__":
    s, f, v = rf.supply(), rf.survey(), rf.vehicles()
    fig1_aggregate(s)
    fig2_zones(s)
    fig3_configuration(s)
    fig4_location(s)
    fig5_signage(s)
    fig6_marking(s)
    fig7_offstreet(s)
    fig8_onstreet(s)
    fig9_impact(s)
    fig10_peak_occupancy(f)
    fig11_hourly(f)
    fig12_stay_mix(f)
    fig13_turnover(f)
    fig14_observed_method(s, v)
    fig15_kerb_location(v)
    fig16_displacement(f)
    fig17_truck_share(v)
    print("\nAll figures written to", OUT)
