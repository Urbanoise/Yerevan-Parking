# -*- coding: utf-8 -*-
"""Output 10 - September 2026 round, part 2: define the survey "zone" at first use.

Terminology (user, 29 Sep 2026): a "zone" is a segment of street - the unit the web
app also uses - and the six survey locations are "areas". The reviewers read "zone"
as a whole area (Logit C61), so the term is defined once where the 208 total is
first stated, ahead of the per-area breakdown apply_o10_sep_comments.py added.

(Supersedes the withdrawn apply_o10_sep_zones.py, which had removed the term.)

Run after apply_o10_sep_comments.py:
      python apply_o10_sep_zone_definition.py            (dry run, saves nothing)
      python apply_o10_sep_zone_definition.py --apply
"""
import shutil
import sys

from docx import Document

from apply_o10_sep_comments import DOC, insert_red
from docx_edit import find

BACKUP = DOC.replace(".docx", " (before zone definition).docx")

DEFINITION = (" - short segments of street, typically one block face, each checked on "
              "every hourly round - in the six areas")


def main(apply):
    doc = Document(DOC)
    body = "\n".join(p.text for p in doc.paragraphs)
    if "(Kentron 58, of which the 53 swept" not in body:
        raise SystemExit("run apply_o10_sep_comments.py first")
    if "short segments of street" in body:
        raise SystemExit("already applied - refusing to apply twice")

    par = find(doc, "10,135 distinct vehicles across 208 survey zones")
    insert_red(par, "208 survey zones", DEFINITION)
    assert "208 survey zones - short segments of street" in par.text
    assert "in the six areas (Kentron 58" in par.text

    if apply:
        shutil.copyfile(DOC, BACKUP)
        doc.save(DOC)
        print("saved", DOC, "\nbackup", BACKUP)
    else:
        print("dry run OK - nothing saved")


if __name__ == "__main__":
    main("--apply" in sys.argv)
