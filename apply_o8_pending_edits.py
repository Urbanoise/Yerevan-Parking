# -*- coding: utf-8 -*-
"""The seven outstanding edits to Output 8, applied IN PLACE.

apply_o8_hook_comments.py rebuilds the 24/08 revision from the 12/08 source every time
it runs. That is no longer safe: the saved file now carries hand edits, including red
text turned black where the change has been accepted. Rebuilding would discard all of
it. This script therefore opens the saved document and changes only the seven passages
still outstanding, leaving every other byte alone.

Each edit checks first whether it is still needed, so the script is safe to re-run and
will say plainly what it skipped. Text replacements inherit the colour of the run they
land in rather than forcing red, so a paragraph already accepted into black stays black.

Backup is written alongside before anything is touched.
"""
import os
import re
import shutil

from docx import Document

import docx_edit as dx
import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-pending-edits).docx")

F = rf.survey()
A, ALL = F["areas"], F["all"]
S = rf.supply()

done, skipped = [], []


def find_maybe(doc, needle, style=None):
    for p in doc.paragraphs:
        if needle in p.text and (style is None or p.style.name == style):
            return p
    return None


def sub_in_place(par, pattern, repl):
    """Regex-replace across runs, keeping each touched run's own formatting - so an
    edit inside a paragraph the user has accepted into black stays black."""
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


def edit(label, fn):
    try:
        if fn():
            done.append(label)
        else:
            skipped.append(label)
    except LookupError:
        skipped.append(label)


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)

    # 1. the correction note - the report carries the corrected figures, so the account
    #    of how they were corrected belongs in the reply to the reviewer, not here
    def drop_correction_note():
        p = find_maybe(doc, "Correction of 24 August 2026")
        if p is None:
            return False
        dx.drop(p)
        return True

    # 2. chapter preamble: lead with the aggregate it promises, then the full range
    def preamble():
        p = find_maybe(doc, "The aggregate headlines are")
        if p is None:
            return False
        lo = min(A.values(), key=lambda a: a["peak_hour_pct"])
        hi = max(A.values(), key=lambda a: a["peak_hour_pct"])
        return sub_in_place(
            p,
            r"occupancy at each area's busiest hour reaches \d+% at [^,]+ and \d+% in "
            r"[^,]+, and \d+% across the six areas together",
            f"occupancy at the busiest hour is {ALL['peak_hour_pct']}% across the six "
            f"areas together, ranging from {lo['peak_hour_pct']}% in {lo['label']} to "
            f"{hi['peak_hour_pct']}% at {hi['label']}")

    # 3. the over-100% paragraph: turnover alone, no markings, no capping defence and
    #    no off-street stacking tail
    def over_100():
        p = find_maybe(doc, "A zone reading above 100% is not a data error")
        if p is None:
            return False
        dx.set_text(
            p,
            "A zone reading above 100% is not a data error. Capacity here is the number "
            "of vehicles a length of kerb can hold, and the count is of every distinct "
            "vehicle that used it during the hour rather than of how many stood there at "
            "one moment. Where the kerb turns over, the two diverge: three vehicles "
            "sharing one space over an hour read as 300%, and the busiest zone in the "
            "survey reaches six times its capacity on that basis. The figure is "
            "therefore a measure of how hard a length of kerb is worked across the hour.",
            red=False)
        return True

    # 4. the design identifies which zones go; the survey counted what stood in them
    def attribution():
        p = find_maybe(doc, "Because the survey recorded which zones")
        if p is None:
            return False
        return sub_in_place(
            p,
            r"Because the survey recorded which zones the conceptual design removes, "
            r"displacement can be measured rather than assumed\.",
            "Because the conceptual design identifies which of the surveyed zones lose "
            "their parking, and the survey counted the vehicles standing in those same "
            "zones, displacement can be measured rather than assumed.")

    # 5. conclusions bullet 3, rebuilt on the wording of section 5.2 so the percentages
    #    attach to the spaces removed rather than dangling off the 1,220 retained
    def conclusions_bullet():
        p = find_maybe(doc, "The conceptual corridor designs remove 4,875")
        if p is None:
            return False
        return sub_in_place(
            p,
            r"and retain or re-establish 1,220 - which is \d+% of all on-street spaces "
            r"in the impact area, and \d+% of all parking in it once off-street is "
            r"included\.",
            "and retain or re-establish 1,220. Measured against the impact area, those "
            f"{S['removed']:,} spaces are "
            f"{round(100 * S['removed'] / S['on_street'])}% of the {S['on_street']:,} "
            "on-street spaces within the corridors and their 100-metre influence area, "
            f"and {round(100 * S['removed'] / S['total'])}% of all {S['total']:,} spaces "
            "once off-street is included.")

    # 6. the demand-side conclusions bullet belongs to Output 10
    def drop_demand_bullet():
        p = find_maybe(doc, "A targeted field occupancy survey on six representative areas")
        if p is None:
            return False
        dx.drop(p)
        return True

    edit("correction note removed", drop_correction_note)
    edit("chapter preamble rewritten", preamble)
    edit("over-100% paragraph rewritten", over_100)
    edit("design/survey attribution fixed", attribution)
    edit("conclusions bullet 3 rewritten", conclusions_bullet)
    edit("demand-side conclusions bullet dropped", drop_demand_bullet)

    doc.save(DOC)
    print("backup:", os.path.basename(BAK))
    for d in done:
        print("  applied:", d)
    for s in skipped:
        print("  SKIPPED (already handled or text moved):", s)
    print("saved:", os.path.basename(DOC))


if __name__ == "__main__":
    main()
