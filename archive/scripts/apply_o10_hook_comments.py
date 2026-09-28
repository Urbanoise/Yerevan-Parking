# -*- coding: utf-8 -*-
"""Output 10, 24/08 revision - the ADB review memo of 12 August (W. Hook).

Copies the 14/08 rev 2 (the yard measure already removed) and applies the comments
that land on the analysis report. Changes are written in red.

Occupancy moves to the same basis as Output 8: area figures are the area's single
busiest clock hour, zone figures are each zone's own peak. The pricing measure keeps
its evidence but now argues it at zone level, which is where the argument actually
lives - you price the kerbs that are full, not the neighbourhoods.

Also applied: Komitas's reclassification rejustified on absorption rather than on the
withdrawn occupancy figure; the revenue-earmarking idea re-homed after the yards
section was deleted; the reviewer's rate-band delegation point added; and the
displacement figures the 24/08 worksheet repair moved.
"""
import os
import re
import shutil
import sys

from docx import Document

import docx_edit as dx
import report_figures as rf

PRES = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(PRES, "Output 10 - Parking Analysis Report - 14082026 (rev 2).docx")
DST = os.path.join(PRES, "Output 10 - Parking Analysis Report - 25082026 (rev).docx")

F = rf.survey()
A, ALL = F["areas"], F["all"]
SURVEYED_ZONES = 203

ON_STREET_ALL, TOTAL, OFFSTREET, REMOVED = 7825, 14557, 6732, 4875
PCT_ONSTREET = round(100 * REMOVED / ON_STREET_ALL)
PCT_TOTAL = round(100 * REMOVED / TOTAL)


def span_sub(par, pattern, repl, red=True):
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


def occupancy_basis(doc):
    """Every area-level occupancy figure moves to the busiest-clock-hour basis."""
    span_sub(dx.find(doc, "The Kentron commercial core runs at 138% peak occupancy"),
             r"The Kentron commercial core runs at 138% peak occupancy",
             f"The Kentron commercial core runs at {A['kentron']['peak_hour_pct']}% "
             f"occupancy at its busiest hour, with {A['kentron']['over_capacity']} of its "
             f"53 zones over capacity at their own peak")

    span_sub(dx.find(doc, "The Malatia-Sebastia residential segment shows the lowest daytime"),
             r"\(54% peak\)", f"({A['malatia']['peak_hour_pct']}% at its busiest hour)")

    rec = dx.find(doc, "Measured recalibration (field survey)")
    span_sub(rec,
             r"Kentron is confirmed high-sensitivity \(138% peak\)",
             f"Kentron is confirmed high-sensitivity "
             f"({A['kentron']['peak_hour_pct']}% at its busiest hour, and "
             f"{A['kentron']['over_capacity']} of its 53 zones over capacity)")

    # the two lower-sensitivity areas and the Gai exception, in the same paragraph
    span_sub(rec, r"behave as genuinely lower-sensitivity \(75% and 54% peak\)",
             f"behave as genuinely lower-sensitivity "
             f"({A['shiraz']['peak_hour_pct']}% and {A['malatia']['peak_hour_pct']}% at "
             f"their busiest hours)")
    span_sub(rec, r"leaves a residual with nowhere to go \(123% peak\)",
             f"leaves a residual with nowhere to go "
             f"({A['mega']['peak_hour_pct']}% at its busiest hour, the highest of the six "
             f"areas)")


def komitas_reclassification(doc):
    """The move from medium to high sensitivity rested partly on a 123% occupancy
    figure that no longer stands as an area statistic. The absorption evidence does
    stand, and is the stronger of the two: nothing displaced from Komitas can be
    re-absorbed on the surrounding kerb."""
    span_sub(dx.find(doc, "Komitas, previously medium, behaves as high-sensitivity"),
             r"Komitas, previously medium, behaves as high-sensitivity \(123% peak, 0% "
             r"on-street absorption\)",
             f"Komitas, previously medium, behaves as high-sensitivity: it reaches "
             f"{A['komitas']['peak_hour_pct']}% at its busiest hour with "
             f"{A['komitas']['over_capacity']} of its 53 zones over capacity, and - the "
             f"binding constraint - none of its displaced demand can be re-absorbed on "
             f"the surrounding kerb at all (0% on-street absorption)")

    span_sub(dx.find(doc, "The Kentron CBD and Komitas Avenue face the highest pressure"),
             r"- 138% and 123% peak occupancy, with only 10% and 0% of displaced demand "
             r"re-absorbable on nearby streets - and Komitas is reclassified from medium "
             r"to high sensitivity on that evidence\.",
             f"- {A['kentron']['peak_hour_pct']}% and {A['komitas']['peak_hour_pct']}% "
             f"occupancy at their busiest hours, {A['kentron']['over_capacity']} and "
             f"{A['komitas']['over_capacity']} of their zones over capacity individually, "
             f"and only 10% and 0% of displaced demand re-absorbable on nearby streets. "
             f"Komitas is reclassified from medium to high sensitivity on the absorption "
             f"evidence above all: it is the one high-pressure area with no kerbside room "
             f"nearby at all.")


def pricing_measure(doc):
    """The 85% measure argued at zone level, which is the scale a tariff acts on."""
    span_sub(dx.find(doc, "Measured occupancy is well above that"),
             r"Measured occupancy is well above that\. Capacity-weighted peak occupancy "
             r"across the surveyed areas is 93%, and 116 zones are over capacity outright\. "
             r"In Kentron, which is entirely within Zone A, peak occupancy reaches 138%\.",
             f"Measured occupancy is well above that on the kerbs that matter. Of the "
             f"{SURVEYED_ZONES} surveyed zones, {ALL['over85_pct']}% are at or above the "
             f"85% target at their busiest hour and {ALL['over_capacity']} are over "
             f"capacity outright. The pressure is concentrated rather than general: in "
             f"Kentron, which lies entirely within Zone A, "
             f"{A['kentron']['over_capacity']} of 53 zones exceed capacity and the area "
             f"as a whole reaches {A['kentron']['peak_hour_pct']}% at "
             f"{A['kentron']['peak_hour']}:00, while Gai Avenue reaches "
             f"{A['mega']['peak_hour_pct']}%.")

    span_sub(dx.find(doc, "This is not a general tariff increase"),
             r"in the outer areas, where peak occupancy is 54% to 75%",
             f"in the outer areas, where occupancy at the busiest hour runs from "
             f"{A['malatia']['peak_hour_pct']}% to {A['garegin']['peak_hour_pct']}%")


def rate_band_delegation(doc):
    """The reviewer's own suggestion: a parking-law revision could let an authority
    move rates within a band without returning to the Council for each change."""
    dx.insert_after(
        dx.find(doc, "This is not a general tariff increase"),
        "A tariff that is reviewed against measured occupancy on a fixed cycle also "
        "raises a practical question of who may change it. If every adjustment requires "
        "a fresh Council of Elders decision, the review cycle will not survive contact "
        "with the calendar. The alternative, which would need a revision to the parking "
        "legislation, is to set the permitted range in the decision itself and delegate "
        "movement within that band to the parking authority, against published "
        "occupancy data and a stated rule. The Council would then be deciding the policy "
        "- the target, the band and the evidence that triggers a move - rather than each "
        "individual price.")


def revenue_earmarking(doc):
    """The Parking Benefit District argument was made inside the residential-yards
    section and was deleted with it on 14 August. It never depended on the yards, so
    it is re-homed under the pricing measure."""
    dx.insert_after(
        dx.find(doc, "The Council would then be deciding the policy"),
        "Public acceptance is easier to win where the money visibly returns to the "
        "streets that generate it. International practice calls this a parking benefit "
        "district: a defined share of the parking revenue raised in an area is spent on "
        "visible local improvements in that same area - footway repair, lighting, "
        "crossings, planting - and reported publicly. The mechanism matters less than "
        "the visibility: it is repeatedly what turns residents from opponents of "
        "parking charges into supporters of them, because the charge stops reading as "
        "extraction and starts reading as a local service. Yerevan already has a "
        "candidate version of this in the proposal to earmark Zone A revenue for the "
        "electric bus fleet; the same logic applied at neighbourhood scale would "
        "strengthen the case for extending paid parking onto the cross-streets.")


def displacement_figures(doc):
    """The 24/08 worksheet repair: displaced demand 1,120 -> 1,123, so 59% -> 60%."""
    span_sub(dx.find(doc, "Across the surveyed areas, peak displaced demand was 1,120"),
             r"peak displaced demand was 1,120 vehicles against 1,886 spaces removed \(59%\)",
             f"peak displaced demand was {ALL['displaced']:,} vehicles against "
             f"{ALL['removed']:,} spaces removed ({ALL['displaced_pct']:.0f}%)")


def impact_area_denominators(doc):
    """Comment 1, carried into the analysis report so the two documents agree.

    The corridor-only share is withdrawn at the client's direction: removal is stated
    against the impact area only, on the two denominators the reviewer asked for. The
    absolute counts are unchanged.
    """
    span_sub(dx.find(doc, "meaning that around 80% of current corridor parking would be removed"),
             r",\s*meaning that around 80% of current corridor parking would be removed\.",
             f". Against the impact area, those {REMOVED:,} spaces are {PCT_ONSTREET}% of "
             f"all {ON_STREET_ALL:,} on-street spaces within 100 metres of the corridors, "
             f"and {PCT_TOTAL}% of all {TOTAL:,} spaces once the {OFFSTREET:,} off-street "
             f"spaces are included.")

    # the Key Conclusions bullet carries the counts but no share at all
    span_sub(dx.find(doc, "Design removes 4,875 of the 6,095 on-corridor on-street spaces"),
             r"on Corridors 1 and 2, retaining 1,220\.",
             f"on Corridors 1 and 2, retaining 1,220 - {PCT_ONSTREET}% of the on-street "
             f"spaces in the impact area, and {PCT_TOTAL}% of all parking within it.")



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
    komitas_reclassification(doc)
    pricing_measure(doc)
    rate_band_delegation(doc)
    revenue_earmarking(doc)
    displacement_figures(doc)
    impact_area_denominators(doc)

    doc.save(DST)
    print("saved:", os.path.basename(DST))


if __name__ == "__main__":
    main()
