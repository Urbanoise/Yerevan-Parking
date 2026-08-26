# -*- coding: utf-8 -*-
"""Apply the reviewer's Output 8 comments and refresh every figure onto the
Corridors 1+2 / v2-conceptual-design basis.

Source : Final Presentation/Output 8 - Parking Surveys and Analysis Report 23062026 (rev).docx
Output : Final Presentation/Output 8 - Parking Surveys and Analysis Report 12082026 (rev).docx
         (the 23062026 file is left untouched — it stays the record of the June text)

The six comments on the "Parking & Traffic Survey" sheet of
"Parking Reports Comments spreadsheet.xlsx", and how each is addressed:

  1  General — removed-spaces figures inconsistent with the final conceptual design
     -> every figure re-derived from report_figures.py (v2 design, Corridors 1+2)
        plus an explicit basis-and-status caveat in the impact chapter, the
        executive summary and the conclusions.
  2  Section 5 par 1 oversimplifies: kerb-aligned bus lanes cost as much parking
     as median-aligned ones -> "Nature of the Impact" rewritten.
  3  "leaves no room for parking" is wrong -> rewritten; room remains between
        stations, which is why 1,220 spaces are retained rather than none.
  4  the meaning of 55% -> refreshed to 59% and defined at first use.
  5  the meaning of >100% occupancy, on-street and off-street -> defined in the
        new chapter and flagged at first use.
  6  the occupancy survey has no methodology, no locations and only aggregated
     results -> replaced by a full chapter with per-area and per-typology results.

Reviewer page references for Output 8 do not match this file: the reviewer read it
after it had been merged into the combined Traffic and Parking report. Every comment
is therefore anchored to text, not to a page.

Run gen_o8_report_figures.py first — this script swaps in the PNGs it writes.
"""
import os
import re
import shutil

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import docx_edit as dx
import report_figures as rf

FP = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(FP, "Output 8 - Parking Surveys and Analysis Report 23062026 (rev).docx")
DST = os.path.join(FP, "Output 8 - Parking Surveys and Analysis Report 12082026 (rev).docx")
FIGS = os.path.join(rf.ROOT, "Field Surveys/Field Surveys Report/Charts/o8")

S, F, V, Y = rf.supply(), rf.survey(), rf.vehicles(), rf.yards()
Z, M, L = S["zones"], S["methods"], S["locations"]
C1, C2 = S["corridors"]["Corridor 01"], S["corridors"]["Corridor 02"]
OC = S["on_corridor"]
pc = lambda v, whole=None: rf.pct(v, whole or OC)

# Sensitivity bands, by street stem. The field survey moved Komitas from medium to
# high (123% peak, no on-street absorption) — the reviewer's Output 10 comment about
# Komitas applies here too, since Table 9 is where Output 8 states the banding.
BANDS = {
    "high": ["Nalbandyan", "Abovyan", "Amiryan", "TigranMec", "Moskovyan",
             "Agatangeghosi", "Komitas"],
    "medium": ["Arshakunyac", "Arshakunyac1st", "Kievyan", "Kievyan1st",
               "GareginNzhdeh", "DavitAnhaght"],
}


def band_rows(band):
    """Named streets and their exact on-corridor capacity for a sensitivity band.
    Anything not named in BANDS falls into 'lower', so the three bands sum to the
    full 6,095 and the table can state totals instead of the old '~1,500-1,800'."""
    stems = BANDS.get(band)
    out = []
    for cor in ("Corridor 01", "Corridor 02"):
        for row in S["streets"][cor]:
            stem = next((k for k, v in rf.STREET_LABELS.items() if v == row["street"]),
                        row["street"])
            in_named = stem in (BANDS["high"] + BANDS["medium"])
            if (stems and stem in stems) or (band == "lower" and not in_named):
                out.append(row)
    out.sort(key=lambda r: -r["spaces"])
    return out


def band_text(band, top=5):
    rows = band_rows(band)
    named = ", ".join(f"{r['street']} ({r['spaces']:,})" for r in rows[:top])
    rest = len(rows) - top
    if rest > 0:
        named += f" and {rest} further streets"
    return named, sum(r["spaces"] for r in rows)


# ---------------------------------------------------------------------------
def refresh_numbers(doc):
    """Every headline figure, re-derived. Ordered longest-match-first so a broad
    pattern cannot eat a narrower one."""
    n = 0

    # --- aggregate supply -------------------------------------------------
    dx.set_text(dx.find(doc, "The survey documented a total of 15,897"),
                f"The survey documented a total of {S['total']:,} parking spaces across "
                f"Corridors 1 and 2 and their 100-metre influence areas, comprising "
                f"{S['on_street']:,} on-street spaces (across {S['on_street_segments']} "
                f"line segments) and {S['off_street']:,} off-street spaces (across "
                f"{S['off_street_facilities']} polygon areas with recorded capacity). "
                f"Corridor 3 is not included in this total: its conceptual design has not "
                f"been prepared, so it is withheld from the assessment. For the record, "
                f"the inventory found 896 on-corridor on-street spaces along Corridor 3.")

    dx.rewrite_table(
        dx.find_table(doc, "Total spaces", "Cross-streets"),
        [["Parameter", "On-Street", "Off-Street", "Total"],
         ["Total spaces", f"{S['on_street']:,}", f"{S['off_street']:,}", f"{S['total']:,}"],
         ["Corridor 1", f"{C1['existing']:,}", "-", ""],
         ["Corridor 2", f"{C2['existing']:,}", "", ""],
         ["Cross-streets", f"{S['cross_street']:,}", "", f"{S['cross_street']:,}"],
         ["Yards", "", f"{S['off_street']:,}", f"{S['off_street']:,}"]])

    dx.rewrite_table(dx.find_table(doc, "Features surveyed"),
                     [["Features surveyed", f"{S['on_street_segments']} segments",
                       f"{S['off_street_facilities']} facilities"]], header=False)

    # --- regulatory zone --------------------------------------------------
    paid = Z["zone_a"] + Z["zone_b"]
    dx.set_text(dx.find(doc, "Of the 7,005 on-street spaces surveyed"),
                f"Of the {OC:,} on-street spaces surveyed along the corridors, the vast "
                f"majority ({Z['free']:,} spaces, {pc(Z['free']):.1f}%) have no payment "
                f"zone classification, reflecting the predominance of free parking in the "
                f"city. Only {paid} spaces ({pc(paid):.1f}%) are within the paid parking "
                f"system managed by Parking City Service CJSC. An additional {Z['taxi']} "
                f"spaces ({pc(Z['taxi']):.1f}%) were identified as specialized locations "
                f"for taxi drivers.")

    dx.rewrite_table(
        dx.find_table(doc, "Zone Classification"),
        [["Zone Classification", "Spaces", "Share of Total"],
         ["Zone A (Red) – paid", f"{Z['zone_a']}", f"{pc(Z['zone_a']):.1f}%"],
         ["Zone B (Blue) – paid", f"{Z['zone_b']}", f"{pc(Z['zone_b']):.1f}%"],
         ["Taxi", f"{Z['taxi']}", f"{pc(Z['taxi']):.1f}%"],
         ["Free", f"{Z['free']:,}", f"{pc(Z['free']):.1f}%"],
         ["Total", f"{OC:,}", "100%"]])

    za = dict(S["zone_a_streets"])
    dx.set_text(dx.find(doc, "Zone A spaces are concentrated in Kentron"),
                f"Zone A spaces are concentrated in the Kentron district along Corridor 1, "
                f"primarily on Nalbandyan ({za.get('Nalbandyan', 0)} spaces), Tigran Mets "
                f"({za.get('Tigran Mets', 0)}), Abovyan ({za.get('Abovyan', 0)}), Amiryan "
                f"({za.get('Amiryan', 0)}), Agatangeghos ({za.get('Agatangeghos', 0)}) and "
                f"Moskovyan ({za.get('Moskovyan', 0)}). Zone B spaces are almost entirely "
                f"on Komitas Avenue (522 of the {Z['zone_b']} Zone B spaces) along "
                f"Corridor 2, with a small remainder on Vagharshyan (12).")

    # --- configuration and location --------------------------------------
    dx.rewrite_table(
        dx.find_table(doc, "Parking Method"),
        [["Parking Method", "Spaces", "Share"],
         ["Parallel", f"{M['parallel']:,}", f"{pc(M['parallel']):.1f}%"],
         ["Perpendicular (90°)", f"{M['90']:,}", f"{pc(M['90']):.1f}%"],
         ["Total", f"{OC:,}", "100%"]])

    dx.rewrite_table(
        dx.find_table(doc, "Location Type"),
        [["Location Type", "Spaces", "Share"],
         ["On-street (road edge)", f"{L['on-street']:,}", f"{pc(L['on-street']):.1f}%"],
         ["Pocket (inset into curb)", f"{L['pocket']:,}", f"{pc(L['pocket']):.1f}%"],
         ["Set-back (separated from road)", f"{L['set-back']}", f"{pc(L['set-back']):.1f}%"],
         ["Total", f"{OC:,}", "100%"]])

    dx.set_text(dx.find(doc, "The predominance of parallel parking"),
                f"The predominance of parallel parking ({pc(M['parallel']):.1f}%) and "
                f"on-street location ({pc(L['on-street']):.1f}%) reflects the typical "
                f"curbside parking pattern along arterial corridors. The significant volume "
                f"of 90° perpendicular parking ({M['90']:,} spaces, {pc(M['90']):.1f}%) "
                f"indicates areas where parking has expanded beyond parallel "
                f"configurations, often without formal markings.")

    sh = V["all"]["shares"]
    off = 100 - sh["location"]["carriageway"]
    dx.set_text(dx.find(doc, "The inventory above records marked configuration"),
                f"The inventory above records marked configuration; the field survey "
                f"additionally recorded how vehicles actually parked, and the two do not "
                f"agree. By vehicle, {sh['method']['parallel']:.0f}% parked parallel, "
                f"{sh['method']['angled45']:.0f}% at 45° and "
                f"{sh['method']['perpendicular']:.0f}% perpendicular — even though no 45° "
                f"parking is marked anywhere on the corridors, so more than a quarter of "
                f"observed parking uses a layout the inventory does not record at all. "
                f"About {off:.0f}% of observed parking sat off the carriageway "
                f"({sh['location']['footpath']:.1f}% on footpaths and "
                f"{sh['location']['setback']:.1f}% in setbacks) — informal encroachment the "
                f"supply map does not capture, highest in Malatia-Sebastia (30.9%) and "
                f"Garegin Nzhdeh (30.4%), lowest in Kentron (10.0%) where the kerb is "
                f"most tightly built. Legality was recorded for every vehicle: only about "
                f"{sh['legal']['illegal']:.1f}% was flagged as illegally parked, indicating "
                f"that the kerbside problem is saturation and tolerated informality rather "
                f"than overt illegality.")

    # --- signage and marking ---------------------------------------------
    dx.set_text(dx.find(doc, "have visible parking signage"),
                f"Only {S['signage_yes']:,} of the {OC:,} on-street spaces "
                f"({pc(S['signage_yes']):.1f}%) have visible parking signage. The remaining "
                f"{S['signage_no']:,} spaces ({pc(S['signage_no']):.1f}%) lack formal "
                f"signage, confirming that the vast majority of parking along the corridors "
                f"operates without clear regulatory indication to drivers.")
    dx.set_text(dx.find(doc, "have visible parking markings"),
                f"Only {S['marking_yes']:,} of the {OC:,} on-street spaces "
                f"({pc(S['marking_yes']):.1f}%) have visible parking markings on the "
                f"pavement. The remaining {S['marking_no']:,} spaces "
                f"({pc(S['marking_no']):.1f}%) lack formal marking.")

    # --- per-corridor detail ---------------------------------------------
    for label, cor, key in (("1", C1, "Corridor 01"), ("2", C2, "Corridor 02")):
        total = cor["existing"] + cor["cross_street"] + cor["off_street"]
        dx.set_text(dx.find(doc, f"The Corridor {label} ({cor['km']} km) accounts for"),
                    f"Corridor {label} ({cor['km']} km) accounts for {cor['existing']:,} "
                    f"on-corridor on-street spaces, a further {cor['cross_street']:,} "
                    f"on-street spaces on cross-streets within the 100-metre influence "
                    f"area, and {cor['off_street']:,} off-street spaces in "
                    f"{cor['off_street_facilities']} facilities — {total:,} spaces in total "
                    f"within the survey area.")
        rows = [["Street", "On-Street Spaces", "Segments", "Parallel", "Perpendicular"]]
        for r in S["streets"][key]:
            rows.append([r["street"], f"{r['spaces']:,}", str(r["segments"]),
                         f"{r['parallel']:,}", f"{r['perpendicular']:,}"])
        rows.append(["Total", f"{cor['existing']:,}",
                     str(sum(r["segments"] for r in S["streets"][key])),
                     f"{sum(r['parallel'] for r in S['streets'][key]):,}",
                     f"{sum(r['perpendicular'] for r in S['streets'][key]):,}"])
        dx.rewrite_table(_street_table(doc, label), rows)

    # the old "illustrative, does not sum" caveat is no longer true
    dx.set_text(dx.find(doc, "The street-level tables in this section list"),
                "Note: the street-level tables in this section are complete — every "
                "on-corridor segment is attributed to a street, so each table sums exactly "
                "to that corridor's on-corridor total (2,349 and 3,746 spaces). A handful "
                "of segment names carrying obvious spelling variants in the survey data "
                "have been folded into the correct street.")

    # --- absorptive capacity ---------------------------------------------
    dx.set_text(dx.find(doc, "off-street spaces within the 100-metre influence area"),
                f"{S['off_street']:,} off-street spaces within the 100-metre influence area "
                f"of Corridors 1 and 2. This stock is overwhelmingly gated residential "
                f"courtyard rather than public parking: courtyards are "
                f"{S['off_street_yard_facilities']} of the {S['off_street_facilities']} "
                f"facilities ({S['off_street_yard_facilities_pct']:.0f}%) and "
                f"{S['off_street_yards']:,} of the {S['off_street']:,} spaces "
                f"({S['off_street_yards_pct']:.0f}%); the balance is {S['off_street_named_facilities']} "
                f"named commercial and institutional lots, which are individually about "
                f"twice the size of a courtyard",
                red=True)
    dx.set_text(dx.find(doc, "on-street spaces on cross-streets within the influence"),
                f"{S['cross_street']:,} on-street spaces on cross-streets within the "
                f"influence area, many of which are currently underutilised and could "
                f"accommodate additional demand through formal delineation (1,505 of these "
                f"spaces are still free to park and the city could turn them into Zone A/B "
                f"paid parking).")

    a = F["all"]
    dx.set_text(dx.find(doc, "Measured absorption (surveyed areas)"),
                f"Measured absorption (surveyed areas). Of the peak displaced demand, "
                f"surviving on-street capacity absorbs about "
                f"{a['absorbed_onstreet_pct']}% ({F['areas']['kentron']['absorbed_onstreet_pct']}% "
                f"in the Kentron core, {F['areas']['komitas']['absorbed_onstreet_pct']}% in "
                f"Komitas, up to {F['areas']['malatia']['absorbed_onstreet_pct']}% in "
                f"Malatia-Sebastia). The balance is closed by off-street capacity — but "
                f"{a['offstreet_dependency_pct']:.0f}% of the absorptive capacity counted "
                f"({a['absorb_offstreet']:,} of {a['absorb_capacity']:,} spaces) is "
                f"off-street rather than kerbside, and that off-street stock is "
                f"{S['off_street_yard_facilities_pct']:.0f}% gated residential courtyard by "
                f"facility count ({S['off_street_yards_pct']:.0f}% by capacity), counted at "
                f"gross capacity as if already open. The "
                f"conclusion that displaced demand can be re-absorbed (approaching 100% in "
                f"aggregate) is therefore conditional on those yards being opened and "
                f"actively managed; this dependency, and the measures to address it, are "
                f"carried in the companion Parking Analysis Report (Output 10).",
                keep_lead_bold=True)

    dx.set_text(dx.find(doc, "Measured off-street occupancy (field survey)"),
                f"Measured off-street occupancy (field survey). The off-street side of this "
                f"balance is now partly observed, not only inventoried. In each of the six "
                f"areas the survey recorded hourly occupancy in one representative "
                f"off-street facility ({Y['total_spaces']} surveyed spaces in total) using "
                f"the same licence-plate method as on-street. Averaged across the day these "
                f"accessible facilities run about {Y['weighted_avg_pct']}% full, so real "
                f"off-street headroom demonstrably exists. At the peak hour, however, three "
                f"of the six are already at or beyond their marked capacity (Palace "
                f"{Y['areas']['mega']['peak_pct']}%, Nalbandyan "
                f"{Y['areas']['kentron']['peak_pct']}%, Komitas City "
                f"{Y['areas']['komitas']['peak_pct']}%) and only three keep meaningful "
                f"spare (Garegin {Y['areas']['garegin']['peak_pct']}%, Shiraz "
                f"{Y['areas']['shiraz']['peak_pct']}%, Sebastia "
                f"{Y['areas']['malatia']['peak_pct']}%). These surveyed facilities are "
                f"accordingly excluded from the absorptive-capacity figure above — they "
                f"already carry their own demand — so the courtyard dependency refers to "
                f"the still-closed residential yards that could not be surveyed.",
                keep_lead_bold=True)

    dx.rewrite_table(
        dx.find_table(doc, "Surveyed off-street facility"),
        [["Area", "Surveyed off-street facility", "Formal spaces", "Avg. occupancy",
          "Peak-hour occupancy"]] +
        [[F["areas"][k]["label"], Y["areas"][k]["name"], f"{Y['areas'][k]['spaces']}",
          f"{Y['areas'][k]['avg_pct']}%", f"{Y['areas'][k]['peak_pct']}%"]
         for k in ("kentron", "komitas", "garegin", "mega", "malatia", "shiraz")] +
        [["All six (total / weighted avg.)", "—", f"{Y['total_spaces']}",
          f"{Y['weighted_avg_pct']}%", "—"]])
    return n


def _street_table(doc, label):
    """The Corridor N street table, located by its caption rather than its contents
    (the contents are what we are about to replace)."""
    caption = dx.find_styled(doc, f"Corridor {label}: Street-Level Detail", "Caption")
    el = caption._p.getnext()
    while el is not None and el.tag != qn("w:tbl"):
        el = el.getnext()
    if el is None:
        raise LookupError(f"no table after Corridor {label} caption")
    from docx.table import Table
    return Table(el, doc)


CAVEAT = (
    "Basis and status of these figures. The parking-impact figures in this chapter "
    "follow the v2 conceptual design and cover Corridors 1 and 2 only; Corridor 3 is "
    "withheld from the impact assessment because its conceptual design has not yet "
    "been prepared. Because the conceptual design is not final, the removal and "
    "retention figures — and the displacement figures that follow from them — will be "
    "updated when the design is signed off. They are the current best estimate, not a "
    "final count, and they supersede the figures given in the June draft, which were "
    "based on an earlier design revision and on all three corridors."
)


def drop_corridor_3(doc):
    """Corridor 3 has no conceptual design, so it is out of the impact frame. Its
    street-level section is removed and its inventory total preserved in the
    aggregate-supply note instead of being silently dropped."""
    # Anchored on the HEADING, not on the first text match: the List of Tables
    # repeats "Corridor 3: Street-Level Detail" near the top of the document, and
    # starting the range there would delete the whole front matter.
    first = dx.find_styled(doc, "Corridor 3: Street-Level Detail", "Heading 2")
    last = dx.find(doc, "Unlike Corridors 1 and 2, Corridor 3 contains no named")
    dx.drop_range(first, last)


def fix_impact_chapter(doc):
    """Reviewer comments 2 and 3 (median vs kerb-aligned; 'no room for parking'),
    plus the refreshed removal figures and the basis caveat."""
    dx.set_text(
        dx.find(doc, "The conceptual corridor designs adopt a central median alignment"),
        "The conceptual corridor designs reallocate the whole cross-section. Along much "
        "of the alignment the dedicated bus lanes run in the central median; along other "
        "sections they run kerbside. That distinction matters for where passengers board "
        "— an island platform in the carriageway rather than a stop on the footway — but "
        "it does not drive the parking impact. A kerb-aligned bus lane occupies the very "
        "kerbside space that parking occupies, and so removes as much on-street parking "
        "as a median-aligned one; in station areas it removes slightly more. The parking "
        "loss follows from reallocating the full right-of-way to bus lanes, general "
        "traffic, cycle lanes and adequate footways, not from the choice of alignment. "
        f"The cross-sections allocate carriageway width to dedicated bus lanes "
        f"(2 × 3.5 m), mixed-traffic lanes (2 × 3.0 m per direction), median platforms "
        f"and separators (0.5 m buffers), cycle lanes, and minimum sidewalk widths of "
        f"2.50 m on each side. Where the existing right-of-way is fully consumed by that "
        f"allocation no kerbside parking can be retained, and this is the case along most "
        f"of the alignment. Between stations, however, the cross-section is less "
        f"demanding, and in most such sections there is room for parking to remain. That "
        f"is why the design retains or re-establishes {S['retained']:,} spaces "
        f"({S['retained_pct']:.0f}% of the on-corridor supply) rather than removing all "
        f"of it: the removal figure is {S['removed_pct']:.0f}%, not 100%.")

    dx.set_text(
        dx.find(doc, "Based on the supply inventory and the initial corridor designs"),
        f"Setting the supply inventory against the v2 conceptual design, the bus priority "
        f"corridors remove {S['removed']:,} of the {OC:,} on-corridor on-street spaces "
        f"({S['removed_pct']:.0f}%) and retain or re-establish {S['retained']:,} "
        f"({S['retained_pct']:.0f}%). Corridor 1 loses {C1['removed']:,} of "
        f"{C1['existing']:,} spaces, retaining {C1['retained']}; Corridor 2 loses "
        f"{C2['removed']:,} of {C2['existing']:,}, retaining {C2['retained']}. The "
        f"retained spaces sit off the running way — in pockets, setbacks and bays "
        f"re-established between stations — rather than on the carriageway itself. The "
        f"breakdown by sensitivity zone is as follows:")

    anchor = dx.find(doc, "Setting the supply inventory against the v2 conceptual design")
    dx.insert_after(anchor, CAVEAT, bold_lead=True)

    # Table 9 — Komitas moves from medium to high on the measured behaviour
    hi_streets, hi_total = band_text("high")
    md_streets, md_total = band_text("medium", top=4)
    lo_streets, lo_total = band_text("lower", top=5)
    assert hi_total + md_total + lo_total == OC, (hi_total, md_total, lo_total)
    dx.rewrite_table(
        dx.find_table(doc, "Sensitivity", "Key Concern"),
        [["Sensitivity", "Corridor Segments", "On-Street Spaces", "Key Concern"],
         ["High", hi_streets, f"{hi_total:,}",
          "Zone A and Zone B pricing; limited side-street capacity; competing commercial "
          "demands. Field survey: Kentron 138% peak with only "
          f"{F['areas']['kentron']['absorbed_onstreet_pct']}% absorbable on-street; "
          f"Komitas {F['areas']['komitas']['peak_pct']}% peak with "
          f"{F['areas']['komitas']['absorbed_onstreet_pct']}% on-street absorption — "
          "Komitas is reclassified from medium to high on this evidence."],
         ["Medium", md_streets, f"{md_total:,}",
          "Mixed residential, commercial and arterial functions; some absorptive capacity "
          f"on parallel streets. Field survey: Garegin Nzhdeh "
          f"{F['areas']['garegin']['peak_pct']}% peak / "
          f"{F['areas']['garegin']['absorbed_onstreet_pct']}% absorption."],
         ["Lower", lo_streets, f"{lo_total:,}",
          "Predominantly free and unmarked; suburban; more flexible accommodation. Field "
          f"survey: Shiraz/Hasratyan {F['areas']['shiraz']['peak_pct']}% / "
          f"{F['areas']['shiraz']['absorbed_onstreet_pct']}%, Malatia-Sebastia "
          f"{F['areas']['malatia']['peak_pct']}% / "
          f"{F['areas']['malatia']['absorbed_onstreet_pct']}% — confirmed lower."]])


def fix_displacement(doc):
    """Reviewer comment 4 — what the ratio actually means."""
    a = F["all"]
    dx.set_text(
        dx.find(doc, "Locally measured. Across the surveyed areas"),
        f"Locally measured. Across the surveyed areas, peak displaced demand was "
        f"{a['displaced']:,} vehicles against {a['removed']:,} spaces removed — "
        f"{a['displaced_pct']:.0f}%. That percentage is the measured displaced demand set "
        f"against the supply removed in the same six areas, and it is worth stating "
        f"precisely what each side of it is. Displaced demand is the number of distinct "
        f"vehicles observed parking in the zones the conceptual design removes, counted at "
        f"each area's own busiest hour and summed across the six areas "
        f"({a['displaced']:,} vehicles). The denominator is the formal capacity removed in "
        f"those same zones ({a['removed']:,} spaces). The ratio is below 100% because the "
        f"kerb is not full everywhere at the same time: fewer vehicles actually need "
        f"re-homing than there are spaces being taken away. It is a demand overlay on six "
        f"representative areas rather than a corridor-wide re-survey, and it should not be "
        f"read as meaning that "
        f"{100 - a['displaced_pct']:.0f}% of the removed supply was unused — only that at "
        f"no single hour were all of those spaces occupied at once. The principle that "
        f"displaced demand falls well below the supply removed is therefore now measured "
        f"in Yerevan, not merely inferred from European precedent.", keep_lead_bold=True)


OVER_100 = (
    "How occupancy is measured, and what a figure above 100% means. Occupancy in this "
    "report is the number of distinct vehicles recorded using a length of kerb during an "
    "hour, divided by the number of spaces on it. It is an hour-long count rather than an "
    "instantaneous snapshot, so a reading above 100% does not mean the kerb was physically "
    "overfull at any one moment: it means more distinct vehicles used that kerb within the "
    "hour than there are spaces, because the spaces turned over. Two further effects lift "
    "on-street readings above 100%. Vehicles parked outside the marked bays are counted "
    f"against the marked capacity — {V['all']['shares']['location']['footpath']:.1f}% of "
    f"observed vehicles stood on footpaths and "
    f"{V['all']['shares']['location']['setback']:.1f}% in setbacks — and where no bays are "
    "marked at all (86% of the corridor kerb) the denominator is an estimate of capacity, "
    "one space per 7.5 metres of parallel kerb, rather than a count of stripes. Off-street "
    "the same turnover effect applies, with stacking on top of it: vehicles stand in aisles "
    "and against walls in facilities whose capacity is estimated from area at 30 m² per "
    f"space. That is how the Palace lot reaches {Y['areas']['mega']['peak_pct']}% and the "
    f"Nalbandyan yard {Y['areas']['kentron']['peak_pct']}% at their peak hour. A figure "
    "above 100% is therefore a reliable signal of saturation and of parking spilling beyond "
    "the marked supply — it is not a data error, and it is not a measure of illegal parking, "
    f"which was separately recorded and is only {V['all']['shares']['legal']['illegal']:.1f}% "
    "of observations."
)


# ---------------------------------------------------------------------------
# the new occupancy chapter (reviewer comment 6)
# ---------------------------------------------------------------------------
def _after_table(doc, table):
    """A fresh empty paragraph immediately after `table`, returned as the next anchor.

    It must be a NEW paragraph, not the document's existing next one: returning the
    existing one hands the chain a paragraph that already belongs to the following
    chapter, and every subsequent insert then lands after that chapter's heading.
    """
    p = doc.add_paragraph()
    p.style = doc.styles["Normal"]
    table._tbl.addnext(p._p)
    return p


def occupancy_chapter(doc):
    """Replace the single-paragraph "Occupancy and Demand" chapter with a full one:
    methodology, locations, and results broken down by typology.

    The reviewer's complaint was that Output 10 points here for the occupancy detail
    and there is none: "no explanation of the occupancy survey methodology, the
    locations where they were conducted, and only highly aggregated results are
    shown, not broken down by typology as discussed."
    """
    head = dx.find(doc, "Occupancy and Demand: Field Survey Results")
    dx.set_text(head, "Field Occupancy Survey: Methodology, Locations and Results")
    body = dx.find(doc, "The demand-side analysis has been completed through the targeted")
    a, sh = F["all"], V["all"]["shares"]

    dx.set_text(body,
        "The demand-side evidence in this report comes from a targeted field occupancy "
        "survey carried out after the desk-based supply inventory. This chapter documents "
        "how it was designed, where it was conducted and what it measured, and then "
        "presents the results broken down by area and by parking typology. The aggregate "
        "headlines are that capacity-weighted peak occupancy across the surveyed areas "
        f"reaches {a['peak_pct']}%, that {a['over85_pct']}% of surveyed zones exceed the 85% "
        f"efficiency threshold at their peak hour, and that the kerb is short-stay and "
        f"high-turnover. Those aggregates conceal a range from "
        f"{F['areas']['malatia']['peak_pct']}% to {F['areas']['kentron']['peak_pct']}%, "
        f"however, and it is the range rather than the average that determines what "
        f"mitigation each part of the corridor needs.")

    cur = dx.insert_block(body, [
        ("Heading 2", "Survey Design and Instrument"),
        ("Normal",
         "The survey was a rolling licence-plate census rather than a spot count. "
         "Enumerators walked a fixed circuit of numbered survey zones once an hour from "
         "07:00 to 24:00, recording every parked vehicle on each pass. Recording the plate "
         "rather than only a headcount is what makes duration, turnover and displacement "
         "measurable: a plate seen in consecutive hours is one vehicle staying, whereas the "
         "same space occupied by successive plates is turnover, and a headcount cannot tell "
         "the two apart."),
        ("Normal",
         "For every parked vehicle the enumerator recorded seven fields: the hour of "
         "observation; the survey zone; the licence plate; the vehicle type (sedan, truck "
         "or motorcycle); where the vehicle stood relative to the carriageway (on the "
         "carriageway, on the footpath, or in a setback); how it was parked (parallel, 45 "
         "degrees, or perpendicular); and whether the parking was legal or illegal. The "
         "last three fields are what allow the results to be broken down by typology rather "
         "than reported only in aggregate, and they are what reveal where observed "
         "behaviour departs from the marked supply."),
        ("Normal",
         f"Occupancy is measured against the formal (striped) capacity already recorded in "
         f"the supply inventory, so the demand and supply sides share a single denominator. "
         f"Where a segment has no marked bays, capacity is the inventory estimate of one "
         f"space per 7.5 metres of parallel kerb. A parking event, the unit behind turnover, "
         f"is one continuous run of hours in which a plate is present; a gap of more than "
         f"one hour is treated as the space having been vacated and re-used. In total the "
         f"survey produced {V['all']['sightings']:,} on-street vehicle sightings covering "
         f"{V['all']['distinct_plates']:,} distinct vehicles across {a['surveyed_zones']} "
         f"survey zones, plus one off-street facility in each of the six areas."),
        ("Normal", "**" + OVER_100),
        ("Normal",
         "Two limits of the instrument should be stated at the outset. The window closes at "
         "midnight, so true overnight-residential demand is under-counted and the "
         "residential long-stay tail visible in the data is a lower bound. And payment "
         "compliance cannot be observed by an enumerator on foot, because whether a session "
         "was paid for is held only in the Parking City Service back-office. These are the "
         "two dimensions for which the municipal ANPR record, if released, would still add "
         "value."),
    ])

    cur = dx.insert_block(cur, [
        ("Heading 2", "Where and When the Surveys Were Conducted"),
        ("Normal",
         "Six areas were surveyed rather than the full 34 km of corridor. They were chosen "
         "to span the corridors' sensitivity range: a dense commercial core under paid "
         "regulation (Kentron), the city's largest Zone B concentration (Komitas Avenue), a "
         "retail-anchored destination (Gai Avenue at Mega Mall), a mixed residential and "
         "commercial arterial (Garegin Nzhdeh), and two outer residential areas "
         "(Shiraz/Hasratyan and Malatia-Sebastia). Between them they cover the full range "
         "of regulatory status, land use and kerb pressure found along the corridors, which "
         "is what the displacement assessment requires."),
        ("Normal",
         "The areas were surveyed on four separate ordinary mid-week working days between "
         "29 May and 3 June 2026, with no weekend or public holiday. Spreading them across "
         "days rather than surveying simultaneously was deliberate: a one-off disruption on "
         "any single day would show up as a localised outlier against the other areas, "
         "whereas a behavioural pattern that repeats across four separate days in six "
         "separate places is a pattern. The table below sets out the survey footprint."),
    ])

    cap = dx.insert_after(cur, "Table X - Field occupancy survey: areas, dates and footprint",
                          style="Caption")
    corridor_of = {"kentron": "1", "komitas": "2", "mega": "2", "garegin": "1",
                   "shiraz": "2", "malatia": "2"}
    rows = [["Area", "Survey date", "Day", "Zone codes", "Survey paths", "Formal spaces",
             "Corridor"]]
    for key, label, date, weekday in rf.SURVEY_AREAS:
        v = F["areas"][key]
        rows.append([label, date, weekday, v["zones"], str(v["paths"]),
                     f"{v['spaces']:,}", corridor_of[key]])
    rows.append(["All six areas", "29 May to 3 June 2026", "4 working days", "-",
                 str(sum(F["areas"][k]["paths"] for k in F["areas"])),
                 f"{sum(F['areas'][k]['spaces'] for k in F['areas']):,}", "1 and 2"])
    tbl = dx.add_table_after(doc, cap, rows,
                             widths=[1.35, 0.95, 0.72, 0.72, 0.62, 0.72, 0.55])
    cur = _after_table(doc, tbl)

    cur = dx.insert_block(cur, [
        ("Heading 2", "Occupancy Results by Area"),
        ("Normal",
         f"Capacity-weighted peak occupancy across all six areas is {a['peak_pct']}%, "
         f"{a['over85_pct']}% of the {a['surveyed_zones']} surveyed zones exceed the 85% "
         f"efficiency threshold at their peak hour, and {a['over_capacity']} zones are over "
         f"capacity outright. The aggregate is not the operative number, because the six "
         f"areas differ by a factor of nearly three. Kentron runs at "
         f"{F['areas']['kentron']['peak_pct']}% and Malatia-Sebastia at "
         f"{F['areas']['malatia']['peak_pct']}%: the first has no slack at all, the second "
         f"has a great deal. Three of the six areas, Kentron, Komitas and Gai Avenue, are "
         f"over capacity at the peak hour, and those are precisely the areas where displaced "
         f"demand cannot simply move to the next street."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig10_peak_occupancy_by_area.png"),
                               caption="Figure X - Peak-hour occupancy by surveyed area")

    cap = dx.insert_after(cur, "Table X - Occupancy, stay and turnover by surveyed area",
                          style="Caption")
    rows = [["Area", "Peak occupancy", "Zones over 85%", "Zones over capacity",
             "Average stay", "Turnover per space/day"]]
    for key, label, *_ in rf.SURVEY_AREAS:
        v = F["areas"][key]
        rows.append([label, f"{v['peak_pct']}%", f"{v['over85_pct']}%",
                     str(v["over_capacity"]), f"{v['avg_stay_h']} h", f"{v['turnover']}"])
    rows.append(["All six areas", f"{a['peak_pct']}%", f"{a['over85_pct']}%",
                 str(a["over_capacity"]), f"{a['avg_stay_h']} h",
                 f"{a['turnover_lo']} to {a['turnover_hi']}"])
    tbl = dx.add_table_after(doc, cap, rows, widths=[1.5, 0.9, 0.9, 0.95, 0.75, 1.05])
    cur = _after_table(doc, tbl)

    cur = dx.insert_block(cur, [
        ("Normal",
         "The demand profile through the day explains why a single peak figure is adequate "
         "for the displacement assessment. Occupancy rises steeply from 07:00, plateaus "
         "across the working day, and holds late: the evening does not empty the kerb, "
         "because the residential and commercial peaks overlap rather than alternate. There "
         "is no quiet hour into which displaced demand could be shifted by timing measures "
         "alone."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig11_hourly_demand_profile.png"),
                               caption="Figure X - Vehicles present by clock hour, all six "
                                       "areas combined")

    cur = dx.insert_block(cur, [
        ("Heading 2", "Results by Parking Typology"),
        ("Normal",
         "The survey recorded how each vehicle was parked as well as that it was parked, "
         "which allows the results to be broken down by typology. Three breakdowns matter "
         "for the corridor design: how vehicles are arranged, where they stand relative to "
         "the carriageway, and what kind of vehicle they are."),
        ("Normal",
         f"**Configuration: the marked supply understates angled parking. The inventory "
         f"records the corridor kerb as {pc(M['parallel']):.1f}% parallel and "
         f"{pc(M['90']):.1f}% perpendicular, with no 45-degree parking marked anywhere "
         f"along either corridor. The survey found {sh['method']['parallel']:.0f}% of "
         f"vehicles parked parallel, {sh['method']['angled45']:.0f}% at 45 degrees and "
         f"{sh['method']['perpendicular']:.0f}% perpendicular. More than a quarter of "
         f"observed parking therefore uses a layout that does not exist in the marked "
         f"supply at all. That is a finding rather than a discrepancy: where bays are "
         f"unmarked, drivers self-organise into whichever angle fits the most cars, which "
         f"is why delineating the existing free parking recovers usable capacity without "
         f"adding any."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig14_configuration_observed.png"),
                               caption="Figure X - Parking configuration: as marked against "
                                       "as actually parked")

    off = 100 - sh["location"]["carriageway"]
    cur = dx.insert_block(cur, [
        ("Normal",
         f"**Kerb location: a fifth of parking is not on the carriageway. Across the six "
         f"areas {off:.0f}% of observed vehicles stood off the carriageway, "
         f"{sh['location']['footpath']:.1f}% on footpaths and "
         f"{sh['location']['setback']:.1f}% in setbacks. This is informal encroachment the "
         f"supply inventory does not capture, and it varies sharply by area: it reaches "
         f"30.9% in Malatia-Sebastia and 30.4% in Garegin Nzhdeh, where footway parking is "
         f"routine, and falls to 10.0% in Kentron, where the kerb is too tightly built to "
         f"allow it. Footway parking is the component with a direct pedestrian and "
         f"accessibility cost, and it is concentrated in the outer areas rather than in the "
         f"centre. It is also distinct from illegality: only {sh['legal']['illegal']:.1f}% "
         f"of observations were recorded as illegal, so footway parking in these areas is "
         f"tolerated rather than enforced against."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig15_kerb_location_by_area.png"),
                               caption="Figure X - Where vehicles actually stood, by area")

    cur = dx.insert_block(cur, [
        ("Normal",
         f"**Vehicle type: freight is concentrated in pockets. Sedans account for "
         f"{sh['vehicle']['sedan']:.1f}% of observed vehicles and motorcycles for "
         f"{sh['vehicle']['motorcycle']:.1f}%. Trucks are {V['all']['truck_pct']}% of all "
         f"classified vehicles across the six areas, but the distribution is what matters: "
         f"the truck share reaches {V['areas']['malatia']['truck_pct']}% in "
         f"Malatia-Sebastia ({V['areas']['malatia']['trucks']:,} of "
         f"{V['areas']['malatia']['classified']:,} vehicles) and "
         f"{V['areas']['shiraz']['truck_pct']}% in Shiraz/Hasratyan, against "
         f"{V['areas']['kentron']['truck_pct']}% in Kentron. Loading provision should "
         f"therefore be sized to those measured pockets rather than distributed uniformly "
         f"along the corridors."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig17_truck_share_by_area.png"),
                               caption="Figure X - Freight presence by area")

    cur = dx.insert_block(cur, [
        ("Heading 2", "Duration of Stay and Turnover"),
        ("Normal",
         f"The corridor kerb is dominated by short visits. About {a['stay']['shortPct']}% of "
         f"stays are one hour or less and "
         f"{a['stay']['shortPct'] + a['stay']['errandPct']}% are two hours or less, while "
         f"genuine all-day storage of eight hours or more is about "
         f"{a['stay']['alldayPct']}% and the intermediate worker-length stay of two to eight "
         f"hours about {a['stay']['workerPct']}%. The average stay is {a['avg_stay_h']} "
         f"hours. This distribution is stable across all six areas, which is the strongest "
         f"single behavioural finding of the survey: the kerb serves visitors and errands, "
         f"not commuters."),
        ("Normal",
         "It matters for mitigation because it inverts the intuitive policy response. A kerb "
         "dominated by all-day commuter storage is fixed with maximum-stay limits; a kerb "
         "that already turns over every hour is not, and imposing visitor caps on it would "
         "regulate the very behaviour the policy wants. Pricing, delineation and off-street "
         "supply are the levers that bind here. The long-stay tail that does exist is "
         "largely residential and overnight, and the daytime window under-counts it."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig12_duration_of_stay.png"),
                               caption="Figure X - Duration of stay by area")

    cur = dx.insert_block(cur, [
        ("Normal",
         f"Turnover follows directly from the duration mix. Measured as parking events per "
         f"marked space per day across all bay types, it runs from "
         f"{F['areas']['malatia']['turnover']} in Malatia-Sebastia to "
         f"{F['areas']['kentron']['turnover']} in Kentron, where the busiest kerb recycles "
         f"each space between seven and eight times a day. The gradient tracks land use "
         f"rather than regulation: the commercial core and the retail destination turn over "
         f"fastest, the outer residential areas slowest, and the paid Zone B on Komitas sits "
         f"between them at {F['areas']['komitas']['turnover']}."),
        ("Normal",
         f"**A note on the basis, because an earlier figure circulated. Turnover here is "
         f"measured across all bay types — road-edge kerb, pockets and setbacks together — "
         f"so every area rests on at least {min(v['spaces'] for v in F['areas'].values())} "
         f"marked spaces. An earlier draft quoted a range of "
         f"{a['turnover_road_edge_lo']} to {a['turnover_road_edge_hi']} per space per day, "
         f"measured on the road-edge kerb alone. That calculation is arithmetically correct "
         f"and is reproduced in the underlying data, but its two highest values are not "
         f"reliable: Gai Avenue has only {F['areas']['mega']['road_edge_spaces']} road-edge "
         f"spaces and Malatia-Sebastia only {F['areas']['malatia']['road_edge_spaces']}, "
         f"essentially all of their parking being in pockets and setbacks, so those ratios "
         f"rest on denominators too small to carry a figure. On the four areas that do have "
         f"a substantial road-edge kerb the two bases sit close together — Komitas "
         f"{F['areas']['komitas']['turnover_road_edge']} against "
         f"{F['areas']['komitas']['turnover']}, Garegin Nzhdeh "
         f"{F['areas']['garegin']['turnover_road_edge']} against "
         f"{F['areas']['garegin']['turnover']}, Shiraz/Hasratyan "
         f"{F['areas']['shiraz']['turnover_road_edge']} against "
         f"{F['areas']['shiraz']['turnover']}, with Kentron the widest at "
         f"{F['areas']['kentron']['turnover_road_edge']} against "
         f"{F['areas']['kentron']['turnover']}. The all-bay-type range is used throughout "
         f"this report."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig13_turnover_by_area.png"),
                               caption="Figure X - Turnover by area")

    cur = dx.insert_block(cur, [
        ("Heading 2", "Measured Displacement by Area"),
        ("Normal",
         f"Because the survey recorded which zones the conceptual design removes, "
         f"displacement can be measured rather than assumed. Across the six areas the "
         f"design removes {a['removed']:,} spaces, in which {a['displaced']:,} distinct "
         f"vehicles were observed at the areas' respective peak hours, or "
         f"{a['displaced_pct']:.0f}% of the supply removed. The per-area picture is far more "
         f"uneven than that aggregate, and the unevenness is the finding: displaced demand "
         f"runs from {F['areas']['malatia']['displaced_pct']:.0f}% of removed supply in "
         f"Malatia-Sebastia to {F['areas']['mega']['displaced_pct']:.0f}% at Gai Avenue, and "
         f"the share that surviving nearby on-street capacity can re-absorb runs from "
         f"{F['areas']['komitas']['absorbed_onstreet_pct']}% in Komitas to "
         f"{F['areas']['malatia']['absorbed_onstreet_pct']}% in Malatia-Sebastia."),
        ("Normal",
         "The two dimensions do not move together, and that is what drives the sensitivity "
         "banding. Kentron and Komitas combine high displaced demand with almost no "
         "on-street capacity to receive it, so their mitigation has to be off-street. "
         "Shiraz/Hasratyan and Malatia-Sebastia combine modest displacement with ample "
         "nearby kerb, so delineation and organisation suffice. Gai Avenue is the outlier: "
         "displaced demand is essentially the whole removed supply, and even filling every "
         "nearby facility leaves a residual, which is why its kerb parking is left in place "
         "for now and revisited as the area develops."),
    ])
    cur = dx.add_picture_after(cur, os.path.join(FIGS, "fig16_displacement_by_area.png"),
                               caption="Figure X - Measured displacement by area")

    cap = dx.insert_after(cur, "Table X - Measured displacement and absorption by area",
                          style="Caption")
    rows = [["Area", "Spaces removed", "Displaced at peak", "Displaced as % of removed",
             "Nearby on-street", "Absorbed on-street", "Nearby off-street"]]
    for key, label, *_ in rf.SURVEY_AREAS:
        v = F["areas"][key]
        rows.append([label, f"{v['removed']:,}", f"{v['displaced']:,}",
                     f"{v['displaced_pct']:.0f}%", f"{v['absorb_onstreet']:,}",
                     f"{v['absorbed_onstreet_pct']}%", f"{v['absorb_offstreet']:,}"])
    rows.append(["All six areas", f"{a['removed']:,}", f"{a['displaced']:,}",
                 f"{a['displaced_pct']:.0f}%", f"{a['absorb_onstreet']:,}",
                 f"{a['absorbed_onstreet_pct']}%", f"{a['absorb_offstreet']:,}"])
    tbl = dx.add_table_after(doc, cap, rows,
                             widths=[1.3, 0.8, 0.8, 0.95, 0.8, 0.85, 0.85])
    cur = _after_table(doc, tbl)

    dx.insert_block(cur, [
        ("Heading 2", "What the Survey Cannot Observe"),
        ("Normal",
         "Three limits bound what the results above can carry. The survey window runs to "
         "midnight, so true overnight-residential demand is under-counted and the "
         "residential long-stay share should be read as a lower bound; this matters most in "
         "Malatia-Sebastia, whose daytime pressure is the lowest of the six but whose "
         "long-stay signature is the strongest. Payment compliance was not observable, so "
         "the survey cannot say what share of vehicles in Zone A and Zone B had paid; that "
         "would require the Parking City Service back-office record. And six areas are not "
         "the whole corridor: the displacement figures are a demand overlay on "
         "representative areas rather than a corridor-wide census, and they are stated as "
         "such wherever they appear."),
        ("Normal",
         f"One further check is worth recording because it returned a negative result. The "
         f"plate log allows long-term stationary vehicles to be identified, since a plate "
         f"present in every hourly sweep of the window has not moved all day, which is the "
         f"cheapest observable proxy for a stored or abandoned vehicle. Across all six areas "
         f"only {V['all']['stationary_all_window']} vehicles of the "
         f"{V['all']['distinct_plates']:,} observed met that test. On this evidence "
         f"long-term vehicle storage and abandonment are not a material component of "
         f"corridor kerb demand, and the kerb pressure documented in this chapter is genuine "
         f"in-use demand."),
    ])


# ---------------------------------------------------------------------------
# figures, executive summary and conclusions
# ---------------------------------------------------------------------------
# The June draft's eight figures were app screenshots whose stat panels had gone
# stale (Figure 1 read 15,255 free spaces, Figure 7 read 7,479 off-street). Each is
# replaced by the corresponding chart rendered from report_figures.py, matched by
# caption so the swap cannot silently land on the wrong picture.
FIGURE_SWAPS = [
    ("Aggregate Supply Summary", "fig01_aggregate_supply.png",
     "Aggregate parking supply, Corridors 1 and 2 with their 100 m influence area"),
    ("On-Street Parking by Regulatory Zone", "fig02_regulatory_zone.png",
     "On-corridor on-street supply by regulatory zone"),
    ("On-Street Parking by Configuration", "fig03_configuration.png",
     "On-corridor on-street supply by marked configuration"),
    ("On-Street Parking by Location", "fig04_location.png",
     "On-corridor on-street supply by physical location"),
    ("Parking Signage", "fig05_signage.png", "Parking signage coverage"),
    ("Marking", "fig06_marking.png", "Pavement marking coverage"),
    ("Available Absorptive Capacity (Off-street)", "fig07_absorptive_offstreet.png",
     "Available absorptive capacity (off-street)"),
    ("Available Absorptive Capacity (On-street)", "fig08_absorptive_onstreet.png",
     "Available absorptive capacity (on-street)"),
]


def swap_figures(doc):
    """Replace each stale screenshot with its regenerated chart. The picture sits in
    the paragraph BEFORE its caption in this document, so the caption is the anchor
    and the picture is found by walking back from it."""
    from docx.text.paragraph import Paragraph
    done = 0
    for caption_text, png, new_caption in FIGURE_SWAPS:
        # Must be a FIGURE caption. Several tables share their figure's title, and the
        # table caption comes first in document order ("Table 4 - On-Street Parking by
        # Configuration" precedes "Figure 3 - ..."), so matching on the title alone
        # rewrote the table's caption and swapped the preceding figure's image.
        cap = None
        for p in doc.paragraphs:
            if (p.style.name == "Caption" and caption_text in p.text
                    and p.text.strip().startswith("Figure")):
                cap = p
                break
        if cap is None:
            raise LookupError(f"figure caption not found: {caption_text}")
        pic = None
        el = cap._p.getprevious()
        while el is not None:
            if el.tag == qn("w:p") and "graphic" in el.xml:
                pic = Paragraph(el, doc)
                break
            el = el.getprevious()
        if pic is None:
            raise LookupError(f"no picture before caption: {caption_text}")
        dx.replace_image(doc, pic, os.path.join(FIGS, png))
        dx.set_picture_width(pic, 6.1)
        # keep the "Figure N" prefix; renumber_captions fixes the number later
        prefix = cap.text.split(" - ")[0] if " - " in cap.text else "Figure"
        dx.set_text(cap, f"{prefix} - {new_caption}")
        done += 1
    return done


def add_impact_figure(doc):
    """A new figure for the removal/retention split, placed in the impact chapter.
    The June draft asserted the removal figure without showing it."""
    anchor = dx.find(doc, "Basis and status of these figures")
    dx.add_picture_after(anchor, os.path.join(FIGS, "fig09_impact_by_corridor.png"),
                         caption="Figure X - Parking removed and retained by corridor")


def fix_summary_and_conclusions(doc):
    a = F["all"]
    dx.set_text(
        dx.find(doc, "A targeted field occupancy survey has since been completed"),
        f"A targeted field occupancy survey has since been completed on six representative "
        f"areas spanning the corridors' sensitivity range, surveyed on ordinary mid-week "
        f"working days (29 May to 3 June 2026). It supplies the demand-side evidence "
        f"previously unavailable. Across the surveyed areas, capacity-weighted peak "
        f"occupancy reaches {a['peak_pct']}%, with {a['over85_pct']}% of zones exceeding the "
        f"85% efficiency threshold at the peak hour; parking is overwhelmingly short-stay "
        f"(about {a['stay']['shortPct']}% of vehicles stay one hour or less, "
        f"{a['stay']['shortPct'] + a['stay']['errandPct']}% two hours or less) with turnover "
        f"of {a['turnover_lo']} to {a['turnover_hi']} vehicles per marked space per day on the "
        f"road-edge kerb; and peak "
        f"displaced demand equals only {a['displaced_pct']:.0f}% of the spaces removed "
        f"({a['displaced']:,} vehicles against {a['removed']:,} spaces in the surveyed "
        f"areas), confirming with local measurement the international finding that displaced "
        f"demand is materially lower than the supply removed. Occupancy readings above 100% "
        f"are explained where they first appear: they mean more distinct vehicles used a "
        f"kerb within the hour than it has marked spaces, not that the kerb was physically "
        f"overfull at any one instant.")

    dx.insert_after(
        dx.find(doc, "A targeted field occupancy survey has since been completed"),
        "Basis of the impact figures. The parking-removal, retention and displacement "
        "figures in this report follow the v2 conceptual design and cover Corridors 1 and 2; "
        "Corridor 3 is withheld pending its conceptual design. They supersede the June "
        "draft's figures and will be updated again when the conceptual design is final.",
        bold_lead=True)

    # --- conclusions ------------------------------------------------------
    dx.set_text(
        dx.find(doc, "The parking supply inventory for the Yerevan bus priority corridor"),
        f"The parking supply inventory for the Yerevan bus priority corridor project "
        f"provides a comprehensive, georeferenced evidence base covering {S['total']:,} "
        f"parking spaces across {S['features']:,} surveyed features on Corridors 1 and 2 and "
        f"their 100-metre influence areas. The key conclusions are:")

    dx.set_text(
        dx.find(doc, "The survey documented 8,862 on-street parking spaces"),
        f"The survey documented {S['on_street']:,} on-street parking spaces across "
        f"{S['on_street_segments']} segments and {S['off_street']:,} off-street spaces "
        f"across {S['off_street_facilities']} facilities within Corridors 1 and 2 and their "
        f"100-metre influence areas.")

    paid = Z["zone_a"] + Z["zone_b"]
    dx.set_text(
        dx.find(doc, "are within the paid parking system (260 in Zone A"),
        f"Only {paid} of the {OC:,} on-corridor on-street spaces ({pc(paid):.1f}%) are "
        f"within the paid parking system ({Z['zone_a']} in Zone A, {Z['zone_b']} in Zone B). "
        f"The remaining {100 - pc(paid):.1f}% are free or unregulated, confirming the "
        f"informal nature of most corridor parking. Only {pc(S['signage_yes']):.0f}% of the "
        f"on-corridor kerb carries signage and {pc(S['marking_yes']):.0f}% carries marking.")

    dx.set_text(
        dx.find(doc, "The conceptual corridor designs will require the removal of 5,953"),
        f"The conceptual corridor designs remove {S['removed']:,} of the {OC:,} on-corridor "
        f"on-street spaces ({S['removed_pct']:.0f}%), {C1['removed']:,} on Corridor 1 and "
        f"{C2['removed']:,} on Corridor 2, and retain or re-establish {S['retained']:,} "
        f"({S['retained_pct']:.0f}%). The loss follows from reallocating the full "
        f"cross-section to bus lanes, general traffic, cycle lanes and adequate footways, "
        f"not from the median alignment as such: kerb-aligned sections remove as much "
        f"kerbside parking as median-aligned ones. These figures follow the v2 conceptual "
        f"design and will be updated when the design is final.")

    dx.set_text(
        dx.find(doc, "Available absorptive capacity includes 7,035 off-street spaces"),
        f"Available absorptive capacity includes {S['off_street']:,} off-street spaces and "
        f"{S['cross_street']:,} cross-street on-street spaces, of which 1,505 are currently "
        f"free to park and could be brought into the Zone A/B paid system.")

    dx.set_text(
        dx.find(doc, "A targeted field occupancy survey on six representative areas"),
        f"A targeted field occupancy survey on six representative areas (surveyed on "
        f"ordinary working days) measured the demand side: capacity-weighted peak occupancy "
        f"of {a['peak_pct']}%, with {a['over85_pct']}% of zones over the 85% threshold; a "
        f"short-stay, high-turnover kerb (about {a['stay']['shortPct']}% of stays one hour "
        f"or less; turnover {a['turnover_lo']} to {a['turnover_hi']} per marked space per "
        f"day across all bay types); "
        f"observed parking that departs from the marked supply "
        f"({V['all']['shares']['method']['angled45']:.0f}% of vehicles park at 45 degrees "
        f"where no 45-degree bay is marked, and "
        f"{100 - V['all']['shares']['location']['carriageway']:.0f}% park off the "
        f"carriageway); and peak displaced demand equal to only {a['displaced_pct']:.0f}% of "
        f"spaces removed ({a['displaced']:,} against {a['removed']:,} in the surveyed "
        f"areas). The methodology, the locations and the per-typology results are set out in "
        f"full in the field occupancy survey chapter.")

    dx.set_text(
        dx.find(doc, "Aggregate re-absorption approaching 100% is achievable"),
        f"Aggregate re-absorption approaching 100% is achievable but conditional on opening "
        f"the gated residential courtyards. Off-street capacity supplies "
        f"{a['offstreet_dependency_pct']:.0f}% of the absorptive capacity counted "
        f"({a['absorb_offstreet']:,} of {a['absorb_capacity']:,} spaces), counted at gross "
        f"capacity as if already open, and that off-street stock is "
        f"{S['off_street_yard_facilities_pct']:.0f}% courtyard by facility count and "
        f"{S['off_street_yards_pct']:.0f}% by capacity.")


# ---------------------------------------------------------------------------
def renumber_captions(doc):
    """Renumber every Figure/Table caption in document order.

    Necessary because Corridor 3's table is gone and the new chapter adds captions
    written as "Figure X" / "Table X". The Lists of Figures and Tables are real TOC
    fields keyed on the Caption style, so once the captions are right the lists
    rebuild themselves on field update.
    """
    counters = {"Figure": 0, "Table": 0}
    for p in doc.paragraphs:
        if p.style.name != "Caption":
            continue
        for kind in ("Figure", "Table"):
            if p.text.strip().startswith(kind):
                counters[kind] += 1
                # Strip whatever separator the existing caption used. These files mix
                # "Figure 1 - Title", "Figure 4, Title" and "Figure 10. Title", so a
                # naive split on " - " leaves the old number embedded.
                rest = re.sub(rf"^{kind}\s*[A-Za-z0-9]*\s*[-–—.,:]?\s*", "",
                              p.text.strip())
                # Rebuilt WITH its SEQ field: the Lists of Figures and Tables collect
                # only paragraphs that carry one, so plain text would empty them.
                dx.set_caption(p, kind, rest, number=counters[kind])
                break
    return counters


def force_field_update(doc):
    """Ask Word to refresh fields on open, so the Lists of Figures and Tables and the
    page references rebuild without the client having to press F9."""
    settings = doc.settings.element
    for existing in settings.findall(qn("w:updateFields")):
        settings.remove(existing)
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


def main():
    shutil.copyfile(SRC, DST)
    doc = Document(DST)

    refresh_numbers(doc)
    drop_corridor_3(doc)
    fix_impact_chapter(doc)
    fix_displacement(doc)
    occupancy_chapter(doc)
    swap_figures(doc)
    add_impact_figure(doc)
    fix_summary_and_conclusions(doc)
    counters = renumber_captions(doc)
    force_field_update(doc)

    doc.save(DST)
    print("WROTE:", DST)
    print(f"       {counters['Figure']} figures, {counters['Table']} tables")

    also = os.path.join(rf.ROOT, "Field Surveys/Field Surveys Report",
                        os.path.basename(DST))
    shutil.copyfile(DST, also)
    print("COPIED:", also)


if __name__ == "__main__":
    main()
