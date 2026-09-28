# -*- coding: utf-8 -*-
"""Correct how the area-level occupancy figure is described, IN PLACE.

The methodology paragraph called the area figure "the most vehicles standing anywhere
in the area at one moment". That is wrong. What the pipeline computes is

    vap[hour] = sum over zones of (distinct plates seen in that zone during that hour)

so the area figure counts vehicles that USED the kerb during the busiest clock hour,
exactly like the zone figure. The only difference between the two is which hour is
used: one shared across the area, or each zone's own.

That distinction matters for the reader, because it answers the obvious question the
chapter otherwise leaves open - if a zone can read 300%, why does no area exceed 100%?
The answer is that no area's kerb turned over fast enough within a single shared hour
to pass its capacity. It is a result, not a cap, and the report should say so rather
than implying the area figure is bounded by construction.

Edits the saved document; every other byte is left alone. Backup written first.
"""
import os
import re
import shutil

from docx import Document

import docx_edit as dx
import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-area-basis-note).docx")

F = rf.survey()
A, ALL = F["areas"], F["all"]


def sub_in_place(par, pattern, repl):
    """Regex-replace across runs, keeping each touched run's formatting."""
    m = re.search(pattern, par.text)
    if not m:
        return False
    i, j, first = m.start(), m.end(), True
    pos = 0
    for run in par.runs:
        s, e = pos, pos + len(run.text)
        pos = e
        if e <= i or s >= j:
            continue
        head = run.text[: max(0, i - s)]
        tail = run.text[max(0, j - s):] if j < e else ""
        run.text = head + (m.expand(repl) if first else "") + tail
        first = False
    return True


def find_maybe(doc, needle):
    return next((p for p in doc.paragraphs if needle in p.text), None)


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)
    done, skipped = [], []

    # 1. the area-level sentence: same count as the zone figure, different hour
    p = find_maybe(doc, "At area level the report gives the busiest clock hour")
    if p is not None and sub_in_place(
            p,
            r"At area level the report gives the busiest clock hour: the most vehicles "
            r"standing anywhere in the area at one moment, against that area's capacity\.",
            "At area level the report gives the busiest clock hour: of the hours "
            "surveyed, the one in which the greatest number of distinct vehicles used "
            "the area's kerb, against that area's capacity. It counts the same thing the "
            "zone figure counts - vehicles that used the kerb during the hour, not a "
            "snapshot of how many stood there at once - but it takes a single hour "
            "shared across the whole area instead of each zone's own busiest hour."):
        done.append("area-level sentence corrected")
    else:
        skipped.append("area-level sentence")

    # 2. why no area exceeds 100% on that basis - a result, not a cap. Sits at the end
    #    of the same paragraph, after the sentence explaining why zone peaks cannot be
    #    aggregated.
    p = find_maybe(doc, "so zone figures cannot be added together or averaged into an area total")
    if p is not None and sub_in_place(
            p,
            r"so zone figures cannot be added together or averaged into an area total\.",
            "so zone figures cannot be added together or averaged into an area total. "
            "The shared hour also spreads the count across all of an area's kerb, "
            "including the stretches that are quiet at that time, which is why no area "
            f"exceeds its capacity on this basis - the highest is Gai Avenue at "
            f"{A['mega']['peak_hour_pct']}%. That is a result rather than a ceiling: an "
            "area whose kerb turned over fast enough within the hour would read above "
            "100%, exactly as individual zones do."):
        done.append("why areas stay under 100% explained")
    else:
        skipped.append("why areas stay under 100%")

    # 3. the results paragraph makes the same simultaneity claim
    p = find_maybe(doc, "vehicles stand on the kerb when each area is at its own busiest hour")
    if p is not None and sub_in_place(
            p,
            r"vehicles stand on the kerb when each area is at its own busiest hour",
            "distinct vehicles used the kerb, each area counted at its own busiest hour"):
        done.append("results paragraph corrected")
    else:
        skipped.append("results paragraph")

    doc.save(DOC)
    print("backup:", os.path.basename(BAK))
    for d in done:
        print("  applied:", d)
    for s in skipped:
        print("  SKIPPED:", s)
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
