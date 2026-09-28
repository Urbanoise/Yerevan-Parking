# -*- coding: utf-8 -*-
"""Reply to the ADB review memo of 12 August inside the memo itself.

Writes real Word comment bubbles anchored to the paragraphs they answer, so the memo
can go back as a marked-up document rather than as a separate response note. The
original is left untouched; replies land in a copy.

One reply per point the memo raises: what changed and where, or where the memo is
mistaken and on what evidence, or that the point is still open. Figures are pulled
from report_figures so a bubble cannot quote a number the reports no longer carry.
"""
import os
import shutil
import sys

from docx import Document

import report_figures as rf

PRES = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(PRES, "Memo on Parking Surveys and Policy.docx")
DST = os.path.join(PRES, "Memo on Parking Surveys and Policy - STS responses 24082026.docx")

AUTHOR, INITIALS = "Nikoloz Archavadze, STS", "NA"

F = rf.survey()
A, ALL = F["areas"], F["all"]
K = A["kentron"]

# anchor phrase -> reply. Anchors are verbatim fragments of the memo.
REPLIES = [
    ("the report and presentations should present the total share of parking spaces removed",
     "Added, and the corridor-only share is withdrawn. Both reports now state removal "
     "against the impact area rather than against the alignment: the 4,875 spaces "
     "removed are 62% of the 7,825 on-street spaces within the corridors and their "
     "100-metre influence area, and 33% of all 14,557 spaces once the 6,732 off-street "
     "spaces are counted. The absolute counts are unchanged, so nothing is hidden - but "
     "the 80% figure measured the corridor against itself and is no longer given. "
     "Per-area figures are in the displacement table."),

    ("an original supply of 534 parking spaces was available",
     "Our figures differ and we should reconcile them. We record 178 spaces retained of "
     "586 surveyed in Kentron (408 removed), against your 224 of 534. Two causes: ours "
     "are rebased on the v2 conceptual design, which post-dates the 3 July report you "
     "reviewed, and our Kentron zone list runs to 58 zones. Happy to go through it line "
     "by line."),

    ("The presentation of values over 100% for a parking occupancy survey is confusing",
     "Accepted, and corrected. Area figures now use the single busiest clock hour - the "
     f"basis you applied - so Kentron reads {K['peak_hour_pct']}% at {K['peak_hour']}:00 "
     "against your ~91%. Zone-level figures keep each zone's own peak hour and can still "
     "exceed 100%. That is real rather than an artefact. Capacity in this survey is the "
     "number of vehicles a length of kerb can hold, not a count of painted bays - most of "
     "the corridor is unmarked, so markings play no part in the calculation. A reading "
     "goes past 100% because the count is of every distinct vehicle that used the space "
     "during the hour, not of how many stood there at once - three vehicles sharing one "
     "space over an hour read as 300%. It measures how hard the kerb is worked across "
     "the hour."),

    ("leave it up to Nico whether or not he wants the occupancy rates recalculated",
     "None, as it turns out. Both bases were already being computed in our processing "
     "chain and printed side by side on every run; the reports simply led with the wrong "
     "one. No re-processing of the raw data was needed."),

    ("Present the occupancy data on an area by area basis rather than in aggregate",
     "Already done in the 30 July revision of Output 8 and in the web dashboard, both "
     "per area and per zone below that. The 24 July deck was the last artefact still "
     "leading with aggregates. You were reviewing the 3 July documents."),

    ("The figures representing parking removed by the project are not based on the latest",
     "We are now working to the v2 design of 23 July, which identifies 1,220 retained "
     "spaces individually. If the PIU adds parking, the figures will be re-cut against "
     "the design when it is final."),

    ("this worksheet shows that there is no detailed breakdown in zones where some of the",
     "The retained set is not derived from a threshold applied to whole zones - it is "
     "drawn by hand from the v2 design, space by space, to 1,220 spaces in total. So a "
     "part-retained stretch is not rounded in or out, and we have not applied a "
     "fractional split, which would be less precise than the drawing."),

    ("In a few of the zone specific worksheets, the time period was missing",
     "Confirmed, corrected, and it went further than the two you opened. Zone 40's block "
     "held two hourly sweeps under one label; it is now split, giving 25 vehicles at "
     "19:00 and 18 at 20:00. Zone 19's label is also absent, but its block contains a "
     "single sweep, so no observation was misplaced there. A sweep of all six workbooks "
     "found three more genuine merges - Komitas zones 83 and 86, both now split, and "
     "Malatia-Sebastia zones 2 and 23, where no plate repeats inside the block so the "
     "boundary cannot be located; those two are left as recorded and flagged in the "
     "methodology rather than split on an assumption."),

    ("These instances certainly seem like it was a surveyor error",
     "It was not a surveyor error - it is the missing label. The 20:00 sweep sat under "
     "the 19:00 heading, so a vehicle recorded at 19:00 and again at 21:00 looked as "
     "though it had left and returned. The 8-9pm concentration you noticed is exactly "
     "where the defect sits. No caveat about an undercounted evening window is needed "
     "now that the block is split."),

    ("It is not clear how STS got results of 138% occupancy rates in Kentron",
     "You were right and we have changed it. The 138% was the sum of the 53 Kentron "
     "zones' individual peak hours divided by total capacity. Those peaks fall at "
     "different times of day, so the figure counted vehicles that were never present "
     f"together. At a single clock hour Kentron peaks at {K['peak_hour_cars']} vehicles "
     f"at {K['peak_hour']}:00, which is {K['peak_hour_pct']}% of its 534 spaces - your "
     "figure. Both reports now lead with that basis, and the zone-level series is "
     "labelled as what it is."),

    ("why are they colored green?  What does cap weighted mean?",
     "Fair on both counts. The colour on that view is the retained/removed lens, not "
     "occupancy, so a green segment is one the design keeps and can still be busy - the "
     "legend does not say so clearly enough. 'Capacity-weighted' meant each zone weighted "
     "by its number of spaces rather than counted equally; the term is retired in this "
     "revision. We can send the per-zone table behind the figure."),

    ("Nico was unhappy that the primary solution emphasized in the Parking Analysis",
     "Accepted in full and actioned on 14 August, before this memo reached us. The "
     "measure, its two figures, its entry in the further-studies list and every "
     "absorption claim that rested on it have been removed from Output 10."),

    ("Since there is only one parking yard it would be good to know more about it",
     "One correction for the record. That yard is the only one we occupancy-surveyed in "
     "Kentron, not the only one inventoried: the supply survey holds 15 off-street yards "
     "totalling 455 spaces within 100 m of the Kentron survey footprint. It does not "
     "change your conclusion, since the other 14 are the gated courtyards now ruled out, "
     "but the downtown off-street stock is larger than the memo implies. Whether that "
     "yard is publicly accessible and charged is a question we will put to the operator."),

    ("Its also not clear how there could be such a large negative occupancy",
     "The negative values follow from subtracting observed vehicles from a fixed 60-space "
     "capacity: in hours when more than 60 distinct vehicles used the yard, the remainder "
     "goes below zero. It is the same turnover effect that produces readings above 100% - "
     "an hour-long count records every vehicle that used the space, not how many stood "
     "there at once."),

    ("of the 2725 parked vehicles observed in the Kentron area throughout the day",
     "Agreed, and the data supports it. One definitional gap to settle first: you count "
     "766 of 2,725 Kentron vehicles staying over two hours; our stay bins give 1,384 of "
     "3,002. We will reconcile the two definitions before either figure is published, "
     "then quantify the vehicle-hours a two-hour cap would release, zone by zone."),

    ("Its seems like it should be possible to quantify the number of parking spaces",
     "Agreed. 2,654 of the 2,930 surveyed kerb spaces are unpriced white, against 276 "
     "paid blue, so the convertible stock is known per zone. Your point about "
     "redistribution within a zone is one we had not made and is now in Output 10 under "
     "the occupancy-based tariff measure."),

    ("In general the policy measures proposed should be backed up with data",
     "Accepted as the main outstanding item in this review. Quantifying every measure in "
     "every zone is a substantial piece of work and we would rather size it with you than "
     "commit to a scope here - our suggestion is to start with the three high-sensitivity "
     "areas."),

    ("Increase the parking charges even on the existing charged parking zones",
     "This measure has been in the report since the July revision - adjusting charges "
     "zone by zone to the 85% occupancy target, with the rate set against published "
     "measurements. The June text you reviewed predates it. Your point about the legal "
     "mechanism is new and is now added: set the permitted band in the Council decision "
     "and delegate movement within that band to the parking authority, which would need a "
     "revision to the parking legislation."),

    ("Giving the revenue to the neighborhood to incentivize participation",
     "Added under the pricing measure as a parking benefit district - a defined share of "
     "the revenue raised in an area spent on visible local improvements in the same area, "
     "and reported publicly. It had been in the draft inside the residential-yards "
     "section and was removed with it; it never depended on the yards, so it is now "
     "re-homed."),

    ("I am not in favor of expanding the downtown parking supply",
     "Agreed, and neither report recommends new downtown supply. The one place we stop "
     "short of removal is Gai Avenue, where the kerb parking is left in place for now "
     "rather than replaced, pending the mall's own parking or the planned BRT."),
]



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

    paras = doc.paragraphs
    placed, missed = 0, []
    for anchor, reply in REPLIES:
        target = next((p for p in paras if anchor in p.text and p.runs), None)
        if target is None:
            missed.append(anchor[:60])
            continue
        doc.add_comment(runs=target.runs, text=reply, author=AUTHOR, initials=INITIALS)
        placed += 1

    doc.save(DST)
    print(f"placed {placed} of {len(REPLIES)} comments")
    for m in missed:
        print("  NOT ANCHORED:", m)
    print("saved:", os.path.basename(DST))


if __name__ == "__main__":
    main()
