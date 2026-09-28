# -*- coding: utf-8 -*-
"""Soften the measured-recalibration paragraph of Output 10, IN PLACE.

The facts are unchanged. What changes is the order and the adjectives: the paragraph
led with the two most constrained areas and buried the reassuring aggregate at the end,
and it carried loaded phrasing - "the constraint is acute", "the binding constraint",
"none ... at all", "nowhere to go", "theoretical maximum" - that made a measured
finding read as an alarm.

Three substantive improvements go with the tone:

  * the aggregate finding (1,123 vehicles displaced against 1,886 spaces removed) moves
    to the front, where it frames the per-area detail instead of trailing it;
  * a sentence is added explaining what the absorption percentages actually count -
    kerb the survey did not already measure, excluding the parking retained on the
    corridors, which carries its own users. Komitas's 0% means no uncounted kerb
    nearby, not that the area is left with no parking, and the paragraph previously
    invited the harsher reading;
  * "and is reclassified accordingly throughout this report" was dangling off the end
    of a parenthesis about absorption; it now attaches to the reclassification.

The paragraph's two body runs are currently red (this revision's changes, not yet
accepted), so the replacement stays red to match. Backup written first.
"""
import os
import shutil

from docx import Document

import docx_edit as dx
import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 25082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-tone-edit).docx")

F = rf.survey()
A, ALL = F["areas"], F["all"]

NEW = (
    " The survey tests these a-priori labels against behaviour. Across the surveyed "
    f"areas the design removes {ALL['removed']:,} spaces, in which {ALL['displaced']:,} "
    "distinct vehicles were counted at each area's busiest hour, so measured "
    "displacement falls well below the supply removed. Beneath that aggregate the areas "
    f"differ. Kentron is confirmed high-sensitivity, at {A['kentron']['peak_hour_pct']}% "
    f"occupancy at its busiest hour with {A['kentron']['over_capacity']} of its 53 zones "
    "over capacity, and about 10% of its displaced demand can be re-absorbed on nearby "
    "streets. Komitas, previously medium, behaves as high-sensitivity and is "
    "reclassified accordingly throughout this report: it reaches "
    f"{A['komitas']['peak_hour_pct']}% at its busiest hour with "
    f"{A['komitas']['over_capacity']} of its 53 zones over capacity, and none of its "
    "displaced demand can be re-absorbed on the surrounding kerb. Both absorption "
    "figures count only kerb that the survey did not already measure, and exclude the "
    "parking retained on the corridors themselves, which carries its own users. "
    "Shiraz/Hasratyan and Malatia-Sebastia behave as genuinely lower-sensitivity, at "
    f"{A['shiraz']['peak_hour_pct']}% and {A['malatia']['peak_hour_pct']}% at their "
    f"busiest hours. Gai Avenue is the exception: at {A['mega']['peak_hour_pct']}% it is "
    "the fullest of the six, and the capacity around it is smaller than what the design "
    "removes, so its kerb parking stays for now and is given a fresh look as the area "
    "changes - when new facilities become available or the planned BRT line arrives.")


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)

    par = dx.find(doc, "Measured recalibration (field survey)")
    if len(par.runs) < 2:
        raise SystemExit("paragraph structure changed - expected a bold lead run "
                         "followed by body runs")

    # Refuse if the paragraph is no longer the one this rewrite was written against.
    # These phrases are exactly what the rewrite removes; if any is already gone, the
    # text has been edited by hand since and overwriting it would destroy that work.
    expected = ["the constraint is acute",
                "the binding constraint",
                "nowhere to go",
                "theoretical maximum"]
    missing = [e for e in expected if e not in par.text]
    if missing:
        raise SystemExit(
            "REFUSING to rewrite the paragraph - it has changed since this edit was "
            "prepared. Missing marker(s): " + "; ".join(missing) + ". Re-read the "
            "paragraph and rebuild the replacement against its current wording.")

    # Report what is being preserved, so the colour decision is visible rather than
    # assumed: the replacement inherits run 1's formatting, whatever it now is.
    colour = par.runs[1].font.color
    shown = colour.rgb if colour is not None and colour.type is not None else "automatic"
    print("lead run kept as-is:", repr(par.runs[0].text))
    print("replacement inherits run 1 colour:", shown)

    # keep run 0 (the bold "Measured recalibration (field survey)." lead) exactly as is;
    # the replacement goes into run 1, which carries this revision's red, and the
    # remaining body runs are emptied.
    par.runs[1].text = NEW
    for run in par.runs[2:]:
        run.text = ""

    doc.save(DOC)
    print("backup:", os.path.basename(BAK))
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
