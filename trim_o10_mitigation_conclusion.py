"""Replace the 5.6 "Conclusion of the mitigation framework" subsection with a single
short closing paragraph at the end of the measures section.

Reviewer asked only for "some sort of conclusion" to the measures section; the full
subsection restated the sequencing point and the Gai Avenue residual that 5.7 Phasing
and 5.8 Limitations already carry. This drops the subsection and closes 5.5 with one
red paragraph instead, with no figures or percentages in it and no reference
to the residential-yard measure and none to Gai Avenue.

Edits the 13/08 revision in place (it carries hand edits made after
apply_o10_reviewer_comments.py ran, so it is not regenerated).
"""
import shutil

from docx import Document

import docx_edit as dx
import report_figures as rf
import os

DOC = os.path.join(rf.ROOT, "Final Presentation",
                   "Output 10 - Parking Analysis Report - 13082026 (rev).docx")
BAK = DOC.replace(".docx", " (pre-5.6-trim).docx")

CLOSER = (
    "Applying that package well matters as much as adopting it. The measures reinforce "
    "one another and are meant to be used with judgement rather than uniformly, so their "
    "effect depends on how they are sequenced, communicated and adjusted to local "
    "conditions. Kerb management is a continuing process rather than a one-off "
    "intervention, and the arrangements set out above should be kept under review and "
    "refined in the light of experience as the corridors are delivered."
)


def main():
    shutil.copyfile(DOC, BAK)
    doc = Document(DOC)

    head = dx.find_styled(doc, "Conclusion of the mitigation framework", "Heading 2")
    last = dx.find(doc, "The one area where the framework does not resolve the problem")
    dx.drop_range(head, last)

    anchor = dx.find(doc, "Taken together, these measures form a layered mitigation package")
    dx.insert_after(anchor, CLOSER, red=True)

    doc.save(DOC)
    print("backup:", BAK)


if __name__ == "__main__":
    main()
