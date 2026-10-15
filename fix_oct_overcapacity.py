# -*- coding: utf-8 -*-
"""OCT'26 copies of Output 8 / Output 10: why a zone reads above 100%.

The first pass explained it as parking beyond the formal spaces (vehicles off the
carriageway). That is wrong: those zones read high because of the calculation. Each
vehicle is credited half an hour in its arrival and departure hours; when several come
and go through the same small zone within one hour they stayed less than that, so the
credited time adds up to more than the spaces could hold at once. 43 of the 44 such
zones have ten spaces or fewer. Edits the saved files in place (they may carry hand
edits), red as the rest of this round.
"""
import json
import os

from docx import Document

import docx_edit as dx
import report_figures as rf

OCT = os.path.join(rf.ROOT, "Final Presentation", "OCT'26")
O8 = os.path.join(OCT, "Output 8 - Parking Surveys and Analysis Report 15102026 (rev).docx")
O10 = os.path.join(OCT, "Output 10 - Parking Analysis Report 15102026 (rev).docx")


def small_overcap(max_space=10):
    feats = json.load(open(rf.SURVEYS, encoding="utf-8"))["features"]
    over = [f["properties"] for f in feats
            if f["properties"].get("peak_occupancy") is not None
            and f["properties"].get("space")
            and f["properties"]["peak_occupancy"] > f["properties"]["space"]]
    return len(over), sum(1 for p in over if p["space"] <= max_space)


def main():
    f = rf.survey()
    al, k, ga = f["all"], f["areas"]["kentron"], f["areas"]["mega"]
    n_over, n_small = small_overcap()
    assert n_over == al["over_capacity"], (n_over, al["over_capacity"])

    doc = Document(O8)
    assert dx.sub(dx.find(doc, "zones hold more vehicles than their formal capacity"),
                  r"and (\d+) zones hold more vehicles than their formal capacity\.",
                  r"and \1 zones, almost all of them small, read above 100%.")
    dx.set_text(dx.find(doc, "A zone can still read above 100%."),
        f"A zone can still read above 100%. This is a result of the calculation, not of "
        f"vehicles parked beyond the kerb. The method credits every vehicle with half an "
        f"hour in the hour it arrives and the hour it leaves; where several vehicles come and "
        f"go through the same small zone within one hour, each stayed less than that, so "
        f"their credited time adds up to more than the zone's spaces could hold at one "
        f"moment. {n_over} of the 203 zones read above 100% at their busiest hour, and "
        f"{n_small} of them have ten spaces or fewer. No area as a whole does: the highest is "
        f"Gai Avenue at {ga['peak_hour_pct']}%.")
    doc.save(O8)
    print("saved", O8)

    doc = Document(O10)
    assert dx.sub(dx.find(doc, "hold more vehicles than their capacity at their own peak"),
                  r"and (\d+) hold more vehicles than their capacity at their own peak",
                  r"and \1 read above 100% at their own peak")
    p = dx.find(doc, "more vehicles than they have spaces")
    assert dx.sub(p, r"and (\d+) hold more vehicles than they have spaces",
                  r"and \1 read above 100%")
    assert dx.sub(p, r"and (\d+) exceed capacity,", r"and \1 read above 100%,")
    doc.save(O10)
    print("saved", O10)


if __name__ == "__main__":
    main()
