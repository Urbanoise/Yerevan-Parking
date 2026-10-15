# -*- coding: utf-8 -*-
"""Output 8, October 2026 round: the ADB memo of 7 Oct 2026 on the 30 Sep versions.

Builds a new dated copy from the 30 Sep response copy (SEP'26, left untouched as the
record) and applies this round's changes in red:

  * occupancy on the reviewer's basis: a vehicle counts half an hour in the hours it
    arrives and leaves and a full hour between (compute_field_survey_metrics.mjs,
    'walter'); every occupancy, stay, hourly and displacement figure moves with it,
    and the "a zone can read above 100%" explanation is rewritten;
  * Bagratunyats N03-N06 retained (32 spaces): 1,220 -> 1,252 retained, 4,875 -> 4,843
    removed; Corridor 1 869 -> 901;
  * a full Executive Summary;
  * Gai Avenue: "(Mega Mall)" dropped from the area labels, Figure 16 relabelled as an
    all-day average;
  * figures re-rendered (charts) and re-captured from the app (maps).

The September round's red is turned black and its closed comment threads removed, so
red marks only this round. Every number is read from report_figures.
Usage: python apply_o8_oct_edits.py [--force]
"""
import os
import sys

from docx import Document

import docx_edit as dx
import gen_o8_figures_24082026 as g24
import gen_o8_report_figures as g
import report_figures as rf

ROOT = rf.ROOT
SRC = os.path.join(ROOT, "Final Presentation", "SEP'26",
                   "Output 8 - Parking Surveys and Analysis Report_25082026_Logit comments"
                   " - STS responses.docx")
OCT = os.path.join(ROOT, "Final Presentation", "OCT'26")
OUT = os.path.join(OCT, "Output 8 - Parking Surveys and Analysis Report 15102026 (rev).docx")
MAPS = os.path.join(OCT, "O8 app maps")
g.OUT = os.path.join(OCT, "charts")


def _guard_existing():
    if os.path.exists(OUT) and "--force" not in sys.argv:
        sys.exit(f"refusing to overwrite {OUT} (it may carry hand edits); use --force")


def n(x):
    return f"{round(x):,}"


def main():
    _guard_existing()
    s, f, y = rf.supply(), rf.survey(), rf.yards()
    A, al = f["areas"], f["all"]
    c1, c2 = s["corridors"]["Corridor 01"], s["corridors"]["Corridor 02"]
    k, km, ga, gn, sh, ma = (A[x] for x in ("kentron", "komitas", "mega", "garegin",
                                             "shiraz", "malatia"))
    st = al["stay"]
    empty = al["removed"] - al["displaced"]

    # charts
    figs = {
        "Parking removed as a share of the impact area": g24.fig_removal_share(s),
        "Peak-hour occupancy by surveyed area": g.fig10_peak_occupancy(f),
        "Vehicles present by clock hour": g.fig11_hourly(f),
        "Duration of stay by area": g.fig12_stay_mix(f),
        "Parking removed and demand displaced, by area": g.fig16_displacement(f),
        # app prints (capture_o8_app_maps.py + compose_o8_app_maps.py, O8_MAPS_DIR=OCT'26)
        "On-corridor parking retained and removed": os.path.join(MAPS, "removed.jpg"),
        "occupancy by zone in the six survey areas": os.path.join(MAPS, "occ_grid.jpg"),
    }

    doc = Document(SRC)
    print("September red recoloured:", dx.accept_red(doc), "| comments removed:",
          dx.strip_comments(doc))

    # ---- Executive Summary ------------------------------------------------------
    anchor = dx.find(doc, "The bus priority corridors are: Corridor 1 (11.66 km)")
    dx.insert_block(anchor, [
        (None, f"This report documents the parking supply on and around Corridors 1 and 2, "
               f"measures how that parking is used, and assesses what the conceptual "
               f"corridor designs remove. The desk-based inventory records {n(s['total'])} "
               f"spaces within the corridors and their 100-metre influence area: "
               f"{n(s['on_corridor'])} on-street spaces on the corridors themselves, "
               f"{n(s['cross_street'])} on cross-streets and {n(s['off_street'])} off-street. "
               f"The corridor kerb is largely unmanaged: {s['zones']['free'] * 100 / s['on_corridor']:.0f}% "
               f"of on-corridor spaces are free, only {s['signage_yes'] * 100 / s['on_corridor']:.0f}% "
               f"carry signage and {s['marking_yes'] * 100 / s['on_corridor']:.0f}% marking. Paid parking (Zone A {s['zones']['zone_a']}, "
               f"Zone B {s['zones']['zone_b']}) is concentrated in Kentron and on Komitas Avenue."),
        (None, f"The v2 conceptual design removes {n(s['removed'])} of the {n(s['on_corridor'])} "
               f"on-corridor spaces and retains or re-establishes {n(s['retained'])} "
               f"({s['retained_pct']:.0f}%): Corridor 1 keeps {n(c1['retained'])} of "
               f"{n(c1['existing'])} and Corridor 2 {n(c2['retained'])} of {n(c2['existing'])}. "
               f"Measured against the impact area, the removed spaces are "
               f"{s['removed'] * 100 / s['on_street']:.0f}% of on-street parking and "
               f"{s['removed'] * 100 / s['total']:.0f}% of all parking once off-street is counted. "
               f"These figures follow the v2 design and will change as the design develops."),
        (None, f"A licence-plate occupancy survey of six representative areas (203 zones and "
               f"2,878 spaces, recorded hourly from 07:00 to 24:00 on four working days "
               f"between 29 May and 3 June 2026) measured how the kerb is used. Each vehicle "
               f"is counted for half an hour in the hours it arrives and leaves and for a "
               f"full hour in between. At their busiest hour the six areas together run at "
               f"{al['peak_hour_pct']}% of capacity. Gai Avenue ({ga['peak_hour_pct']}%) and "
               f"Kentron ({k['peak_hour_pct']}%) are the most pressured, Malatia-Sebastia "
               f"({ma['peak_hour_pct']}%) and Shiraz/Hasratyan ({sh['peak_hour_pct']}%) the "
               f"least. Pressure is concentrated on particular streets rather than spread "
               f"across whole areas: {al['over85_pct']}% of zones reach the 85% target at "
               f"their busiest hour, {k['over85_pct']}% in Kentron, and {al['over_capacity']} "
               f"zones, almost all of them small, read above 100%. The kerb serves short "
               f"visits: {st['shortPct']}% of stays last an hour or less, the average stay is "
               f"{al['avg_stay_h']} hours, and each space turns over {al['turnover_lo']} to "
               f"{al['turnover_hi']} times a day."),
        (None, f"In the surveyed areas the design removes {n(al['removed'])} spaces, and at "
               f"the busiest hour {n(al['displaced'])} vehicles were parked in them; that is "
               f"the demand to be re-accommodated. Surviving nearby kerb space can absorb "
               f"{al['absorbed_onstreet_pct']}% of it. The remainder depends on off-street "
               f"capacity, most of which is gated residential courtyards not open to the "
               f"public today. The measures that address this are set out in the companion "
               f"Parking Analysis Report (Output 10)."),
    ])

    # ---- Chapter 5: impacts -----------------------------------------------------
    dx.sub(dx.find(doc, "That is why the design retains or re-establishes 1,220 spaces."),
           r"1,220 spaces", f"{n(s['retained'])} spaces")
    dx.set_text(dx.find(doc, "The bus priority corridors remove 4,875 of the 6,095"),
        f"The bus priority corridors remove {n(s['removed'])} of the {n(s['on_corridor'])} "
        f"on-corridor on-street spaces and retain or re-establish {n(s['retained'])}. "
        f"Corridor 1 loses {n(c1['removed'])} of {n(c1['existing'])} spaces, retaining "
        f"{n(c1['retained'])}; Corridor 2 loses {n(c2['removed'])} of {n(c2['existing'])}, "
        f"retaining {n(c2['retained'])}. Measured against the impact area, those "
        f"{n(s['removed'])} spaces are {s['removed'] * 100 / s['on_street']:.0f}% of the "
        f"{n(s['on_street'])} on-street spaces within the corridors and their 100-metre "
        f"influence area, and {s['removed'] * 100 / s['total']:.0f}% of all "
        f"{n(s['total'])} spaces once the {n(s['off_street'])} off-street spaces are "
        f"counted. The first figure counts on-street supply only; the second includes "
        f"off-street.")

    t7 = dx.find_table(doc, "Field survey: Kentron")
    for row in t7.rows[1:]:
        cell = row.cells[-1]
        txt = cell.text
        head = txt.split("Field survey:")[0]
        if txt.startswith("Zone A and Zone B pricing"):
            new = (f"{head}Field survey: Kentron {k['peak_hour_pct']}% at its busiest hour, "
                   f"with {k['over85_pct']}% of its zones at or above 85% and only "
                   f"{k['absorbed_onstreet_pct']}% absorbable on-street; Komitas "
                   f"{km['peak_hour_pct']}% with {km['absorbed_onstreet_pct']}% on-street "
                   f"absorption - Komitas is reclassified from medium to high on this evidence.")
        elif txt.startswith("Mixed residential"):
            new = (f"{head}Field survey: Garegin Nzhdeh {gn['peak_hour_pct']}% at its busiest "
                   f"hour / {gn['absorbed_onstreet_pct']}% absorption.")
        else:
            new = (f"{head}Field survey: Shiraz/Hasratyan {sh['peak_hour_pct']}% / "
                   f"{sh['absorbed_onstreet_pct']}%, Malatia-Sebastia {ma['peak_hour_pct']}% / "
                   f"{ma['absorbed_onstreet_pct']}% - confirmed lower.")
        dx.set_cell(cell, new)

    # ---- Chapter 6: field occupancy survey ---------------------------------------
    dx.sub(dx.find(doc, "The aggregate headlines are that occupancy at the busiest hour is"),
           r"is 61% across the six areas together, ranging from 35% in Malatia-Sebastia to 99% at Gai Avenue",
           f"is {al['peak_hour_pct']}% across the six areas together, ranging from "
           f"{ma['peak_hour_pct']}% in Malatia-Sebastia to {ga['peak_hour_pct']}% at Gai Avenue")

    # Table 8: average daily occupancy on the new basis (turnover unchanged)
    import apply_o8_sep_zone_table as zt
    rows = zt.rows()
    k_cap = int(rows[1][2].replace(",", ""))   # Kentron zones with occupancy data (534)
    rows = [[r[0].replace(" (Mega Mall)", "")] + r[1:] for r in rows]
    dx.rewrite_table(dx.find_table(doc, "Zones surveyed", "Average daily occupancy"), rows)

    dx.set_text(dx.find(doc, "How occupancy is measured."),
        f"How occupancy is measured. Occupancy is the share of spaces in use: the average "
        f"number of vehicles parked on a stretch of kerb during an hour, divided by the "
        f"number of spaces on it. The hourly rounds record which vehicles were present, "
        f"not how long within the hour each one stood there, so the time is estimated: a "
        f"vehicle counts for half an hour in the hour it is first seen and half an hour in "
        f"the hour it is last seen, and for a full hour in every hour between. A vehicle "
        f"already present at the first round (07:00) or still present at the last counts "
        f"the full hour, because it arrived before or left after the survey window. Each "
        f"area is reported at its busiest hour. In Kentron, for example, an average of "
        f"{n(k['peak_hour_cars'])} vehicles were parked on the {n(k_cap)} surveyed "
        f"spaces during the {k['peak_hour']:02d}:00 hour: {n(k['peak_hour_cars'])} / "
        f"{n(k_cap)} = {k['peak_hour_pct']}%. Every area percentage in this "
        f"chapter is calculated this way. The same calculation for a single zone uses that "
        f"zone's own busiest hour, which shows which stretches of kerb are saturated; "
        f"because those hours differ from zone to zone, zone figures cannot be added up into "
        f"an area figure.")

    import fix_oct_overcapacity as fo
    n_over, n_small = fo.small_overcap()
    dx.set_text(dx.find(doc, "A zone can read above 100%."),
        f"A zone can still read above 100%. This is a result of the calculation, not of "
        f"vehicles parked beyond the kerb. The method credits every vehicle with half an "
        f"hour in the hour it arrives and the hour it leaves; where several vehicles come and "
        f"go through the same small zone within one hour, each stayed less than that, so "
        f"their credited time adds up to more than the zone's spaces could hold at one "
        f"moment. {n_over} of the 203 zones read above 100% at their busiest hour, and "
        f"{n_small} of them have ten spaces or fewer. No area as a whole does: the highest is "
        f"Gai Avenue at {ga['peak_hour_pct']}%.")

    t9 = dx.find_table(doc, "Survey date", "Formal spaces")
    dx.set_cell(next(r.cells[0] for r in t9.rows if "Mega Mall" in r.cells[0].text),
                "Gai Avenue")

    dx.set_text(dx.find(doc, "Across the six areas together, 1,756 distinct vehicles"),
        f"Across the six areas together, an average of {n(al['peak_hour_cars'])} vehicles "
        f"were parked at each area's busiest hour - {al['peak_hour_pct']}% of the 2,878 "
        f"spaces in the zones where occupancy was recorded. That is 52 fewer than the 2,930 "
        f"spaces in Table 9, because five Kentron zones were inventoried on the supply side "
        f"but not swept for occupancy; they are excluded from every occupancy figure in this "
        f"chapter, which is why Kentron is measured against 534 spaces rather than 586. The "
        f"aggregate is not the operative number, because the six areas differ sharply. Gai "
        f"Avenue is the most pressured at {ga['peak_hour_pct']}% at {ga['peak_hour']:02d}:00, "
        f"with Kentron at {k['peak_hour_pct']}% at {k['peak_hour']:02d}:00 and Komitas at "
        f"{km['peak_hour_pct']}% at {km['peak_hour']:02d}:00; Malatia-Sebastia reaches only "
        f"{ma['peak_hour_pct']}% and Shiraz/Hasratyan {sh['peak_hour_pct']}%. No area as a "
        f"whole reaches the 85% target; the pressure sits on particular streets, and "
        f"{k['over85_pct']}% of Kentron's zones reach it at their busiest hour.")

    cap16 = dx.find_styled(doc, "Average daily occupancy by zone in the six survey areas",
                           "Caption")
    dx.set_caption(cap16, "Figure", "All-day average occupancy by zone in the six survey "
                   "areas (not the busiest hour)", number=16)

    t10 = [["Area", "Peak-hour occupancy (area-wide)", "Average stay",
            "Turnover per space/day"]]
    for key in ("kentron", "komitas", "mega", "garegin", "shiraz", "malatia"):
        a = A[key]
        t10.append([a["label"].replace(" (Mega Mall)", ""),
                    f"{a['peak_hour_pct']}% at {a['peak_hour']:02d}:00",
                    f"{a['avg_stay_h']:.1f} h", f"{a['turnover']}"])
    t10.append(["All six areas", f"{al['peak_hour_pct']}% (each area at its own hour)",
                f"{al['avg_stay_h']:.1f} h", f"{al['turnover_lo']} to {al['turnover_hi']}"])
    dx.rewrite_table(dx.find_table(doc, "Peak-hour occupancy (area-wide)", "Average stay"), t10)

    dx.set_text(dx.find(doc, "The corridor kerb is dominated by short visits."),
        f"The corridor kerb is dominated by short visits. About {st['shortPct']}% of stays "
        f"last one hour or less and {st['shortPct'] + st['errandPct']}% four hours or less, "
        f"while all-day storage of more than eight hours is about {st['alldayPct']}% and "
        f"stays of four to eight hours about {st['workerPct']}%. The average stay is "
        f"{al['avg_stay_h']} hours. This distribution holds in all six areas, which is the "
        f"strongest single behavioural finding of the survey: the kerb serves visitors and "
        f"errands, not commuters.")

    # ---- Chapter 7: displacement -------------------------------------------------
    dx.set_text(dx.find(doc, "The conceptual design removes 1,886 spaces in the six surveyed"),
        f"The conceptual design removes {n(al['removed'])} spaces in the six surveyed areas, "
        f"but displacement counts cars, not spaces: a removed space displaces a car only if "
        f"one is parked there. At the busiest hour for the removed zones in each area, an "
        f"average of {n(al['displaced'])} vehicles were parked in them. That is the displaced "
        f"demand the surrounding streets and off-street facilities must absorb. The other "
        f"{n(empty)} removed spaces were empty at that hour, so their loss reduces supply but "
        f"displaces no one. This does not mean that about {empty * 100 / al['removed']:.0f}% "
        f"of the removed spaces are never used, only that they are not all occupied in the "
        f"same hour.")

    t11 = [["Area", "Spaces removed", "Displaced at peak", "Nearby on-street",
            "Absorbed on-street", "Nearby off-street"]]
    for key in ("kentron", "komitas", "mega", "garegin", "shiraz", "malatia"):
        a = A[key]
        t11.append([a["label"].replace(" (Mega Mall)", ""), n(a["removed"]), n(a["displaced"]),
                    n(a["absorb_onstreet"]), f"{a['absorbed_onstreet_pct']}%",
                    n(a["absorb_offstreet"])])
    t11.append(["All six areas", n(al["removed"]), n(al["displaced"]),
                n(al["absorb_onstreet"]), f"{al['absorbed_onstreet_pct']}%",
                n(al["absorb_offstreet"])])
    dx.rewrite_table(dx.find_table(doc, "Displaced at peak", "Absorbed on-street"), t11)

    dx.sub(dx.find(doc, "Measured absorption (surveyed areas)."),
           r"absorbs about 35% \(10% in the Kentron core, 0% in Komitas, up to 97% in Malatia-Sebastia\)",
           f"absorbs about {al['absorbed_onstreet_pct']}% ({k['absorbed_onstreet_pct']}% in the "
           f"Kentron core, {km['absorbed_onstreet_pct']}% in Komitas, all of it in "
           f"Shiraz/Hasratyan and Malatia-Sebastia)")
    for p in dx.find_all(doc, "Measured absorption (surveyed areas)."):
        dx.set_text(p, p.text, keep_lead_bold=True)

    Y = y["areas"]
    order = sorted(Y, key=lambda a: -Y[a]["peak_pct"])
    names = {"kentron": "Nalbandyan", "komitas": "Komitas City", "garegin": "Garegin",
             "mega": "Palace", "malatia": "Sebastia", "shiraz": "Shiraz"}
    rest = ", ".join(f"{names[a]} ({Y[a]['peak_pct']}%)" for a in order[1:])
    dx.set_text(dx.find(doc, "Measured off-street occupancy (field survey)."),
        f"Measured off-street occupancy (field survey). The off-street side of this balance "
        f"is now partly observed, not only inventoried. In each of the six areas the survey "
        f"recorded hourly occupancy in one representative off-street facility "
        f"({y['total_spaces']} surveyed spaces in total) using the same licence-plate method "
        f"as on-street. Averaged across the day these accessible facilities run about "
        f"{y['weighted_avg_pct']}% full, so real off-street headroom demonstrably exists. "
        f"None of the six is full at its busiest hour: {names[order[0]]} in Kentron comes "
        f"closest at {Y[order[0]]['peak_pct']}%, followed by {rest}. These surveyed facilities "
        f"are accordingly excluded from the absorptive-capacity figure above - they already "
        f"carry their own demand - so the off-street capacity counted above refers to the "
        f"still-closed residential yards that could not be surveyed.", keep_lead_bold=True)

    toff = [["Area", "Surveyed off-street facility", "Formal spaces", "Avg. occupancy",
             "Peak-hour occupancy"]]
    for key in ("kentron", "komitas", "garegin", "mega", "malatia", "shiraz"):
        r = Y[key]
        toff.append([A[key]["label"].replace(" (Mega Mall)", ""), r["name"], str(r["spaces"]),
                     f"{r['avg_pct']}%", f"{r['peak_pct']}%"])
    toff.append(["All six (total / weighted avg.)", "-", str(y["total_spaces"]),
                 f"{y['weighted_avg_pct']}%", "-"])
    dx.rewrite_table(dx.find_table(doc, "Surveyed off-street facility", "Peak-hour occupancy"),
                     toff)

    # ---- Conclusions ---------------------------------------------------------------
    dx.set_text(dx.find(doc, "The conceptual corridor designs remove 4,875 of the 6,095"),
        f"The conceptual corridor designs remove {n(s['removed'])} of the "
        f"{n(s['on_corridor'])} on-corridor on-street spaces, {n(c1['removed'])} on Corridor 1 "
        f"and {n(c2['removed'])} on Corridor 2, and retain or re-establish {n(s['retained'])}. "
        f"Measured against the impact area, those {n(s['removed'])} spaces are "
        f"{s['removed'] * 100 / s['on_street']:.0f}% of the {n(s['on_street'])} on-street "
        f"spaces within the corridors and their 100-metre influence area, and "
        f"{s['removed'] * 100 / s['total']:.0f}% of all {n(s['total'])} spaces once off-street "
        f"is included.")

    # ---- figures -------------------------------------------------------------------
    for needle, path in figs.items():
        dx.swap_figure_above(doc, needle, path)

    # leftovers that must not survive
    for needle in ("4,875", "1,220", "1,123", "Mega Mall)", "142%", "89% at 21:00"):
        hits = [p.text[:80] for p in dx.find_all(doc, needle)]
        hits += [c.text[:80] for t in doc.tables for r in t.rows for c in r.cells
                 if needle in c.text]
        if hits:
            print(f"CHECK {needle!r}:", hits)

    os.makedirs(OCT, exist_ok=True)
    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
