# -*- coding: utf-8 -*-
"""Output 10 - September 2026 round: the Logit review comments of 24 Sep 2026.

Edits the saved 28092026 file IN PLACE (the user may already have touched it), so
nothing here rebuilds the document. New text is red; the reviewer's own untracked
edits are adopted in red as well, except the "is is" typo fix, which is fixed
without colour so a whole bullet does not turn red for one word.

  C57  caveat: retained-space figures come from the v2 design and will be updated
       once the design (Output 6) is final - caveat only, no reconciliation
  C61  Kentron's "53 zones" is 53 of 58, the five unswept excluded; Komitas is
       genuinely 53. Per-area zone counts added where the 208 total is stated
  C85  tariff rates are outside scope and would need PCS payment data
  C86  pros and cons of adding downtown parking capacity (not recommended)
  C90  PIU leads the package within its responsibility for the project
  +    reviewer's rewrite of the "drivers' mindset" paragraph, and "is is"

Run:  python apply_o10_sep_comments.py            (dry run, saves nothing)
      python apply_o10_sep_comments.py --apply
"""
import copy
import shutil
import sys

sys.path.insert(0, "C:/Users/user/Yerevan-Parking")

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from docx_edit import RED, find

DOC = "C:/Users/user/Yerevan-Parking/Final Presentation/SEP'26/Output 10 - Parking Analysis Report - 28092026.docx"
BACKUP = DOC.replace(".docx", " (before sep comments).docx")


# ---------------------------------------------------------------------------
# run-level helpers: colour only the words that change, not the whole paragraph
# ---------------------------------------------------------------------------
def _run_with(par, anchor):
    for r in par.runs:
        if anchor in r.text:
            return r
    raise LookupError(f"anchor not inside a single run: {anchor!r} in {par.text[:60]!r}")


def _clone_run_after(run, text, red):
    new = copy.deepcopy(run._r)
    for t in new.findall(qn("w:t")):
        new.remove(t)
    run._r.addnext(new)
    out = Run(new, run._parent)
    out.text = text
    if red:
        out.font.color.rgb = RED
    return out


def insert_red(par, anchor, text):
    """Insert red `text` immediately after `anchor`. The anchor may straddle runs:
    only the run holding its last character is split."""
    pos = par.text.find(anchor)
    if pos < 0:
        raise LookupError(f"anchor not found: {anchor!r} in {par.text[:60]!r}")
    end, start = pos + len(anchor), 0
    for run in par.runs:
        if start < end <= start + len(run.text):
            break
        start += len(run.text)
    else:
        raise LookupError(f"could not map anchor to a run: {anchor!r}")
    local = end - start
    head, tail = run.text[:local], run.text[local:]
    run.text = head
    added = _clone_run_after(run, text, red=True)
    if tail:
        rest = _clone_run_after(added, tail, red=False)
        rest.font.color.rgb = run.font.color.rgb
    return added


def delete_plain(par, needle, offset, n):
    """Delete `n` characters starting `offset` into the first `needle`, across run
    boundaries, without recolouring anything (typo fixes)."""
    pos = par.text.find(needle)
    if pos < 0:
        raise LookupError(f"not found: {needle!r}")
    lo, hi, start = pos + offset, pos + offset + n, 0
    for run in par.runs:
        t = run.text
        a, b = max(lo - start, 0), min(hi - start, len(t))
        if a < b:
            run.text = t[:a] + t[b:]
        start += len(t)


def append_red(par, text):
    return _clone_run_after(par.runs[-1], text, red=True)


def rewrite_red(par, text):
    """Whole-paragraph rewrite in red, keeping the first run's formatting."""
    first = par.runs[0]
    for r in par.runs[1:]:
        r._r.getparent().remove(r._r)
    first.text = text
    first.font.color.rgb = RED


def clone_para_after(anchor, model, text):
    """New paragraph after `anchor`, formatted like `model` (paragraph + first run)."""
    new = copy.deepcopy(model._p)
    for extra in new.findall(qn("w:r"))[1:]:
        new.remove(extra)
    for child in list(new):
        if child.tag in (qn("w:bookmarkStart"), qn("w:bookmarkEnd"), qn("w:hyperlink"),
                         qn("w:commentRangeStart"), qn("w:commentRangeEnd")):
            new.remove(child)
    anchor._p.addnext(new)
    p = Paragraph(new, anchor._parent)
    rewrite_red(p, text)
    return p


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------
C57_CAVEAT = (
    " These retained-space figures - 1,220 in total, 869 on Corridor 1 and 351 on "
    "Corridor 2 - are taken from the v2 conceptual design and are indicative. The "
    "corridor design is still being developed, and each iteration changes where "
    "parking can be kept; figures reported elsewhere in the project, including in "
    "Output 6, may differ where they reflect a different design iteration."
)

# Superseded on 29 Sep by apply_o10_sep_kentron53.py (Kentron 53, survey 203 zones);
# kept as first applied so the scripts replay in order.
C61_ZONES = (
    " (Kentron 58, of which the 53 swept for occupancy are the basis of every Kentron "
    "occupancy figure in this report; Komitas 53; Shiraz/Hasratyan 34; Garegin "
    "Nzhdeh 31; Malatia-Sebastia 22; Gai Avenue 10)"
)

REVIEWER_231 = (
    "86% of parking spaces on the corridors are unmarked, and 80% are unsigned. They "
    "are free, but they are not organised. Physical delineation is expected to "
    "influence driver behaviour directly: marked bays discourage the informal "
    "positioning that occurs on unmarked kerb, so structuring the existing supply "
    "should improve order even before any pricing intervention is introduced."
)

C85_TARIFF = (
    "Setting tariff rates is outside the scope of this assignment, and this report "
    "therefore proposes no figure for Zone A or Zone B. Calibrating a rate would in any "
    "case require Parking City Service's payment records: hourly payment sessions by "
    "zone and time of day, annual and other period-permit sales, and the notices issued "
    "for failure to pay. That data was not made available to this study. With it, the "
    "charge can be set and adjusted for each tariff zone against the 85% target."
)

C86_TITLE = "Adding parking capacity in the centre"
C86_BODY = [
    "A further option, raised in review, is to replace part of the removed kerb space "
    "by building new parking capacity in the centre, as multi-storey or underground "
    "garages. It has real advantages. It would give short-stay visitors and deliveries "
    "in the commercial core an alternative close to their destinations, it would take "
    "vehicles off footways where the kerb can no longer hold them, and at a single "
    "high-demand destination such as Gai Avenue (Mega Mall), where even best-case "
    "nearby capacity does not cover the measured displacement, it would answer a "
    "specific shortfall.",
    "The disadvantages are more fundamental. Structured parking is expensive per "
    "space, in land as well as construction, and in the centre it competes with "
    "higher-value uses of the same sites. New capacity in the core also attracts "
    "additional car trips into the area the bus corridors are meant to serve, working "
    "against the mode shift that is the primary mitigation. And the field survey shows "
    "the central kerb is short-stay dominated and turning over quickly, so the pressure "
    "there is better addressed by pricing and managing the existing supply than by "
    "adding to it. Adding downtown capacity is therefore not part of the recommended "
    "package. Where a new development or a specific destination can demonstrate a "
    "shortfall that management cannot close, capacity can be assessed case by case, "
    "preferably privately provided and priced at or above the on-street tariff so that "
    "it does not undercut the kerb strategy.",
]

C90_LEAD = (
    "Overall responsibility for implementing the package should rest with the Transport "
    "Department of Yerevan Municipality, which the Institutional Assessment (Output 28) "
    "identifies as the municipality's policy-making and oversight body for urban "
    "transport, including parking. Components delivered through the project itself "
    "remain with the PIU, as set out in the responsibility matrix of the Institutional "
    "and Capacity Building Roadmap (Output 29). Each measure is delivered by the body "
    "that holds the relevant powers: Parking City Service, the Police and other "
    "relevant agencies."
)


def main(apply):
    doc = Document(DOC)
    if "Output 6, may differ" in "\n".join(p.text for p in doc.paragraphs):
        raise SystemExit("already applied - refusing to apply twice")

    # C57 - design-iteration caveat on the retained figures
    append_red(find(doc, "That is why the design retains or re-establishes 1,220 spaces"),
               C57_CAVEAT)

    # C61 - per-area zone counts where the 208 total is stated; Kentron's 53 is "surveyed"
    insert_red(find(doc, "10,135 distinct vehicles across 208 survey zones"),
               "208 survey zones", C61_ZONES)
    for needle, anchor in (("with 42 of its 53 zones over capacity at their own peak", "42 of its 53"),
                           ("with 42 of its 53 zones over capacity. Komitas", "42 of its 53"),
                           ("42 of 53 zones exceed capacity", "42 of 53")):
        insert_red(find(doc, needle), anchor, " surveyed")

    # reviewer's untracked edits
    rewrite_red(find(doc, "86% of parking spaces on the corridors are unmarked"), REVIEWER_231)
    typo = find(doc, "Yerevan's flat 5,000 AMD fine is is modest")
    delete_plain(typo, "fine is is", len("fine is "), len("is "))
    assert "fine is modest" in typo.text, typo.text

    # C85 - tariff rates out of scope; data that would be needed
    outer = find(doc, "This is not a general tariff increase")
    clone_para_after(outer, outer, C85_TARIFF)

    # C86 - adding downtown capacity, before "Taken together"
    taken = find(doc, "Taken together, these measures form a layered mitigation package")
    last_body = find(doc, "Neither this report nor the surveys undertaken establish the scale")
    title_model = find(doc, "Remove derelict and long-term abandoned vehicles")
    body_model = find(doc, "A kerb-management framework should include a route")
    cur = clone_para_after(last_body, title_model, C86_TITLE)
    for text in C86_BODY:
        cur = clone_para_after(cur, body_model, text)
    if cur._p.getnext() is not taken._p:
        print("note: C86 block is not directly followed by 'Taken together' (spacer paragraph?)")

    # C90 - lead agency, after the sequencing paragraph
    seq = find(doc, "This sequencing is a practical requirement")
    clone_para_after(seq, seq, C90_LEAD)

    if apply:
        shutil.copyfile(DOC, BACKUP)
        doc.save(DOC)
        print("saved", DOC, "\nbackup", BACKUP)
    else:
        print("dry run OK - every anchor found; nothing saved")


if __name__ == "__main__":
    main("--apply" in sys.argv)
