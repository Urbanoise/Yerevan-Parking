# -*- coding: utf-8 -*-
"""Withdraw the Gai Avenue kerb-retention recommendation, IN PLACE.

Client position, 25 August 2026: kerb parking at Gai Avenue cannot be kept. Delivering
the bus priority corridor outweighs any number of parking spaces, so the design is not
adjusted at Gai and all 132 of its spaces go.

Two consequences:

  * Output 10's residual-risk note recommended leaving the Gai kerb in place. The
    finding behind it stands - Gai is the one area where even best-case nearby capacity
    does not cover the displaced demand - so the limitation is kept and only the
    recommendation is withdrawn, replaced by the priority principle and a monitoring
    commitment.
  * Output 8's displacement totals needed a caveat only because Output 10 proposed a
    departure from the design. With the recommendation gone there is no departure, so
    that clause is removed and the sentence returns to its earlier form.

Note the same position appears in the STS reply comments on the 12 August reviewer memo
("the one place we stop short of removal is Gai Avenue"). That document is NOT touched
here - it is correspondence, not a draft, and may already have gone out.

Replacements inherit the formatting of the run they land in. Backups first; each edit is
checked before it is applied, so the script is safe to re-run.
"""
import os
import re
import shutil

from docx import Document

import report_figures as rf

ROOT = os.path.join(rf.ROOT, "Final Presentation")
O8 = os.path.join(ROOT, "Output 8 - Parking Surveys and Analysis Report 25082026 (rev).docx")
O10 = os.path.join(ROOT, "Output 10 - Parking Analysis Report - 25082026 (rev).docx")
SUFFIX = " (pre-gai-withdrawal).docx"


def sub_in_place(par, pattern, repl):
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


def apply(path, anchor, pattern, repl, label):
    bak = path.replace(".docx", SUFFIX)
    shutil.copyfile(path, bak)
    doc = Document(path)
    p = next((x for x in doc.paragraphs if anchor in x.text), None)
    ok = p is not None and sub_in_place(p, pattern, repl)
    doc.save(path)
    print("%s  (backup: %s)" % (os.path.basename(path)[:28], os.path.basename(bak)))
    print("   %s: %s" % ("applied" if ok else "SKIPPED (wording moved)", label))
    return ok


def main():
    # Output 10 - keep the limitation, drop the recommendation
    apply(
        O10,
        "Gai Avenue (Mega Mall) is the one area",
        r"so this report recommends that its kerb parking be left in place for now and "
        r"given a fresh look as the area changes\. That is a proposed departure from the "
        r"conceptual design rather than a change already made to it: the removal and "
        r"displacement totals in this report and in Output 8 follow the design as drawn "
        r"and count Gai's 132 spaces as removed\.",
        "The corridor design is not adjusted on that account: delivering bus priority "
        "takes precedence over kerb parking, and the removal totals in this report and "
        "in Output 8 count all 132 of Gai's spaces as removed. Gai Avenue is therefore "
        "where the strongest management response and the closest monitoring after "
        "commissioning will be needed.",
        "Gai retention recommendation withdrawn; limitation and monitoring kept")

    # Output 8 - no departure from the design, so no caveat is needed
    apply(
        O8,
        "displacement can be measured rather than assumed",
        r" These totals follow the conceptual design as drawn, and so include the 132 "
        r"spaces at Gai Avenue that the companion Parking Analysis Report \(Output 10\) "
        r"recommends retaining for the time being\.",
        "",
        "Gai caveat removed - totals need no qualification now")


if __name__ == "__main__":
    main()
