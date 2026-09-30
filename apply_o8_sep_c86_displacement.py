# -*- coding: utf-8 -*-
"""Output 8 - Logit comments, Sep 2026: displacement paragraph, second rewrite (C86).

Lucas asked why the text uses 1,123 vehicles "instead of 1,431". The user (30 Sep)
reads 1,431 as a slip for 1,886, the spaces removed, so the question is really
"why is displacement smaller than the number of spaces removed?". The paragraph under
"Measured Displacement by Area" is rewritten around that: displacement counts cars,
not spaces. The 1,756 step from the first rewrite (apply_o8_sep_comments.py) is dropped.
The reply under the comment is updated to match.

Figures: 1,886 removed, 1,123 displaced at the busiest hour (areaStats / Table 11),
1,886 - 1,123 = 763 removed spaces empty at that hour.

Run:  python apply_o8_sep_c86_displacement.py            (dry run)
      python apply_o8_sep_c86_displacement.py --apply
"""
import sys

from docx import Document

from apply_o8_sep_comments import DST, rewrite_keep_comments
from apply_o8_sep_zone_table import set_reply
from docx_edit import find

REMOVED, DISPLACED = 1886, 1123

TEXT = (
    f"The conceptual design removes {REMOVED:,} spaces in the six surveyed areas, but "
    "displacement counts cars, not spaces: a removed space displaces a car only if one is "
    f"parked there. At the busiest hour for the removed zones in each area, {DISPLACED:,} "
    "vehicles were parked in them. That is the displaced demand the surrounding streets "
    f"and off-street facilities must absorb. The other {REMOVED - DISPLACED:,} removed "
    "spaces were empty at that hour, so their loss reduces supply but displaces no one. "
    "This does not mean that about 40% of the removed spaces are never used, only that "
    "they are not all occupied in the same hour."
)
REPLY = (f"Rewritten: displacement counts cars, not spaces. The design removes {REMOVED:,} "
         f"spaces, but only the {DISPLACED:,} cars parked in them at the busiest hour are "
         "displaced.")


def main(apply):
    doc = Document(DST)
    par = find(doc, "The conceptual design identifies which surveyed zones lose their parking")
    rewrite_keep_comments(par, TEXT)
    print(par.text)
    if not apply:
        print("dry run OK - nothing saved")
        return
    doc.save(DST)
    set_reply(DST, "Lucas Melo", "The text is not clear why you use 1,123", REPLY)
    print("saved", DST)


if __name__ == "__main__":
    main("--apply" in sys.argv)
