# -*- coding: utf-8 -*-
"""Output 10, October 2026 round: the ADB memo of 7 Oct 2026 on the 30 Sep version.

Builds a new dated copy from the 30 Sep response copy (SEP'26, left untouched as the
record) and applies this round's changes in red:

  * a new Executive Summary (the report never had one);
  * occupancy, stay and displacement figures on the reviewer's basis (half an hour in a
    vehicle's arrival and departure hours, compute_field_survey_metrics.mjs 'walter');
    the pricing argument now rests on the streets that reach the 85% target, since no
    surveyed area does as a whole;
  * Gai Avenue is no longer an uncovered shortfall (90 displaced vehicles, 116 nearby
    spaces), so the two sentences saying it is are removed;
  * Bagratunyats N03-N06 retained: 1,220 -> 1,252 retained, 4,875 -> 4,843 removed.

The September round's red is turned black and its closed comment threads removed.
Every number is read from report_figures.
Usage: python apply_o10_oct_edits.py [--force]
"""
import copy
import os
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

import docx_edit as dx
import report_figures as rf

ROOT = rf.ROOT
SRC = os.path.join(ROOT, "Final Presentation", "SEP'26",
                   "Output 10_Parking Analysis Report_25082026_Logit comments - STS responses.docx")
OUT = os.path.join(ROOT, "Final Presentation", "OCT'26",
                   "Output 10 - Parking Analysis Report 15102026 (rev).docx")


def _guard_existing():
    if os.path.exists(OUT) and "--force" not in sys.argv:
        sys.exit(f"refusing to overwrite {OUT} (it may carry hand edits); use --force")


def n(x):
    return f"{round(x):,}"


def new_para(after_el, text, style, unnumbered=False):
    """A fresh paragraph (no inherited pPr) after `after_el`, red text."""
    p = OxmlElement("w:p")
    ppr = OxmlElement("w:pPr")
    ps = OxmlElement("w:pStyle")
    ps.set(qn("w:val"), style)
    ppr.append(ps)
    if unnumbered:
        num = OxmlElement("w:numPr")
        for tag, val in (("w:ilvl", "0"), ("w:numId", "0")):
            e = OxmlElement(tag)
            e.set(qn("w:val"), val)
            num.append(e)
        ppr.append(num)
    p.append(ppr)
    after_el.addnext(p)
    par = Paragraph(p, None)
    if text:
        run = par.add_run(text)
        run.font.color.rgb = dx.RED
    return par


def main():
    _guard_existing()
    s, f = rf.supply(), rf.survey()
    A, al = f["areas"], f["all"]
    c1, c2 = s["corridors"]["Corridor 01"], s["corridors"]["Corridor 02"]
    k, km, ga, gn, sh, ma = (A[x] for x in ("kentron", "komitas", "mega", "garegin",
                                             "shiraz", "malatia"))
    st = al["stay"]
    kz = 53
    k85 = round(k["over85_pct"] * kz / 100)            # Kentron zones at or above 85%
    on_pct = s["removed"] * 100 / s["on_street"]
    all_pct = s["removed"] * 100 / s["total"]

    doc = Document(SRC)
    print("September red recoloured:", dx.accept_red(doc), "| comments removed:",
          dx.strip_comments(doc))

    # ---- Executive Summary, before chapter 1 ------------------------------------------
    intro = next(p for p in doc.paragraphs
                 if p.text.strip() == "Introduction" and p.style.name == "Heading 1")
    pagebreak = intro._p.getprevious()
    assert pagebreak.xpath(".//w:br[@w:type='page']"), "expected a page break before ch. 1"
    cur = new_para(pagebreak, "Executive Summary", "Heading1", unnumbered=True)
    for text in [
        "This report assesses how the bus priority corridors on Corridors 1 and 2 affect "
        "parking in Yerevan and sets out how the displaced demand should be managed. It "
        "complements the Traffic and Parking Surveys and Analysis Report (Output 8), which "
        "holds the full survey evidence.",

        f"Yerevan's corridor kerb is mostly free and weakly organised. Of the "
        f"{n(s['on_corridor'])} on-street spaces on the corridors, "
        f"{s['zones']['free'] * 100 / s['on_corridor']:.0f}% are free, only "
        f"{s['signage_yes'] * 100 / s['on_corridor']:.0f}% carry signage and "
        f"{s['marking_yes'] * 100 / s['on_corridor']:.0f}% marking; the paid system run by "
        f"Parking City Service covers {n(s['zones']['zone_a'] + s['zones']['zone_b'])} of them "
        f"in Zones A and B. The 2024 tariff reform raised charges sharply and is still "
        f"being challenged in the courts.",

        f"The v2 conceptual design removes {n(s['removed'])} of these spaces and retains or "
        f"re-establishes {n(s['retained'])} ({n(c1['retained'])} on Corridor 1, "
        f"{n(c2['retained'])} on Corridor 2). Within the corridors' 100-metre impact area the "
        f"removal is {on_pct:.0f}% of on-street parking and {all_pct:.0f}% of all parking "
        f"once off-street spaces are included.",

        f"A licence-plate survey of six representative areas shows a kerb that is busy in "
        f"places but not full across whole areas. At their busiest hour the six areas run "
        f"at {al['peak_hour_pct']}% of capacity, from {ma['peak_hour_pct']}% in "
        f"Malatia-Sebastia to {k['peak_hour_pct']}% in Kentron and {ga['peak_hour_pct']}% "
        f"at Gai Avenue. The pressure sits on particular streets: {k85} of Kentron's {kz} "
        f"survey zones reach the 85% occupancy target at their busiest hour. Stays are short "
        f"- {st['shortPct']}% last an hour or less - and each space turns over "
        f"{al['turnover_lo']} to {al['turnover_hi']} times a day. In the surveyed areas "
        f"{n(al['displaced'])} vehicles were parked at the busiest hour in the "
        f"{n(al['removed'])} spaces to be removed; surviving nearby kerb space can take "
        f"{al['absorbed_onstreet_pct']}% of them, and the rest depends on off-street capacity "
        f"that is largely closed residential courtyards today.",

        "The corridors themselves are the primary mitigation: faster and more reliable buses "
        "reduce the number of cars that need to park. Around them the report recommends a "
        "layered package, scaled to three sensitivity zones: extending the paid red/blue-line "
        "system onto side streets within 100 metres of the corridors; charged resident "
        "permits limited to one per household; delineating and marking the free kerb that "
        "remains; adjusting charges towards the 85% occupancy target on the streets that "
        "reach it; and withdrawing the flat annual permit in favour of hourly pricing. "
        "Visitor caps are held as a targeted contingency, and new garage capacity in the "
        "centre is not recommended.",

        "The measures should be in place before or together with the removal of corridor "
        "parking. Overall responsibility rests with the Transport Department of Yerevan "
        "Municipality, with components delivered through the project remaining with the PIU.",
    ]:
        cur = new_para(cur._p, text, "Normal")
    cur._p.addnext(copy.deepcopy(pagebreak))

    # ---- chapter 4: impacts ------------------------------------------------------------
    p = dx.find(doc, "That is why the design retains or re-establishes 1,220 spaces")
    dx.sub(p, r"retains or re-establishes 1,220 spaces \(20% of the on-corridor supply\)",
           f"retains or re-establishes {n(s['retained'])} spaces ({s['retained_pct']:.0f}% of "
           f"the on-corridor supply)")
    dx.sub(p, r"1,220 in total, 869 on Corridor 1 and 351 on Corridor 2",
           f"{n(s['retained'])} in total, {n(c1['retained'])} on Corridor 1 and "
           f"{n(c2['retained'])} on Corridor 2")
    dx.sub(dx.find(doc, "Corridor 1 as a whole retains 869 of its 2,349"),
           r"retains 869 of its 2,349", f"retains {n(c1['retained'])} of its {n(c1['existing'])}")
    dx.sub(dx.find(doc, "Malatia-Sebastia in fact records the lowest daytime kerb pressure"),
           r"\(35% at its busiest hour\)", f"({ma['peak_hour_pct']}% at its busiest hour)")

    dx.set_text(dx.find(doc, "The field survey confirms and quantifies these differences."),
        f"The field survey confirms and quantifies these differences. The Kentron commercial "
        f"core runs at {k['peak_hour_pct']}% occupancy at its busiest hour, but {k85} of its "
        f"{kz} zones reach the 85% target and {k['over_capacity']} read above 100% "
        f"at their own peak, and it is short-stay dominated (about "
        f"{k['stay']['shortPct']}% of vehicles stay one hour or less). The Malatia-Sebastia "
        f"residential segment shows the lowest daytime pressure ({ma['peak_hour_pct']}% at its "
        f"busiest hour) and a marked long-stay / overnight share ({ma['stay']['alldayPct']}% of "
        f"stays exceed eight hours), consistent with residential storage rather than turnover. "
        f"Turnover across the surveyed areas runs at {al['turnover_lo']} to "
        f"{al['turnover_hi']} vehicles per space per day.")

    # ---- chapter 5: displacement and measures ----------------------------------------
    dx.set_text(dx.find(doc, "Measured recalibration (field survey)."),
        f"Measured recalibration (field survey). The survey tests these a-priori labels "
        f"against behaviour. Across the surveyed areas the design removes "
        f"{n(al['removed'])} spaces, in which an average of {n(al['displaced'])} vehicles "
        f"were parked at each area's busiest hour, so measured displacement falls well below "
        f"the supply removed. Beneath that aggregate the areas differ. Kentron is confirmed "
        f"high-sensitivity: {k['peak_hour_pct']}% at its busiest hour overall, but {k85} of "
        f"its {kz} zones reach the 85% target and only {k['absorbed_onstreet_pct']}% of its "
        f"displaced demand can be absorbed on nearby kerb. Komitas, previously medium, is "
        f"reclassified as high-sensitivity throughout this report: at {km['peak_hour_pct']}% "
        f"at its busiest hour it is less full than Kentron, but none of its displaced demand "
        f"can be absorbed on nearby kerb. Shiraz/Hasratyan and Malatia-Sebastia behave as "
        f"genuinely lower-sensitivity, at {sh['peak_hour_pct']}% and {ma['peak_hour_pct']}% "
        f"at their busiest hours. Gai Avenue, at {ga['peak_hour_pct']}%, is the fullest of "
        f"the six.", keep_lead_bold=True)

    dx.sub(dx.find(doc, "Field-survey verdict: re-scope, do not remove."),
           r"about 63% of vehicles already stay one hour or less, all-day parking is only around 6%",
           f"about {st['shortPct']}% of vehicles already stay one hour or less, all-day parking "
           f"is only around {st['alldayPct']}%")

    dx.set_text(dx.find(doc, "Adjusting the existing parking charges to the level at which"),
        f"Adjusting the existing parking charges to the level at which the kerb actually "
        f"clears. The commonly adopted occupancy target is 85%, at which roughly one space in "
        f"seven is free and an arriving driver can find it without cruising. Across whole "
        f"areas measured occupancy stays below that target, but the pressure is concentrated "
        f"on particular streets. Of the 203 zones with occupancy data, {al['over85_pct']}% are "
        f"at or above the 85% target at their busiest hour and {al['over_capacity']} read "
        f"above 100%. In Kentron, which lies entirely within Zone A, "
        f"{k85} of {kz} zones reach the target and {k['over_capacity']} read above 100%, "
        f"although the area as a whole reaches {k['peak_hour_pct']}% at "
        f"{k['peak_hour']:02d}:00. A price that leaves those streets that full is below the "
        f"market-clearing price there.")
    lo = min(ma["peak_hour_pct"], sh["peak_hour_pct"], gn["peak_hour_pct"])
    hi = max(ma["peak_hour_pct"], sh["peak_hour_pct"], gn["peak_hour_pct"])
    dx.sub(dx.find(doc, "This is not a general tariff increase"),
           r"runs from 35% to 63%", f"runs from {lo}% to {hi}%")

    dx.sub(dx.find(doc, "replace part of the removed kerb space by building new parking"),
           r", and at a single high-demand destination such as Gai Avenue \(Mega Mall\), where "
           r"even best-case nearby capacity does not cover the measured displacement, it "
           r"would answer a specific shortfall\.",
           ", and at a single high-demand destination it could answer a specific local "
           "shortfall.")
    dx.sub(dx.find(doc, "Survey-specific caveats."),
           r" One residual risk is specific: Gai Avenue \(Mega Mall\) is the one area even "
           r"best-case capacity can't cover\.", "")

    # occupancy method, one sentence where the survey is introduced
    dx.sub(dx.find(doc, "plus one off-street facility per area."),
           r"plus one off-street facility per area\.",
           "plus one off-street facility per area. Occupancy counts each vehicle for half an "
           "hour in the hours it arrives and leaves and for a full hour in between, since the "
           "hourly rounds record which vehicles were present but not for how long.")

    # ---- Conclusions ------------------------------------------------------------------------
    dx.set_text(dx.find(doc, "Parking loss is substantial and inherent to the design."),
        f"Parking loss is substantial and inherent to the design. Design removes "
        f"{n(s['removed'])} of the {n(s['on_corridor'])} on-corridor on-street spaces on "
        f"Corridors 1 and 2, retaining {n(s['retained'])}. Measured against the impact area, "
        f"those {n(s['removed'])} spaces removed are {on_pct:.0f}% of all on-street parking "
        f"within it, and {all_pct:.0f}% of all parking once off-street is included.")
    dx.set_text(dx.find(doc, "Impacts are highly differentiated by zone."),
        f"Impacts are highly differentiated by zone. The Kentron CBD and Komitas Avenue face "
        f"the highest pressure: {k85} of Kentron's {kz} surveyed zones reach the 85% "
        f"occupancy target at their busiest hour, and neither area can absorb much of its "
        f"displaced demand on nearby kerb ({k['absorbed_onstreet_pct']}% and "
        f"{km['absorbed_onstreet_pct']}%). Mid-corridor arterials face moderate pressure; "
        f"outer residential segments require lighter-touch reorganisation.")

    for needle in ("4,875", "1,220", "1,123", "Mega Mall", "89%", "99%", "83%", "used a zone "
                   "during the hour", "63% of"):
        hits = [p.text[:90] for p in dx.find_all(doc, needle)]
        if hits:
            print(f"CHECK {needle!r}:", hits)

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
