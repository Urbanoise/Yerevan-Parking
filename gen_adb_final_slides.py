# -*- coding: utf-8 -*-
"""Parking slides for the final ADB mission — the workstream-shaped cut.

    Parking Slides - ADB Final (6).pptx

Structure follows "Final Presentation/Final Presentation Outline and
Instructions.docx": open with goals and activities, then one slide per survey /
assessment, ending on further studies. It answers "what did you do, what did you
find, what happens next" rather than making an argument, because Yerevan
Municipality attends this one alongside ADB.

This does NOT replace the FULL (11) / TIGHT (5) decks — those are argument-shaped
and lead with "what changed since April". All three are built on the same
ADB Mission_Template.pptx and share one data block, so they cannot contradict
each other: primitives, palette, geometry and DATA are imported from
gen_parking_final_slides rather than copied.

Slide 1's four goals double as the deck's contents: goal 1 -> slides 2 and 3,
goals 2 and 3 -> slide 4, goal 4 -> slide 5.
"""

import os
import shutil

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

import gen_parking_final_slides as base
from gen_parking_final_slides import (
    ASSETS, DATA, ZONES, FONT,
    NAVY, INK, GREY, CARD_BG, CARD_LINE, RED, BLUE, GREEN, AMBER,
    HIGH_T, HIGH_BG, MED_T, LOW_T,
    L, R, CW, ROW1,
    new_deck, base_slide, textbox, write, rect, tile, card, footnote,
    stacked_zone_bar, add_img, grid,
)

# Sampled from the map bitmap itself so the legend swatches match the artwork
# exactly. These are the map's own colours, deliberately NOT the deck's zone
# triad (HIGH_T / MED_T / LOW_T): the legend has to key the image, not the rows.
MAP_HIGH = RGBColor(0xF2, 0x0D, 0x0D)
MAP_MED = RGBColor(0xF2, 0xAF, 0x0D)
MAP_LOW = RGBColor(0x43, 0xF2, 0x0D)

OUT_DECK = base.BASE + "/Parking Slides - ADB Final (6).pptx"

# Extra assets this deck needs, copied into .slide-assets so add_img() works
# unchanged. "yerevan (2).png" is the hand-refined Figure 11 that actually ships
# in Output 10 — fig11_sensitivity_map.jpg is an unused matplotlib render.
EXTRA_ASSETS = {
    "field_survey_locations.png":
        base.BASE + "/Field Survey Locations.png",
    "sensitivity_map.png":
        "C:/Users/user/Yerevan-Parking/Field Surveys/Field Surveys Report/"
        "Charts/yerevan (2).png",
}


def ensure_assets():
    base.ensure_assets()
    for name, src in EXTRA_ASSETS.items():
        shutil.copyfile(src, os.path.join(ASSETS, name))
    print("extra assets ->", ", ".join(sorted(EXTRA_ASSETS)))


def set_notes(slide, text):
    """Speaker notes shown below the slide in Presenter/Notes view."""
    slide.notes_slide.notes_text_frame.text = text


# Speaker narration read while presenting each slide (slides 1–2 are self-
# explanatory and narrated ad-lib from the on-slide numbers).
S3_NOTES = (
    "Everything here is measured, not modelled. Six representative areas, "
    "ordinary mid-week working days at the end of May, licence plates recorded "
    "by hand every hour from seven in the morning to midnight — around 25,000 "
    "observations.\n\n"
    "A word on how to read the occupancy figures, because they go above 100 "
    "percent and that is meaningful, not an error. We walked each area every "
    "hour on the hour and logged every parked car. So the peak figure counts "
    "the distinct vehicles that used a stretch of kerb during its single "
    "busiest hour, measured against how many cars that kerb holds. When Kentron "
    "reads 138 percent, it means that in the busiest hour the kerb served 38 "
    "percent more distinct vehicles than it can hold at one time — because the "
    "parking is short-stay and turns over quickly within the hour. It is a "
    "measure of how hard the kerb works at its peak, not of cars frozen at one "
    "instant. Almost all of this parking is legal — only 0.2 percent was "
    "illegal, and remember that in Yerevan the great majority of legal parking "
    "is on unmarked kerb. So this is about saturation, not rule-breaking.\n\n"
    "The headline is capacity-weighted peak occupancy of 93 percent — "
    "capacity-weighted meaning the big corridors count for more than the small "
    "side streets, so the number reflects where the cars actually are. The "
    "average stay works out to about 1.8 hours.\n\n"
    "But the spread matters more than the average, and that is the chart on the "
    "left — from 54 percent in Malatia-Sebastia up to 138 percent in Kentron. "
    "The survey confirms and quantifies how different these areas are. Kentron "
    "is a commercial core: intense, short-stay. Malatia-Sebastia is "
    "residential — the lowest daytime pressure of the six, but the strongest "
    "overnight signature, which is residential storage rather than turnover. "
    "Same city, same week, two completely different problems — which is why the "
    "mitigation on slide 5 is applied zone by zone, not uniformly.\n\n"
    "The chart at bottom right characterises the demand directly. 63 percent of "
    "stays are an hour or less, 77 percent two hours or less, and genuine "
    "all-day storage is only 7 percent. Turnover runs five to eleven vehicles "
    "per space per day. So the kerb is doing high-turnover retail and errand "
    "work, not commuter storage — and that tells us which measures will "
    "actually bite."
)


def band_label(slide, y, scope, note=None):
    """Scope banner for slide 4, where two different survey scopes share a slide."""
    write(textbox(slide, L, y, 5.60, 0.20), scope, size=8.5, bold=True, color=INK)
    if note:
        write(textbox(slide, R - 4.30, y, 4.30, 0.20, align=PP_ALIGN.RIGHT),
              note, size=8, color=GREY)


def map_legend(slide, x, y):
    """Key the sensitivity map. Without this the map is three unexplained colours."""
    for dx, col, label in ((0.00, MAP_HIGH, "High"), (0.63, MAP_MED, "Medium"),
                           (1.43, MAP_LOW, "Lower")):
        rect(slide, x + dx, y + 0.03, 0.10, 0.10, col)
        write(textbox(slide, x + dx + 0.14, y, 0.60, 0.16), label,
              size=7.5, color=GREY)


def zone_row(slide, x, y, w, h, title, tcolor, bg, meta, measures):
    """One sensitivity band as a wide row: accent | title+meta | measures.

    Rows rather than s_zones' side-by-side columns: once the sensitivity map
    takes the right third, three columns would leave ~1.98in each — too narrow
    for the measure lists.
    """
    rect(slide, x, y, w, h, bg, CARD_LINE)
    rect(slide, x, y, 0.05, h, tcolor)
    write(textbox(slide, x + 0.16, y + 0.09, 2.24, 0.20), title,
          size=9, bold=True, color=tcolor)
    write(textbox(slide, x + 0.16, y + 0.31, 2.30, 0.60), meta.split("\n"),
          size=7.5, color=GREY, space=1)
    write(textbox(slide, x + 2.62, y + 0.09, w - 2.78, h - 0.18),
          ["•  " + m for m in measures], size=7.5, color=INK, space=2)


# --- slides -------------------------------------------------------------------
def s1_overview(prs):
    s = base_slide(prs, "Parking: what we set out to do, and what we did",
                   "Supply, occupancy and off-street context surveyed across the "
                   "three priority corridors and their 100 m influence area")
    card(s, L, ROW1, 5.90, 1.35, "Our goal", None, accent=NAVY, bsize=8.5, bspace=3,
         bullets=["Analyse the existing parking system context along the priority "
                  "corridors and in Yerevan as a whole.",
                  "Assess the impacts of the conceptual corridor designs on "
                  "parking supply.",
                  "Evaluate the potential for parking displacement within the "
                  "defined influence area.",
                  "Identify mitigation options and parking management measures "
                  "that support corridor implementation."])
    card(s, L, 3.02, 5.90, 1.78, "What we did", None, accent=GREEN, bsize=8.5,
         bspace=4,
         bullets=["Parking Supply Survey — desk inventory from 360° video, "
                  "satellite and Yandex imagery, with ~15% cross-checked "
                  "physically in the field.",
                  "Parking Occupancy Survey — six representative areas, "
                  "29 May – 3 June 2026: hourly licence-plate sweeps, 07:00–24:00.",
                  "Off-street context — major facilities on the corridors "
                  "catalogued to test their potential to absorb displaced demand.",
                  "All survey data published and explorable at "
                  "yerevan-parking.vercel.app."])
    add_img(s, "field_survey_locations.png", 6.32, ROW1, w=3.30)
    write(textbox(s, 6.32, 4.70, 3.30, 0.20),
          "Field occupancy survey areas", size=7.5, color=GREY, italic=True)
    footnote(s, "Scale: 994 supply features inventoried; 208 segments and ~2,930 "
                "marked spaces observed, yielding ~24,950 vehicle observations.")
    return s


def s2_supply(prs):
    s = base_slide(prs, "Parking Supply Survey: key data",
                   "15,897 spaces inventoried across the three corridors and "
                   "their 100 m influence areas")
    xs, w = grid(4)
    tiles = [("{:,}".format(DATA["total"]), "Total spaces inventoried", INK),
             ("{:,}".format(DATA["onstreet"]),
              "On-street, across %d segments" % DATA["segments"], INK),
             ("{:,}".format(DATA["offstreet"]),
              "Off-street, across %d facilities" % DATA["facilities"], INK),
             ("{:,}".format(DATA["on_corridor"]),
              "On the corridors themselves", INK)]
    for x, (v, l, c) in zip(xs, tiles):
        tile(s, x, ROW1, w, v, l, color=c, accent=c)
    stacked_zone_bar(s, 2.92)
    card(s, L, 4.02, CW, 0.72,
         "88% of corridor parking is free — and barely organised", None,
         accent=AMBER, bsize=8.5,
         bullets=["Only %d%% has signage and %d%% has markings. Zone A is "
                  "concentrated in Kentron (Nalbandyan 83, Abovyan 46, Amiryan 43); "
                  "Zone B is almost entirely Komitas Avenue (522 of %d)."
                  % (DATA["signage_pct"], DATA["marking_pct"], DATA["zone_b"])])
    footnote(s, "Totals corrected June 2026 (off-street 7,479 → 7,035; total "
                "16,341 → 15,897). On-street and cross-street figures are "
                "unchanged. Paid spaces total 794 — 11.3% of the on-corridor "
                "supply.", y=4.82)
    return s


def s3_occupancy(prs):
    s = base_slide(prs, "Parking Occupancy Survey: key data",
                   "Six representative areas surveyed 29 May – 3 June 2026 — "
                   "hourly licence-plate sweeps, 07:00–24:00")
    write(textbox(s, L, ROW1, 4.86, 0.20), "Peak occupancy by surveyed area",
          size=9, bold=True, color=INK)
    add_img(s, "chart_occupancy.png", L, 1.73, w=4.86)
    write(textbox(s, L, 4.34, 4.86, 0.30),
          "Peak occupancy = distinct vehicles in the busiest hour ÷ parking "
          "capacity (capacity-weighted).", size=7, color=GREY, italic=True)

    tw, th = 2.11, 0.98
    stats = [("%d%%" % DATA["peak_occ"], "Peak occupancy, capacity-weighted", GREEN),
             ("%.1fh" % DATA["avg_stay"], "Average length of stay", INK),
             ("5–11", "Vehicles per space per day", INK),
             ("%d%%" % DATA["d_1h"], "Of stays are one hour or less", BLUE)]
    for i, (v, l, c) in enumerate(stats):
        tile(s, 5.35 + (i % 2) * (tw + 0.19), 1.55 + (i // 2) * (th + 0.08),
             tw, v, l, color=c, accent=c, h=th, vsize=18)

    write(textbox(s, 5.35, 3.70, 4.41, 0.20), "How long vehicles stay",
          size=9, bold=True, color=INK)
    add_img(s, "chart_stay.png", 5.35, 3.86, w=4.41)
    footnote(s, "208 segments · ~2,930 spaces · ~24,950 observations. Because "
                "sweeps are hourly and parking is short-stay, the peak figure "
                "counts distinct vehicles at the busiest hour — peak-hour "
                "intensity of use, not simultaneous fill, so it can pass 100%. "
                "99.8% of vehicles were parked legally (in Yerevan most legal "
                "parking is unmarked).", y=4.82)
    set_notes(s, S3_NOTES)
    return s


def s4_impact(prs):
    s = base_slide(prs, "Impact of the design, and displacement assessment",
                   "The conceptual cross-section removes 85% of on-corridor "
                   "parking; the six surveyed areas measure where those cars go")

    # Band A — corridor-wide (Output 8).
    band_label(s, ROW1, "CORRIDOR-WIDE · impact of the conceptual design",
               "Corridor 1: %s  ·  Corridor 2: %s  ·  Corridor 3: %s"
               % ("{:,}".format(DATA["c1_removed"]),
                  "{:,}".format(DATA["c2_removed"]),
                  "{:,}".format(DATA["c3_removed"])))
    xs, w = grid(4)
    tiles = [("{:,}".format(DATA["on_corridor"]), "On-street, on the corridors", INK),
             ("{:,}".format(DATA["removed"]), "On-street spaces removed", RED),
             ("%d%%" % DATA["removed_pct"], "Of on-corridor parking", RED),
             ("{:,}".format(DATA["retained"]), "Retained or re-established", GREEN)]
    for x, (v, l, c) in zip(xs, tiles):
        tile(s, x, 1.76, w, v, l, color=c, accent=c, h=0.94, vsize=17)

    rect(s, L, 2.84, CW, 0.014, CARD_LINE)

    # Band B — surveyed areas only (geojson). Kept visually separate and labelled:
    # read against the corridor-wide 5,953 above, 908 looks trivial. It is a
    # different scope, not a smaller share.
    band_label(s, 2.94, "SIX SURVEYED AREAS ONLY · measured displacement",
               "A demand overlay — not a re-survey of the full corridor")
    add_img(s, "chart_displacement.png", L, 3.14, w=4.20)

    tw = 1.62
    dt = [("%d%%" % DATA["d_ratio"], "Displaced vs. removed", RED),
          ("%d%%" % DATA["absorb_onstreet"], "Absorbed on-street", BLUE),
          ("%d%%" % DATA["yard_dep"], "Capacity behind gates", HIGH_T)]
    for i, (v, l, c) in enumerate(dt):
        tile(s, 4.66 + i * (tw + 0.12), 3.14, tw, v, l, color=c, accent=c,
             h=1.02, vsize=18)
    write(textbox(s, 4.66, 4.28, 5.10, 0.50),
          "Open and manage the yards BEFORE removing kerb: nearby streets absorb "
          "only 43% (14% in Kentron, 0% in Komitas). Re-absorption reaches ~100% "
          "only via off-street, and 92% of that is gated residential yards.",
          size=8, color=HIGH_T, bold=True)
    footnote(s, "Displacement is measured at a true single clock-hour (908 cars; "
                "summing each zone's own peak would overstate it at 147 vs 93 in "
                "the largest area). Absorbing capacity counts unsurveyed parking "
                "at gross capacity, so it is a best case: the yards were never "
                "occupancy-surveyed.", y=4.84)
    return s


def s5_mitigation(prs):
    s = base_slide(prs, "Mitigation measures and packages by sensitivity zone",
                   "No single measure resolves displacement — the package is "
                   "applied selectively, by measured zone sensitivity")
    zw, zh = 6.28, 1.00
    for i, (title, tcolor, bg, meta, measures) in enumerate(ZONES):
        zone_row(s, L, ROW1 + i * (zh + 0.10), zw, zh, title, tcolor, bg,
                 meta, measures)
    add_img(s, "sensitivity_map.png", 6.72, ROW1, w=2.86)
    map_legend(s, 6.72, 3.70)
    card(s, 6.60, 3.92, 3.10, 0.80, "Exception — Gai Avenue (Mega Mall)", None,
         accent=MED_T, hcolor=MED_T, bsize=7.5,
         bullets=["Kerb parking stays for now; revisit as the area changes — "
                  "mall parking or the planned BRT."])
    footnote(s, "Measures are layered, not singular: each addresses a distinct "
                "facet of displacement, and effectiveness depends on deployment "
                "as an integrated package rather than as standalone "
                "interventions. Map: Output 10, Figure 11.", y=4.80)
    return s


def s6_next_steps(prs):
    s = base_slide(prs, "Further studies and considerations",
                   "Parking is a citywide system and cannot be sustainably "
                   "managed at corridor level alone")
    write(textbox(s, L, ROW1, CW, 0.45),
          "This component is scoped to the BRT corridors and their immediate "
          "influence area. The measures proposed here should therefore be "
          "understood as the first stage of a broader, citywide reform.",
          size=9.5, color=INK)
    xs, w = grid(2)
    card(s, xs[0], 2.10, w, 1.30, "Extend the approach citywide", None,
         accent=NAVY, bsize=8, bspace=3,
         bullets=["Extend the parking supply inventory beyond the corridor "
                  "buffer to a citywide scale.",
                  "Apply focused demand assessments at selected high-pressure "
                  "locations, rather than corridor-wide observational surveys.",
                  "Progressively expand the red-line zonal system into "
                  "neighbourhoods currently outside it."])
    card(s, xs[1], 2.10, w, 1.30, "Supporting studies", None, accent=BLUE,
         bsize=8, bspace=3,
         bullets=["Park & ride feasibility.",
                  "Residential yard opening.",
                  "Legal basis of the resident permit scheme.",
                  "Willingness-to-pay — the empirical foundation for calibrating "
                  "tariffs and guiding the phased roll-out."])
    card(s, L, 3.52, CW, 0.92,
         "Priority: who administers residential-yard opening", None,
         accent=HIGH_T, hcolor=HIGH_T, bsize=8.5,
         bullets=["The yards carry ~92% of the absorptive capacity that makes "
                  "re-absorption work, yet no body currently owns the task. Who "
                  "should lead it, and under what organisational and legal "
                  "arrangement, warrants a dedicated study before any roll-out."])
    footnote(s, "Consistent with the supply-led, spatially targeted methodology "
                "adopted for this assignment.", y=4.86)
    return s


def build(path, slides):
    prs = new_deck()
    for fn in slides:
        fn(prs)
    prs.save(path)
    print("  %-46s %2d slides" % (path.split("/")[-1], len(slides)))


if __name__ == "__main__":
    print("Building the workstream-shaped ADB final mission deck:")
    ensure_assets()
    build(OUT_DECK, [s1_overview, s2_supply, s3_occupancy, s4_impact,
                     s5_mitigation, s6_next_steps])
    print("Done.")
