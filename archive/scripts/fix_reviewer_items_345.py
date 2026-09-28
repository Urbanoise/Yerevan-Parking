# -*- coding: utf-8 -*-
"""Three reconciliations carried out IN PLACE on the 25/08 revisions.

3. Gai Avenue. Output 10 says its kerb parking "is left in place for now"; Output 8
   counts all 132 Gai spaces as removed, and they feed the 1,886 / 1,123 totals. Both
   are right - Output 8 reports the conceptual design as drawn, Output 10 recommends
   departing from it at Gai - but neither document says so, so the two read as a
   contradiction. Stated explicitly in both.

4. Survey size. Both reports say the survey covered "136 survey zones". It did not:
   136 is the number of zones the design REMOVES. The survey covered 208 zones, 203 of
   which carry occupancy data. Corrected in both, and Output 10's "203 surveyed zones"
   is relabelled so 203 and 208 no longer look like rival counts of the same thing.

5. Occupancy denominator. Output 8 gives 61% of 2,878 spaces while Table 8 totals
   2,930. The 52-space difference is five Kentron zones inventoried on the supply side
   but never swept - which is also why Kentron is measured against 534 rather than the
   586 in Table 8, the figure the 12 August review used. Explained where the 61% is
   stated.

Replacements inherit the formatting of the run they land in, so text already accepted
into black stays black. Backups first; every edit is checked before it is applied, so
the script is safe to re-run and reports anything it skipped.
"""
import os
import re
import shutil

from docx import Document

import report_figures as rf

ROOT = os.path.join(rf.ROOT, "Final Presentation")
O8 = os.path.join(ROOT, "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")
O10 = os.path.join(ROOT, "Output 10 - Parking Analysis Report - 25082026 (rev).docx")
SUFFIX = " (pre-items-345).docx"

ZONES_SURVEYED = 208      # distinct survey zones in field-surveys.geojson
ZONES_WITH_OCC = 203      # of those, the ones carrying occupancy data


def sub_in_place(par, pattern, repl):
    """Regex-replace across runs, keeping each touched run's own formatting."""
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
        run.text = head + (repl if first else "") + tail
        first = False
    return True


def edit(doc, anchor, pattern, repl, label, log):
    p = next((x for x in doc.paragraphs if anchor in x.text), None)
    if p is not None and sub_in_place(p, pattern, repl):
        log[0].append(label)
    else:
        log[1].append(label)


def run(path, fn):
    bak = path.replace(".docx", SUFFIX)
    shutil.copyfile(path, bak)
    doc = Document(path)
    log = ([], [])
    fn(doc, log)
    doc.save(path)
    return bak, log


def o8(doc, log):
    # 4. survey size
    edit(doc, "21,186 on-street vehicle sightings",
         r"across 136 survey zones",
         "across %d survey zones" % ZONES_SURVEYED,
         "para 229 - survey size 136 -> %d" % ZONES_SURVEYED, log)

    # 5. occupancy denominator, and with it Kentron 534 vs 586
    edit(doc, "Across the six areas together, 1,756 distinct vehicles",
         r"61% of the 2,878 surveyed spaces\.",
         "61% of the 2,878 spaces in the zones where occupancy was recorded. That is 52 "
         "fewer than the 2,930 spaces in Table 8, because five Kentron zones were "
         "inventoried on the supply side but not swept for occupancy; they are excluded "
         "from every occupancy figure in this chapter, which is why Kentron is measured "
         "against 534 spaces rather than 586.",
         "para 241 - 2,878 vs 2,930 reconciled", log)

    # 3. Gai counted as removed, per the design as drawn
    edit(doc, "displacement can be measured rather than assumed",
         r"or 60% of the supply removed\.",
         "or 60% of the supply removed. These totals follow the conceptual design as "
         "drawn, and so include the 132 spaces at Gai Avenue that the companion Parking "
         "Analysis Report (Output 10) recommends retaining for the time being.",
         "para 286 - Gai counted per design as drawn", log)


def o10(doc, log):
    # 4. survey size, and relabel the 203 so it does not read as a rival total
    edit(doc, "21,186 on-street sightings",
         r"across 136 survey zones",
         "across %d survey zones" % ZONES_SURVEYED,
         "para 152 - survey size 136 -> %d" % ZONES_SURVEYED, log)

    edit(doc, "The commonly adopted occupancy target is 85%",
         r"Of the 203 surveyed zones,",
         "Of the %d zones with occupancy data," % ZONES_WITH_OCC,
         "para 226 - 203 relabelled as zones with occupancy data", log)

    # 3. Gai is a proposed departure from the design, not a change already in it
    edit(doc, "Gai Avenue (Mega Mall) is the one area",
         r"so its kerb parking is left in place for now\.",
         "so this report recommends that its kerb parking be left in place for now and "
         "given a fresh look as the area changes. That is a proposed departure from the "
         "conceptual design rather than a change already made to it: the removal and "
         "displacement totals in this report and in Output 8 follow the design as drawn "
         "and count Gai's 132 spaces as removed.",
         "para 244 - Gai reconciled with the removal totals", log)


def main():
    for name, path, fn in (("Output 8", O8, o8), ("Output 10", O10, o10)):
        bak, (done, skipped) = run(path, fn)
        print("%s  (backup: %s)" % (name, os.path.basename(bak)))
        for d in done:
            print("   applied:", d)
        for s in skipped:
            print("   SKIPPED (already done or wording moved):", s)
        print()


if __name__ == "__main__":
    main()
