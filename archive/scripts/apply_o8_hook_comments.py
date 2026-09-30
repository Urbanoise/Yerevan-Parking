# -*- coding: utf-8 -*-
"""Output 8, 24/08 revision - the ADB review memo of 12 August (W. Hook).

Copies the 12/08 revision and applies the comments that land on the survey report.
Changes are written in red, as in every earlier round, so the reviewer can see what
moved without diffing.

The substantive change is the occupancy basis. The report led with a capacity-weighted
peak that summed each zone's OWN busiest hour; because those hours differ, it counted
vehicles that were never present together, which is why Kentron read 138% and why the
reviewer could not reproduce it from the raw data. Occupancy is now reported at the
area's single busiest clock hour - the most vehicles standing there at one moment,
over capacity - which is what he replicated and got ~91% for Kentron against our 89%.
Zone-level readings still exceed 100%, legitimately: a zone's own peak hour is a real
statistic: an hour-long count of distinct vehicles against what the kerb holds
exceeds 100% wherever the kerb turns over.
Capacity throughout is what a segment can hold, never a count of painted bays -
most of the corridor kerb is unmarked, so a markings-based denominator would be
meaningless and is not used anywhere in the calculations.

Also applied: removal shown against the wider impact area as well as the corridor;
the worksheet repair of 24 August; and the displacement figures it moved.

Numbers come from report_figures.survey() so the document cannot drift from the
GeoJSON. Nothing here re-states a figure by hand.
"""
import os
import re
import shutil
import sys

from docx import Document

import docx_edit as dx
import report_figures as rf

PRES = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(PRES, "Output 8 - Parking Surveys and Analysis Report 12082026 (rev).docx")
DST = os.path.join(PRES, "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")

F = rf.survey()
A, ALL = F["areas"], F["all"]
SURVEYED_CAP = 2878   # surveyed zones carrying occupancy data, the peak-hour denominator

# removal against the three denominators the 24/08 review asked for
ON_CORRIDOR, ON_STREET_ALL, TOTAL, OFFSTREET = 6095, 7825, 14557, 6732
REMOVED = 4875
PCT_ONSTREET = round(100 * REMOVED / ON_STREET_ALL)
PCT_TOTAL = round(100 * REMOVED / TOTAL)


def span_sub(par, pattern, repl, red=True):
    """Regex-replace inside a paragraph even when Word has split the match over runs.

    The replacement goes into the first touched run; with red=True that run is
    recoloured so the change reads as an edit rather than as original text.
    """
    m = re.search(pattern, par.text)
    if not m:
        raise LookupError(f"no match for {pattern[:70]!r} in: {par.text[:90]!r}")
    i, j, first = m.start(), m.end(), True
    pos = 0
    for run in par.runs:
        s, e = pos, pos + len(run.text)
        pos = e
        if e <= i or s >= j:
            continue
        head = run.text[: max(0, i - s)]
        tail = run.text[max(0, j - s):] if j < e else ""
        if first:
            run.text = head + m.expand(repl) + tail
            run.font.color.rgb = dx.RED
        else:
            run.text = head + tail
        first = False
    return par


def hour(a):
    return f"{A[a]['peak_hour']}:00"


def occupancy_basis(doc):
    """The methodology paragraph on what an occupancy figure means, rewritten to keep
    the area basis and the zone basis apart instead of only defending high numbers."""
    dx.set_text(
        dx.find(doc, "How occupancy is measured, and what a figure above 100% means"),
        "How occupancy is measured, and at what scale. Occupancy is the number of "
        "vehicles using a length of kerb, divided by the number of spaces on it. Two "
        "figures follow from that, and this revision keeps them apart. At area level "
        "the report gives the busiest clock hour: the most vehicles standing anywhere "
        "in the area at one moment, against that area's capacity. That is the figure "
        "for judging how full a neighbourhood becomes, and it is the basis of every "
        "area percentage in this chapter. At zone level the report gives each zone's "
        "own busiest hour, which is the right basis for identifying which individual "
        "stretches of kerb are saturated - but those hours fall at different times of "
        "day, so zone figures cannot be added together or averaged into an area total. "
        "An earlier revision did exactly that, which is why Kentron previously appeared "
        f"as 138%. The area reads {A['kentron']['peak_hour_pct']}% at {hour('kentron')}, "
        "and the 138% is now reported only as what it is: the sum of 53 separate zone "
        "peaks, useful for ranking zones and not comparable to an area figure.")

    dx.insert_after(
        dx.find(doc, "the sum of 53 separate zone peaks"),
        "A zone reading above 100% is not a data error. Capacity here is the number of "
        "vehicles a length of kerb can hold, and the count is of every distinct vehicle "
        "that used it during the hour rather than of how many stood there at one "
        "moment. Where the kerb turns over, the two diverge: three vehicles sharing one "
        "space over an hour read as 300%, and the busiest zone in the survey reaches six "
        "times its capacity on that basis. The figure is therefore a measure of how hard "
        "a length of kerb is worked across the hour.")

    dx.set_text(
        dx.find(doc, "Capacity-weighted peak occupancy across all six areas is 93%"),
        f"Across the six areas together, {ALL['peak_hour_cars']:,} vehicles stand on the "
        f"kerb when each area is at its own busiest hour - {ALL['peak_hour_pct']}% of the "
        f"{SURVEYED_CAP:,} surveyed spaces. The aggregate is not the operative number, "
        f"because the six areas differ sharply. Gai Avenue is the most pressured at "
        f"{A['mega']['peak_hour_pct']}% at {hour('mega')}, with Kentron at "
        f"{A['kentron']['peak_hour_pct']}% at {hour('kentron')} and Komitas at "
        f"{A['komitas']['peak_hour_pct']}% at {hour('komitas')}; Malatia-Sebastia reaches "
        f"only {A['malatia']['peak_hour_pct']}% and Shiraz/Hasratyan "
        f"{A['shiraz']['peak_hour_pct']}%. No area is over capacity as a whole at any "
        f"single hour, but that is a statement about neighbourhoods rather than about "
        f"kerbs. Within them the pressure is concentrated: "
        f"{A['kentron']['over_capacity']} of Kentron's 53 surveyed zones, "
        f"{A['komitas']['over_capacity']} of Komitas's 53 and "
        f"{A['mega']['over_capacity']} of Gai Avenue's 10 exceed capacity at their own "
        f"peak hour. Those are the streets where displaced demand cannot simply move to "
        f"the next block.")


def impact_area_denominators(doc):
    """Comment 1: removal is reported against the impact area, not against the corridor.

    The corridor-only share (80% of the on-corridor kerb) is withdrawn at the client's
    direction - it measures the alignment against itself and reads as the headline
    impact when it is not the one the reviewer asked for. The absolute counts stay, so
    nothing is hidden; only the two impact-area shares are given as percentages.
    """
    supply = dx.find(doc, "The bus priority corridors remove 4,875")
    span_sub(supply, r"on-corridor on-street spaces \(80%\) and retain or re-establish "
                     r"1,220 \(20%\)\.",
             "on-corridor on-street spaces and retain or re-establish 1,220.")
    span_sub(supply, r"Corridor 2 loses 3,395 of 3,746, retaining 351\.",
             "Corridor 2 loses 3,395 of 3,746, retaining 351. Measured against the impact "
             f"area, those {REMOVED:,} spaces are {PCT_ONSTREET}% of the "
             f"{ON_STREET_ALL:,} on-street spaces within the corridors and their "
             f"100-metre influence area, and {PCT_TOTAL}% of all {TOTAL:,} spaces once "
             f"the {OFFSTREET:,} off-street spaces are counted. The first figure counts "
             "on-street supply only; the second includes off-street.")

    span_sub(dx.find(doc, "The conceptual corridor designs remove 4,875 of the 6,095"),
             r"on-corridor on-street spaces \(80%\), 1,480 on Corridor 1 and 3,395 on "
             r"Corridor 2, and retain or re-establish 1,220 \(20%\)\. ?",
             "on-corridor on-street spaces, 1,480 on Corridor 1 and 3,395 on Corridor 2, "
             "and retain or re-establish 1,220. Measured against the impact area, those "
             f"{REMOVED:,} spaces are {PCT_ONSTREET}% of the {ON_STREET_ALL:,} on-street "
             "spaces within the corridors and their 100-metre influence area, and "
             f"{PCT_TOTAL}% of all {TOTAL:,} spaces once off-street is included. ")


def displacement_figures(doc):
    """The worksheet repair moved displaced demand from 1,120 to 1,123."""
    span_sub(dx.find(doc, "peak displaced demand was 1,120 vehicles"),
             r"peak displaced demand was 1,120 vehicles against 1,886 spaces removed - 59%",
             f"peak displaced demand was {ALL['displaced']:,} vehicles against "
             f"{ALL['removed']:,} spaces removed - {ALL['displaced_pct']:.0f}%")

    span_sub(dx.find(doc, "the design removes 1,886 spaces, in which 1,120 distinct"),
             r"in which 1,120 distinct", f"in which {ALL['displaced']:,} distinct")

    # The design, not the survey, determines which zones lose their parking; the survey
    # only counted the vehicles standing in them. The original wording credited the
    # survey with both.
    span_sub(dx.find(doc, "Because the survey recorded which zones the conceptual design removes"),
             r"Because the survey recorded which zones the conceptual design removes, "
             r"displacement can be measured rather than assumed\.",
             "Because the conceptual design identifies which of the surveyed zones lose "
             "their parking, and the survey counted the vehicles standing in those same "
             "zones, displacement can be measured rather than assumed.")

    # the demand-side conclusions bullet is dropped entirely - see drop_demand_bullet()


def remaining_stale_figures(doc):
    """Every other place the old occupancy basis or the pre-repair counts survive.

    Anchored on distinctive neighbouring text so they cannot match the correction note
    or the methodology paragraph, both of which quote the old figures on purpose.
    """
    # the second mention inside the "Locally measured" paragraph
    span_sub(dx.find(doc, "counted at each area's own busiest hour and summed across the six areas"),
             r"summed across the six areas \(1,120 vehicles\)",
             f"summed across the six areas ({ALL['displaced']:,} vehicles)")

    # Chapter preamble. It promises aggregate headlines, so it leads with the aggregate
    # and then gives the full range rather than naming a couple of areas arbitrarily -
    # picking the top two left Komitas just below the cut for no stated reason.
    lo = min(A.values(), key=lambda a: a["peak_hour_pct"])
    hi = max(A.values(), key=lambda a: a["peak_hour_pct"])
    span_sub(dx.find(doc, "The aggregate headlines are that capacity-weighted peak occupancy"),
             r"capacity-weighted peak occupancy across the surveyed areas reaches 93%",
             f"occupancy at the busiest hour is {ALL['peak_hour_pct']}% across the six "
             f"areas together, ranging from {lo['peak_hour_pct']}% in {lo['label']} to "
             f"{hi['peak_hour_pct']}% at {hi['label']}")

    # displacement chapter
    span_sub(dx.find(doc, "distinct vehicles were observed at the areas' respective peak hours"),
             r"or 59% of the supply removed",
             f"or {ALL['displaced_pct']:.0f}% of the supply removed")




def drop_demand_bullet(doc):
    """Remove the field-occupancy bullet from the conclusions.

    At the client's direction: Output 8's conclusions cover the supply inventory and
    the design's impact on it; summarising the demand-side analysis belongs to Output
    10. The survey chapter itself is untouched - only the conclusions bullet goes.
    """
    dx.drop(dx.find(doc, "A targeted field occupancy survey on six representative areas"))


def worksheet_repair_note(doc):
    """Comment 5: the missing hour labels. Recorded in the methodology because it
    changed published figures, however slightly."""
    dx.insert_after(
        dx.find(doc, "In total the survey produced 21,186 on-street vehicle sightings"),
        "Correction of 24 August 2026. Review of the raw workbooks found that in a small "
        "number of zone worksheets an hour-block label had not been entered, so two "
        "consecutive hourly sweeps were consolidated under a single hour: that hour then "
        "carried two laps of observations and the hour after it appeared empty. Three "
        "such blocks were separated - Kentron zone 40 (19:00/20:00), Komitas zones 83 "
        "(18:00/19:00) and 86 (14:00/15:00) - each at the row where the surveyor's plate "
        "sequence restarts. Two further blocks, Malatia-Sebastia zones 2 (20:00/21:00) "
        "and 23 (10:00/11:00), show the same pattern but contain no repeated plate to "
        "locate the boundary, so they have been left as recorded rather than split on an "
        "assumption; between them they hold 52 observations and affect no area or "
        "corridor figure in this report. The correction moved capacity-weighted peak "
        "occupancy across the six areas from 93% to 92% and peak displaced demand from "
        "1,120 vehicles to 1,123. No observation was added or discarded; only the hour "
        "against which it is recorded has changed.")


ROW_KEYS = [("Kentron", "kentron"), ("Komitas", "komitas"), ("Gai Avenue", "mega"),
            ("Garegin", "garegin"), ("Shiraz", "shiraz"), ("Malatia", "malatia")]


def area_of(label):
    """Map a table row's area label to an areas[] key."""
    for prefix, key in ROW_KEYS:
        if label.startswith(prefix):
            return key
    return None


def occupancy_table(doc):
    """Table 10 - the peak-occupancy column moves to the area-wide basis, with the
    hour it falls in, so the figure carries its own definition."""
    t = dx.find_table(doc, "Peak occupancy", "Turnover")
    dx.set_cell(t.rows[0].cells[1], "Peak-hour occupancy (area-wide)", bold=True)
    for row in t.rows[1:]:
        key = area_of(row.cells[0].text.strip())
        if key:
            a = A[key]
            dx.set_cell(row.cells[1], f"{a['peak_hour_pct']}% at {a['peak_hour']}:00")
        elif row.cells[0].text.strip().startswith("All six"):
            dx.set_cell(row.cells[1], f"{ALL['peak_hour_pct']}% (each area at its own hour)")


def displacement_table(doc):
    """Table 11 - the two cells the worksheet repair moved."""
    t = dx.find_table(doc, "Displaced at peak", "Absorbed on-street")
    for row in t.rows[1:]:
        key = area_of(row.cells[0].text.strip())
        if key:
            dx.set_cell(row.cells[2], f"{A[key]['displaced']:,}")
        elif row.cells[0].text.strip().startswith("All six"):
            dx.set_cell(row.cells[2], f"{ALL['displaced']:,}")



def _guard_existing():
    """Refuse to overwrite a deliverable that has been edited by hand since it was built.

    These scripts rebuild from the previous revision every run. Once the output has been
    opened in Word and worked on - wording adjusted, accepted red text recoloured to
    black - a rebuild silently discards all of it. Further changes to an already-issued
    revision belong in a targeted in-place script (see apply_o8_pending_edits.py), which
    edits the saved file and leaves everything else untouched.

    --force regenerates from source anyway, losing any hand edits.
    """
    if os.path.exists(DST) and "--force" not in sys.argv:
        raise SystemExit(
            "REFUSING to rebuild " + os.path.basename(DST) + " - it already exists and "
            "may carry hand edits that a rebuild would discard. Apply further changes in "
            "place instead (see apply_o8_pending_edits.py), or re-run with --force to "
            "regenerate it from " + os.path.basename(SRC) + " and lose them.")


def main():
    _guard_existing()
    shutil.copyfile(SRC, DST)
    doc = Document(DST)

    occupancy_basis(doc)
    occupancy_table(doc)
    displacement_table(doc)
    impact_area_denominators(doc)
    displacement_figures(doc)
    remaining_stale_figures(doc)
    drop_demand_bullet(doc)
    # WITHDRAWN, 24 Aug 2026, at the client's direction. The note recorded what the
    # worksheet repair found and what it moved (93%->92%, 1,120->1,123 vehicles).
    # Every figure in the report is now the corrected one, so the note documented
    # our own processing history rather than anything the reader needs; the account
    # of what was found belongs in the reply to the reviewer, where it now sits.
    # worksheet_repair_note(doc)

    # a stray edit artefact from an earlier round
    span_sub(dx.find(doc, "raI fixedther"), r"raI fixedther", "rather", red=False)

    # Capacity is what fits, not what is painted. The original wording framed the
    # fallback as an exception for unmarked segments, which reads as though a marked
    # bay count were the norm; on these corridors it is the other way round.
    off = dx.find(doc, "already at or beyond their marked capacity")
    span_sub(off, r"already at or beyond their marked capacity",
             "already at or beyond capacity")
    # The reader meets a reading over 100% here, well before the chapter that explains
    # what one means. With area figures now on the single-hour basis and none of them
    # over 100%, an unexplained 194% reads as a contradiction rather than as overflow.
    span_sub(off, r"These surveyed facilities are accordingly excluded",
             "Each of these is a single facility measured at its own busiest hour, and a "
             "reading above 100% is a real measure of overflow rather than a data error; "
             "the chapter on the field occupancy survey sets out in detail how it arises. "
             "These surveyed facilities are accordingly excluded")

    span_sub(dx.find(doc, "Occupancy is measured against the formal capacity"),
             r"Occupancy is measured against the formal capacity already recorded in the "
             r"supply inventory, so the demand and supply sides share a single "
             r"denominator\. Where a segment has no marked bays, capacity is the inventory "
             r"estimate of one space per 7\.5 metres of parallel kerb\.",
             "Occupancy is measured against the capacity already recorded in the supply "
             "inventory - the number of vehicles a segment can hold - so the demand and "
             "supply sides share a single denominator. Where the inventory carries no "
             "figure for a segment, capacity is estimated at one vehicle per 7.5 metres "
             "of parallel kerb.")

    doc.save(DST)
    print("saved:", os.path.basename(DST))


if __name__ == "__main__":
    main()
