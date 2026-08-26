# -*- coding: utf-8 -*-
"""Trim the Gai Avenue residual-risk note to the finding alone, IN PLACE.

The retention recommendation is withdrawn (client position, 25 August 2026) and nothing
replaces it: the measured finding stands on its own, and the 132 spaces removed are
already stated in the displacement chapter and Table 10. This also clears the comma
splice left by the previous pass.

Backup first; the edit is checked before it is applied, so the script is safe to re-run.
"""
import os
import re
import shutil

from docx import Document

import report_figures as rf

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 25082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-gai-trim).docx")

OLD = (r", The corridor design is not adjusted on that account: delivering bus priority "
       r"takes precedence over kerb parking, and the removal totals in this report and in "
       r"Output 8 count all 132 of Gai's spaces as removed\. Gai Avenue is therefore where "
       r"the strongest management response and the closest monitoring after commissioning "
       r"will be needed\.")


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


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)
    p = next((x for x in doc.paragraphs
              if "Gai Avenue (Mega Mall) is the one area" in x.text), None)
    ok = p is not None and sub_in_place(p, OLD, ".")
    doc.save(DOC)
    print("backup:", os.path.basename(BAK))
    print("  %s: Gai note trimmed to the finding" % ("applied" if ok else "SKIPPED"))
    if ok:
        print("\n  now reads: ..." + p.text[-135:])


if __name__ == "__main__":
    main()
