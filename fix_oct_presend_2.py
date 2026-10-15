# -*- coding: utf-8 -*-
"""OCT'26 copies of Output 8 / Output 10: second pre-send pass (15 Oct 2026), in black.

  * O8: Corridor 2 off-street 3,692 -> 3,722 and total 8,679 -> 8,709 (Palace lot
    32 -> 62 on 30 Sep; the corridor split now adds up to the 6,762 quoted elsewhere).
  * O8: the methodology paragraph no longer says demand came from ANPR data (the
    report says ANPR is not relied on); it names the field occupancy survey instead.
  * O8: ToR reference corrected to paragraphs 61 and 65 (surveys and parking analysis).
  * O10: the 85% paragraph names the three low-pressure areas and separates the
    pricing rule from the paid-zone extension recommended at Garegin Nzhdeh.

Usage: python fix_oct_presend_2.py
"""
from docx import Document

import docx_edit as dx
import report_figures as rf
from fix_oct_presend import O8, O10, replace_plain


def main():
    c2 = rf.supply()["corridors"]["Corridor 02"]
    assert c2["off_street"] == 3722, c2["off_street"]
    total = 3746 + c2["cross_street"] + c2["off_street"]
    assert total == 8709, total

    doc = Document(O8)
    p = dx.find(doc, "and 3,692 off-street spaces in 156 facilities")
    replace_plain(p, "3,692", f"{c2['off_street']:,}")
    replace_plain(p, "8,679", f"{total:,}")
    replace_plain(dx.find(doc, "supplemented by targeted demand analysis using municipal ANPR"),
                  "supplemented by targeted demand analysis using municipal ANPR data where available",
                  "supplemented by a targeted field occupancy survey")
    replace_plain(dx.find(doc, "The ToR (Task 3, paragraphs 59"),
                  "paragraphs 59–63", "paragraphs 61 and 65")
    doc.save(O8)
    print("saved", O8)

    doc = Document(O10)
    replace_plain(dx.find(doc, "the same rule implies no charge at all"),
                  "in the outer areas, where occupancy at the busiest hour runs from 18% to 37%, "
                  "the same rule implies no charge at all for the time being, and organising the "
                  "free parking is the appropriate measure there instead.",
                  "in Malatia-Sebastia, Shiraz/Hasratyan and Garegin Nzhdeh, where occupancy at "
                  "the busiest hour runs from 18% to 37%, the same rule gives no reason to raise "
                  "charges. Where paid zones are extended there, the purpose is to control "
                  "spillover from the corridor rather than to clear a full kerb, and in the "
                  "lower-pressure areas organising the free parking comes first.")
    doc.save(O10)
    print("saved", O10)


if __name__ == "__main__":
    main()
