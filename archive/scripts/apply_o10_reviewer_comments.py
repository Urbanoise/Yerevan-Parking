# -*- coding: utf-8 -*-
"""Apply the reviewer's Output 10 comments and refresh every figure onto the
Corridors 1+2 / v2-conceptual-design basis.

Source : Final Presentation/Output 10 - Parking Analysis Report - 23062026 (rev).docx
Output : Final Presentation/Output 10 - Parking Analysis Report - 30072026 (rev).docx
         (the 23062026 file is left untouched)

The 21 comments on the "Parking Policy" sheet, and how each is addressed.

NOTE ON SECTION NUMBERS. The reviewer's numbers run one chapter higher than what Word
renders from this file: their "Chapter 5" (parking impacts) is the rendered Chapter 4,
their "6.5" (mitigation measures) is the rendered 5.5, and their "Section 6.3" is 5.3.
Comments are therefore matched to content, never to a number. The document's own
"see Section 5.5" cross-reference is correct and is left alone. The hand-typed
"7.1 / 7.2" labels in the Conclusions ARE removed, because those headings now carry
real list numbering (fix_heading_numbering) and Word numbers them itself.

  p.13   patrol vehicles vs pole-mounted ANPR      -> enforcement description reconciled
  p.14   occupancy detail promised in O8, absent   -> O8 now carries a full chapter;
                                                      §4.3 rewritten to past tense
  p.14   Ch5 par 1 still blames median alignment   -> rewritten (as in O8)
  p.15   retained figures need a caveat            -> refreshed + basis caveat
  p.15   §5.3 "no parking in the housing estates"  -> rewritten
  p.15   §5.3 overstates Arshakunyats parking loss -> softened, with the retained count
  p.16   "must incorporate loading bays"           -> answered: the designs do NOT
                                                    include them; written as a
                                                    recommendation to the design team
  §6.3   annual passes: what share? eliminate      -> promoted to a firm measure
  p.18   park and ride is recommended              -> every reference removed
  §6.5   needs a conclusion                        -> new closing subsection
  §6.5   no mention of pricing to 85% occupancy    -> new measure
  §6.5   annual-pass removal absent from 6.5       -> new measure
  §6.5   derelict vehicles                         -> new measure, with a measured proxy
  p.19   blames Soviet estates for having no parking -> value judgement removed
  p.19   "committed pre-condition" unexplained     -> defined at first use
  p.20   §6.5.4 permits: one per household, charged -> rewritten as the reviewer asks
  p.21   "load bearing committed precondition"     -> one consistent term, defined
  p.22   measures image sits in the yards section  -> moved to Chapter 7
  p.23   who implements this?                      -> WITHDRAWN, handled with reviewer
  p.24   Komitas should be listed high             -> moved in every list
  p.24   park and ride still mentioned             -> removed

Plus the short-form BRT mode-shift statement from "BRT Mode Shift - Draft Subchapter
for Output 10.docx", inserted into §6.1.

Enforcement in Yerevan is entirely fixed pole-mounted ANPR with no roving
plate-scanning scan cars — confirmed by the user on 30 Jul 2026. The "mobile ANPR"
wording in the June draft was a drafting artefact and is corrected throughout.

One point remains drafted on a stated assumption, because the repository holds no
source that settles it; it is listed in the delivery note:
  * resident permits become priced and capped at one per household, which reverses
    the free-first-permit design the June draft proposed.

CORRECTION, 13 Aug 2026. An earlier version of this script wrote the loading bays up
as a design fact — "a design requirement agreed between the parking and corridor
design teams". No such agreement exists. The reviewer's comment ("you are all one
team, if the parking report says there should be loading bays, they should be in the
conceptual design") was read as a statement that the bays were already provided; it
is an instruction about what ought to happen, not a report of what has. The user
confirmed on 13 Aug 2026 that the design team has made no designated loading bays.
The report now says so plainly and directs the recommendation at the design team,
which answers the reviewer's "do they or don't they?" without asserting anything
unverified. Do not restate an assumption as an agreement between teams.
"""
import os
import re
import shutil

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import docx_edit as dx
import report_figures as rf

FP = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(FP, "Output 10 - Parking Analysis Report - 23062026 (rev).docx")
DST = os.path.join(FP, "Output 10 - Parking Analysis Report - 30072026 (rev).docx")

S, F, V, Y = rf.supply(), rf.survey(), rf.vehicles(), rf.yards()
Z = S["zones"]
C1, C2 = S["corridors"]["Corridor 01"], S["corridors"]["Corridor 02"]
OC, A = S["on_corridor"], F["all"]
pc = lambda v, whole=None: rf.pct(v, whole or OC)

PRECONDITION_DEF = (
    "A note on the term prerequisite. Several measures below are described as "
    "prerequisites rather than options. The distinction is arithmetical, not "
    "rhetorical: a prerequisite is a measure the displacement balance depends on, so "
    "that if it is not delivered the conclusion that displaced demand can be "
    "re-absorbed does not hold. Opening the gated residential courtyards is the "
    "clearest case, because off-street capacity carries "
    f"{A['offstreet_dependency_pct']:.0f}% of the absorptive capacity counted and that "
    f"stock is {S['off_street_yard_facilities_pct']:.0f}% courtyard by facility count. "
    "Everything "
    "else in the package improves the outcome; a prerequisite is load-bearing, and "
    "removing kerb capacity before it is in place would strand the displaced demand "
    "the survey measures. The earlier drafts used 'committed precondition' and "
    "'load-bearing' interchangeably for this idea; this report uses 'prerequisite' "
    "throughout."
)


# ---------------------------------------------------------------------------
def fix_enforcement(doc):
    """p.13 — the report describes pole-mounted cameras in one place and a 'patrol
    vehicle' in another. The reviewer asks which it is.

    Answered by describing the fixed-camera chain end to end and calling it complete,
    NOT by asserting that patrol vehicles do not exist. The report should state how the
    system works; a flat negative draws attention to the thing being denied and invites
    the question of how it is known. Vehicles are simply not mentioned in this context,
    and the stray reference that prompted the comment is removed.
    """
    dx.set_text(dx.find(doc, '"Parking City Service" operates ANPR cameras mounted on the poles'),
                '"Parking City Service" operates ANPR cameras mounted on poles along the '
                'street. These cameras surveil the designated parking zones, capturing the '
                'licence plates of every vehicle parked. Enforcement runs entirely through '
                'this fixed camera network: a parked vehicle is detected by the camera '
                'covering its zone, its plate is matched against the payment record held in '
                'the back-office, and a citation is issued from there if no valid session is '
                'found. That chain — fixed camera, back-office match, citation — is '
                'the complete mechanism by which a parking violation is established in '
                'Yerevan.')

    # "mobile ANPR" reads as vehicle-mounted, which is what prompted the question
    dx.sub_doc(doc, r"the operation of the mobile Automatic Number Plate Recognition \(ANPR\)",
               "the operation of the automated Automatic Number Plate Recognition (ANPR) "
               "camera network")
    dx.sub_doc(doc, r"a sophisticated, automated system utilizing mobile Automatic Number "
                    r"Plate Recognition \(ANPR\) technology",
               "a sophisticated, automated system built on a fixed network of Automatic "
               "Number Plate Recognition (ANPR) cameras")
    dx.sub_doc(doc, r"Operational Enforcement through Mobile ANPR Technology",
               "Operational Enforcement through ANPR Technology")

    # The Warsaw precedent legitimately describes Warsaw's scan cars, but it was
    # labelled "Mobile ANPR" — the same phrase that made the enforcement chapter read
    # as though Yerevan had them. Relabelled, and the contrast with Yerevan's
    # pole-mounted network made explicit so the two cannot be conflated.
    dx.sub_doc(doc, r"Automated E-Enforcement \(Mobile ANPR\):",
               "Automated E-Enforcement:")
    dx.sub_doc(doc, r"PCS CJSC already operates ANPR cameras— this asset should be "
                    r"prioritised for strict corridor enforcement\.",
               "Yerevan achieves the same automation through a fixed network instead: "
               "PCS CJSC already operates pole-mounted ANPR cameras, and that asset "
               "should be prioritised for strict corridor enforcement and extended to "
               "the side streets that take displaced demand.")
    dx.sub_doc(doc, r"was \"unable\" to make a payment before the patrol vehicle arrived",
               'was "unable" to make a payment before the camera recorded the vehicle')
    dx.sub_doc(doc, r"before the patrol vehicle arrived",
               "before the camera recorded the vehicle")


def refresh_numbers(doc):
    """Every figure onto the v2 / Corridors 1+2 basis."""
    dx.set_text(dx.find(doc, "The parking assessment for Yerevan was based on a desk-based"),
                f"The parking assessment for Yerevan was based on a desk-based parking supply "
                f"inventory covering the bus priority corridors with a 100-metre influence "
                f"area. Across Corridors 1 and 2 the survey identified {S['total']:,} parking "
                f"spaces, including {OC:,} on-street spaces on the corridors themselves, "
                f"{S['cross_street']:,} on-street spaces on adjacent cross-streets, and "
                f"{S['off_street']:,} off-street spaces in yards and lots. Corridor 3 is "
                f"withheld from the assessment pending its conceptual design; for the record "
                f"the inventory found a further 896 on-corridor spaces along it. This broader "
                f"survey frame matters because the project is concerned not only with the "
                f"parking currently on the corridors but also with the nearby streets and "
                f"off-street spaces that may absorb part of the impact once the corridor "
                f"designs are implemented.")

    paid = Z["zone_a"] + Z["zone_b"]
    dx.set_text(dx.find(doc, "The survey results show that the existing parking system"),
                f"The survey results show that the existing parking system along the corridors "
                f"is dominated by unregulated supply. Of the on-corridor spaces, {Z['free']:,} "
                f"({pc(Z['free']):.1f}%) are free, while only a relatively small proportion "
                f"fall within Zone A ({Z['zone_a']} spaces), Zone B ({Z['zone_b']} spaces) or "
                f"designated taxi spaces ({Z['taxi']}). The physical organisation of parking is "
                f"also weak: only {pc(S['signage_yes']):.0f}% of corridor parking has signage, "
                f"only {pc(S['marking_yes']):.0f}% has markings, and about "
                f"{pc(S['methods']['parallel']):.0f}% "
                f"is parallel parking. These findings indicate that a large share of the "
                f"existing parking supply is poorly structured and not managed in a systematic "
                f"way.")

    dx.set_text(dx.find(doc, "When the supply inventory was compared with the conceptual"),
                f"When the supply inventory was compared with the conceptual corridor designs, "
                f"the scale of impact became clear. On the v2 design the corridors would remove "
                f"{S['removed']:,} of the {OC:,} on-corridor spaces while {S['retained']:,} "
                f"would be retained or re-established, meaning that around "
                f"{S['removed_pct']:.0f}% of current corridor parking would be removed. This is "
                f"a substantial change, but it should be interpreted carefully. Even though all "
                f"Zone A corridor spaces would be removed, their share in relation to the total "
                f"Zone A parking supply in the city remains limited. Equally important, the "
                f"cross-street and yard inventory demonstrates that the corridor itself is not "
                f"the only location where parking can be managed or reorganised. These figures "
                f"follow the current conceptual design and will be updated when it is final.")

    dx.set_text(dx.find(doc, "The conceptual designs remove on-street parking along almost"),
                f"The conceptual designs remove on-street parking along almost the entire "
                f"length of the corridors — {S['removed_pct']:.0f}% of the on-corridor supply, "
                f"with roughly {S['retained']:,} spaces retained off the carriageway. This "
                f"outcome is not incidental but inherent to the design philosophy: the bus "
                f"lanes, combined with the requirement for cycle lanes, widened sidewalks and "
                f"landscaped curb extensions between every three to four retained off-corridor "
                f"parking spaces (as specified in the Terms of Reference), occupy the entirety "
                f"of the available right-of-way. This is consistent with the policy direction "
                f"established in the 2022 Mott MacDonald Parking and Taxi Management Strategy, "
                f"which explicitly states that parking will not be permitted on streets with "
                f"strategic bus routes, as the space is required for bus lanes, cycle lanes and "
                f"bus stops.")

    off = 100 - V["all"]["shares"]["location"]["carriageway"]
    dx.sub_doc(doc, r"The field survey found about 24\.5% of vehicles parked off the "
                    r"carriageway \(13% on footpaths, 11\.5% in setbacks\)",
               f"The field survey found about {off:.0f}% of vehicles parked off the carriageway "
               f"({V['all']['shares']['location']['footpath']:.1f}% on footpaths, "
               f"{V['all']['shares']['location']['setback']:.1f}% in setbacks)")

    # displacement recalibration
    dx.set_text(dx.find(doc, "Measured recalibration (field survey). The survey tests these"),
                f"Measured recalibration (field survey). The survey tests these a-priori labels "
                f"against behaviour. Kentron is confirmed high-sensitivity "
                f"({F['areas']['kentron']['peak_pct']}% peak) but for an off-street-led reason: "
                f"only about {F['areas']['kentron']['absorbed_onstreet_pct']}% of its displaced "
                f"demand can be re-absorbed on nearby streets. Komitas, previously medium, "
                f"behaves as high-sensitivity ({F['areas']['komitas']['peak_pct']}% peak, "
                f"{F['areas']['komitas']['absorbed_onstreet_pct']}% on-street absorption) and is "
                f"reclassified accordingly throughout this report. Shiraz/Hasratyan and "
                f"Malatia-Sebastia behave as genuinely lower-sensitivity "
                f"({F['areas']['shiraz']['peak_pct']}% and "
                f"{F['areas']['malatia']['peak_pct']}% peak). Gai Avenue is the one exception: "
                f"even filling every nearby off-street yard to capacity leaves a residual with "
                f"nowhere to go ({F['areas']['mega']['peak_pct']}% peak). So the kerb parking "
                f"simply stays for now, and gets a fresh look later as the area changes, when "
                f"new facilities become available or the planned BRT line arrives. Across the "
                f"surveyed areas, peak displaced demand was {A['displaced']:,} vehicles against "
                f"{A['removed']:,} spaces removed ({A['displaced_pct']:.0f}%) — that is, the "
                f"distinct vehicles counted in the removed zones at each area's busiest hour, "
                f"set against the capacity removed in those same zones — confirming with local "
                f"measurement that displaced demand falls well below the supply removed.",
                keep_lead_bold=True)

    dx.set_text(dx.find(doc, "Fourth and load-bearing - the re-absorption of displaced demand"),
                f"Fourth, and decisive for everything that follows: the re-absorption of displaced "
                f"demand is conditional "
                f"on off-street capacity. {A['offstreet_dependency_pct']:.0f}% of the "
                f"absorptive capacity that closes the aggregate gap to roughly 100% "
                f"({A['absorb_offstreet']:,} of {A['absorb_capacity']:,} spaces) is "
                f"off-street rather than kerbside, and that off-street stock is "
                f"overwhelmingly gated residential courtyard: "
                f"{S['off_street_yard_facilities_pct']:.0f}% of the facilities and "
                f"{S['off_street_yards_pct']:.0f}% of the capacity, the balance being a "
                f"small number of larger named commercial and institutional lots. It is "
                f"counted at gross capacity as if already open, and in "
                f"Kentron and Komitas the local dependency is higher still. Re-absorption is "
                f"therefore not automatic: it depends on those yards being opened and actively "
                f"managed, which is why opening residential yards is treated below as a "
                f"prerequisite rather than an optional add-on.")

    dx.set_text(dx.find(doc, "Measured off-street occupancy (field survey). This dependency"),
                f"Measured off-street occupancy (field survey). This dependency is now supported "
                f"by observation, not assumed. In each of the six areas the survey recorded "
                f"hourly occupancy in one representative off-street facility "
                f"({Y['total_spaces']} spaces). Averaged across the day these already-accessible "
                f"facilities run about {Y['weighted_avg_pct']}% full, so observed spare capacity "
                f"does exist; but at the peak hour three of the six are already at or over their "
                f"marked capacity (Palace {Y['areas']['mega']['peak_pct']}%, Nalbandyan "
                f"{Y['areas']['kentron']['peak_pct']}%, Komitas City "
                f"{Y['areas']['komitas']['peak_pct']}%), with Garegin "
                f"({Y['areas']['garegin']['peak_pct']}%), Shiraz "
                f"({Y['areas']['shiraz']['peak_pct']}%) and Sebastia "
                f"({Y['areas']['malatia']['peak_pct']}%) retaining real headroom. The facilities "
                f"already in use are themselves busy at the peak, which is why they are set "
                f"aside from the absorptive count, and the capacity that closes the displacement "
                f"gap sits in the gated residential courtyards that remain closed. The measured "
                f"occupancy therefore strengthens the case for treating the opening of "
                f"residential yards as a prerequisite; the per-facility figures are tabulated in "
                f"the companion Output 8.", keep_lead_bold=True)

    dx.set_text(dx.find(doc, "Field-survey verdict.  Elevate to a committed precondition"),
                f"Field-survey verdict. Elevate to a prerequisite. Off-street capacity carries "
                f"{A['offstreet_dependency_pct']:.0f}% of the absorptive capacity counted and is "
                f"{S['off_street_yard_facilities_pct']:.0f}% gated residential courtyard by "
                f"facility count, and "
                f"the roughly 100% aggregate re-absorption is conditional on opening them. This "
                f"moves from an optional outer-zone pilot to a core prerequisite of the whole "
                f"mitigation package.", keep_lead_bold=True)

    # The turnover range appears in several phrasings ("runs at 5-11 vehicles per
    # space per day", "turnover is already 5-11 per space per day"), so match the
    # number pair rather than any one sentence.
    # The "5-11 per space per day" in the June text was measured on the road-edge kerb
    # alone; its top end rests on 4 road-edge spaces in Malatia and 6 at Gai. Replaced
    # by the all-bay-type range, which every area can support (see report_figures).
    dx.sub_doc(doc, r"5\s*[–-]\s*11(?=\s*(vehicles\s*)?per space per day)",
               f"{A['turnover_lo']} to {A['turnover_hi']} ")
    dx.sub_doc(doc, r"peak displaced demand equal to only 55% of the spaces removed "
                    r"\(908 against 1,643\)",
               f"peak displaced demand equal to only {A['displaced_pct']:.0f}% of the spaces "
               f"removed ({A['displaced']:,} against {A['removed']:,})")
    dx.sub_doc(doc, r"about 92% of the absorptive capacity",
               f"{A['offstreet_dependency_pct']:.0f}% of the absorptive capacity")
    dx.sub_doc(doc, r"which carry about 92% of the absorptive capacity",
               f"which carry {A['offstreet_dependency_pct']:.0f}% of the absorptive capacity")
    dx.sub_doc(doc, r"About 90% of the kerb is currently unpriced",
               f"About {100 - pc(Z['zone_a'] + Z['zone_b']):.0f}% of the kerb is currently "
               f"unpriced")
    dx.sub_doc(doc, r"about 88% of corridor parking is unmarked",
               f"about {pc(S['marking_no']):.0f}% of corridor parking is unmarked")
    dx.sub_doc(doc, r"88% of parking spaces on the corridors are unmarked and unsigned",
               f"{pc(S['marking_no']):.0f}% of parking spaces on the corridors are unmarked, "
               f"and {pc(S['signage_no']):.0f}% are unsigned")
    dx.sub_doc(doc, r"roughly 24\.5% sits off the carriageway",
               f"roughly {off:.0f}% sits off the carriageway")
    dx.sub_doc(doc, r"\(123\.1% peak", f"({F['areas']['komitas']['peak_pct']}% peak")
    dx.sub_doc(doc, r"truck share = trucks ÷ all classified vehicles surveyed in the area: "
                    r"12\.6% in Malatia-Sebastia, 8\.0% in Shiraz, 4\.9% citywide",
               f"truck share = trucks divided by all classified vehicles surveyed in the area: "
               f"{V['areas']['malatia']['truck_pct']}% in Malatia-Sebastia, "
               f"{V['areas']['shiraz']['truck_pct']}% in Shiraz, {V['all']['truck_pct']}% "
               f"across all six areas")
    dx.sub_doc(doc, r"reaches 12\.6% in Malatia-Sebastia \(548 of 4,339 vehicles\) and 8\.0% "
                    r"in Shiraz \(198 of 2,469\), against 4\.9% citywide",
               f"reaches {V['areas']['malatia']['truck_pct']}% in Malatia-Sebastia "
               f"({V['areas']['malatia']['trucks']:,} of "
               f"{V['areas']['malatia']['classified']:,} vehicles) and "
               f"{V['areas']['shiraz']['truck_pct']}% in Shiraz "
               f"({V['areas']['shiraz']['trucks']} of "
               f"{V['areas']['shiraz']['classified']:,}), against {V['all']['truck_pct']}% "
               f"across all six areas")
    dx.sub_doc(doc, r"only about 14% of its displaced demand",
               f"only about {F['areas']['kentron']['absorbed_onstreet_pct']}% of its displaced "
               f"demand")


# ---------------------------------------------------------------------------
# chapter 5 — impacts
# ---------------------------------------------------------------------------
def fix_impact_chapter(doc):
    """Reviewer: the first paragraph of Chapter 5 still blames the median alignment;
    §5.3 claims there is no parking in the housing estates; §5.3 overstates the loss
    along Arshakunyats; and the loading-bay sentence does not say whether the design
    actually provides them — it does not, so the sentence is written as a recommendation
    directed at the design team."""
    dx.set_text(
        dx.find(doc, "The conceptual corridor designs developed under Task 2"),
        "The conceptual corridor designs developed under Task 2 of the project represent a "
        "fundamental reallocation of street space. Along much of the alignment the "
        "dedicated bus lanes run in the central median, consistent with international best "
        "practice for bus rapid transit as endorsed by the ITDP BRT Standard and the "
        "European BHLS (Buses with High Level of Service) framework; along other sections "
        "they run kerbside. It is worth being precise about what follows from that choice, "
        "because it is easy to attribute the parking loss to the median alignment. A "
        "kerb-aligned bus lane occupies the very kerbside space that parking occupies, and "
        "so removes as much on-street parking as a median-aligned one; the difference "
        "between the two is where passengers board, an island platform in the carriageway "
        "rather than a stop on the footway, not how much parking survives. The parking "
        "impact follows from reallocating the full right-of-way to bus lanes, general "
        "traffic, cycle lanes and adequate footways. That reallocation, not the alignment, "
        "is what carries direct and significant consequences for the existing on-street "
        "parking supply along both corridors.")

    dx.set_text(
        dx.find(doc, "The cross-sections developed by the design team allocate"),
        f"The cross-sections developed by the design team allocate the available carriageway "
        f"width to dedicated bus lanes (2 x 3.5 m), mixed-traffic lanes (2 x 3.0 m per "
        f"direction), median platforms and separators (0.5 m buffers), and minimum sidewalk "
        f"widths of 2.50 m on each side. In station areas, additional width is required to "
        f"accommodate 18-metre platform structures, turnstiles and bike parking facilities. "
        f"Where the existing right-of-way is fully consumed by that allocation, no kerbside "
        f"parking can be retained, and this is the case along most of the alignment. Between "
        f"stations, however, the cross-section is less demanding and in most such sections "
        f"there is room for parking to remain. That is why the design retains or "
        f"re-establishes {S['retained']:,} spaces ({S['retained_pct']:.0f}% of the "
        f"on-corridor supply) rather than removing all of it.")

    # §5.3 — the housing estates
    dx.set_text(
        dx.find(doc, "In residential segments of Corridors 2 and 3, particularly through"),
        "In residential segments of Corridor 2, particularly through the Nor Nork and "
        "Malatia-Sebastia districts, the parking that will be removed is predominantly used "
        "for overnight residential storage. It should be said plainly that these areas are "
        "not without parking. Aerial imagery and the field survey both show substantial "
        "parking between the blocks: along the internal streets, on setbacks and hard "
        "standing, and in the sheds and lock-up garages that occupy parts of the courtyards. "
        "Malatia-Sebastia in fact records the lowest daytime kerb pressure of the six "
        f"surveyed areas ({F['areas']['malatia']['peak_pct']}% peak) and the highest share "
        f"of parking standing off the carriageway (30.9%). The accurate statement is not "
        "that parking is absent but that formal, allocated provision per dwelling is low: "
        "the Soviet-era blocks were laid out before mass car ownership, so what exists is "
        "informal and unmanaged rather than designed. It should also be noted that the "
        "Corridor 2 alignment through Nor Nork runs at some distance from the housing "
        "estates themselves, so the parking directly removed there is largely arterial "
        "kerbside parking rather than the residents' own courtyard parking. The risk to "
        "manage is therefore displacement pressure arriving in those courtyards, not the "
        "loss of a provision the estates never had.")

    dx.set_text(
        dx.find(doc, "Along Arshakunyats Avenue, the wide right-of-way"),
        f"Along Arshakunyats Avenue, the wide right-of-way (typically exceeding 30 metres) "
        f"has historically accommodated multiple lanes of traffic alongside parking. The "
        f"conceptual design uses this width to provide a comprehensive cross-section "
        f"including bus lanes, two mixed-traffic lanes per direction, cycle lanes and "
        f"generous sidewalks. The width is largely consumed by that allocation, but not "
        f"entirely: Arshakunyats retains parking in the sections where the right-of-way "
        f"allows, and Corridor 1 as a whole retains {C1['retained']} of its "
        f"{C1['existing']:,} on-corridor spaces. The earlier draft's statement that the "
        f"design precludes the retention of any on-street parking along this avenue "
        f"overstated the position and is corrected here.")

    # loading bays — the reviewer's "do they or don't they?"
    dx.set_text(
        dx.find(doc, "Delivery and loading operations represent a critical functional"),
        "Delivery and loading operations represent a critical functional requirement that "
        "persists regardless of parking policy. The removal of curbside parking eliminates "
        "the informal loading zones that many businesses currently rely upon. The "
        "conceptual designs do not currently include designated loading bays. This report "
        "recommends that they be added at commercial concentrations along both corridors as "
        "the design is detailed, and directs that recommendation to the corridor design "
        "team. The field survey sizes "
        "that provision, since freight presence is concentrated rather than uniform: the "
        f"truck share of classified vehicles reaches "
        f"{V['areas']['malatia']['truck_pct']}% in Malatia-Sebastia and "
        f"{V['areas']['shiraz']['truck_pct']}% in Shiraz/Hasratyan against "
        f"{V['all']['truck_pct']}% across the six areas, so bays should be concentrated in "
        "those pockets. Taxi operations, currently informal along much of the corridor "
        "network, also require designated pick-up and drop-off facilities, particularly near "
        "stations and commercial concentrations.")


def fix_survey_chapter(doc):
    """The occupancy-survey section was written in the future tense as a plan. It is
    rewritten as what was done, and pointed at the new Output 8 chapter — which is the
    reviewer's "put more details in Output 8" comment resolved from this side."""
    h = dx.maybe(doc, "Field occupancy Survey")
    if h is not None and h.style.name.startswith("Heading"):
        dx.set_text(h, "Field Occupancy Survey", red=False)

    # Two body paragraphs in this section carry the Caption style. That puts them in
    # the List of Figures, which is a real TOC field keyed on Caption, so they have to
    # be demoted to body text or the rebuilt list picks up two paragraphs of prose.
    for frag in ("Field occupancy survey — six representative areas",
                 "The Parking Survey Methodology (v. 18052026) was designed"):
        p = dx.maybe(doc, frag)
        if p is not None and p.style.name == "Caption":
            p.style = doc.styles["Normal"]
    dx.set_text(
        dx.find(doc, "Field occupancy survey — six representative areas"),
        f"A field occupancy survey was carried out on six representative areas (Kentron, "
        f"Komitas, Gai Avenue/Mega Mall, Garegin Nzhdeh, Shiraz/Hasratyan and "
        f"Malatia-Sebastia) rather than the full corridor, on four separate ordinary working "
        f"days between 29 May and 3 June 2026. Enumerators made hourly licence-plate sweeps "
        f"from 07:00 to 24:00, recording for every parked vehicle the hour, the zone, the "
        f"plate, the vehicle type, the kerb location, the parking method and the legality — "
        f"{V['all']['sightings']:,} on-street sightings of "
        f"{V['all']['distinct_plates']:,} distinct vehicles across {A['surveyed_zones']} "
        f"survey zones, plus one off-street facility per area. The measured results are "
        f"summarised in this report; the full methodology, the survey locations and the "
        f"results broken down by area are set out in the field "
        f"occupancy survey chapter of the companion Traffic and Parking Surveys and Analysis "
        f"Report (Output 8).")

    # the four "planned mission" bullets are now history, not plan
    plan = dx.find(doc, "The Parking Survey Methodology (v. 18052026) was designed")
    dx.set_text(plan,
                "The survey was designed to establish an evidence-based baseline for kerbside "
                "use to inform the design of the bus priority corridors, capturing both formal "
                "red-line areas and free parking practice. The Parking Survey Methodology "
                "(v. 18052026) set out three defining features, all of which were executed: "
                "a 17-hour observation window (07:00 to 24:00) covering the full daily cycle "
                "of commuter and residential activity; manual licence-plate recording, which "
                "is what makes turnover and duration measurable rather than estimated; and "
                "systematic logging of parking that encroaches on footways, bus stops and "
                "second lanes. The one element that could not be delivered was payment "
                "compliance, which is observable only in the Parking City Service "
                "back-office.")
    for stale in ("Key features of the planned mission included:",
                  "17-Hour Observation Windows: Deployment of surveyors",
                  "License Plate Recording: Manual recording of plates",
                  "Illegal Parking Documentation: Systematic logging of violations"):
        p = dx.maybe(doc, stale)
        if p is not None:
            dx.drop(p)


# ---------------------------------------------------------------------------
# park & ride — removed everywhere
# ---------------------------------------------------------------------------
def remove_park_and_ride(doc):
    """The reviewer: "conceptual design does not include park and ride, and is not
    recommended. Remove paragraph." Every reference goes, replaced by a single
    sentence recording that it was considered and rejected, so the omission does not
    look like an oversight."""
    # the §6.5 measure block: heading, body, verdict
    head = dx.find(doc, "Park & ride")
    verdict = dx.find(doc, "Field-survey verdict.  The daytime fleet is overwhelmingly "
                           "short-stay. Keep park-and-ride as a future study item.")
    dx.drop_range(head, verdict)

    # the international best-practice paragraph
    dx.set_text(
        dx.find(doc, "Park-and-ride at peripheral stations is a complementary strategy"),
        "Park-and-ride at peripheral stations is a strategy often used to intercept car "
        "trips before they reach congested central sections, and the 2022 Mott MacDonald "
        "strategy recommends it for Yerevan in general terms. It is not carried forward as "
        "a measure in this report: the conceptual design for these corridors does not "
        "include park-and-ride facilities, and the field survey gives no support for "
        f"prioritising it, since the daytime kerb is overwhelmingly short-stay (about "
        f"{A['stay']['shortPct']}% of stays are one hour or less and only about "
        f"{A['stay']['workerPct']}% are all-day commuter parking) and park-and-ride "
        "addresses precisely the all-day commuter trip that is the smallest component of "
        "measured demand. It is therefore recorded here as considered and not recommended.")

    # sensitivity packages
    dx.sub_doc(doc, r", and considering park-and-ride support where corridor structure and "
                    r"trip patterns make that relevant", "")
    dx.sub_doc(doc, r"providing delivery spaces, and considering park-and-ride support where "
                    r"corridor structure and trip patterns make that relevant",
               "providing delivery spaces, and organising the currently informal parking on "
               "the surrounding streets")
    dx.sub_doc(doc, r"organising free parking, developing park-and-ride options, and, where "
                    r"feasible, opening residential yards for controlled daytime use",
               "organising free parking and, where feasible, opening residential yards for "
               "controlled daytime use")
    dx.sub_doc(doc, r"and peripheral interception of trips\.", "and local flexibility.")
    dx.sub_doc(doc, r"reorganisation, local flexibility, and peripheral interception of trips",
               "reorganisation and local flexibility")

    # conclusions
    dx.sub_doc(doc, r"organised free parking, park & ride, and residential yard opening",
               "organised free parking and residential yard opening")
    dx.sub_doc(doc, r"loading bays, visitor caps, P&R, and yard opening",
               "loading bays, visitor caps and yard opening")
    # further studies
    dx.sub_doc(doc, r"Supporting studies on park & ride feasibility, residential yard opening",
               "Supporting studies on residential yard opening")


# ---------------------------------------------------------------------------
# new and rewritten §6.5 measures
# ---------------------------------------------------------------------------
def rewrite_resident_permits(doc):
    """Reviewer p.20 §6.5.4: "Should state more clearly that resident parking permits
    be limited to 1 per household and charged." That reverses the free-first-permit
    design the June draft proposed; drafted as the reviewer directs."""
    dx.set_text(
        dx.find(doc, "Resident permit schemes are a standard instrument for managing"),
        "Resident permit schemes are a standard instrument for managing kerb space in "
        "high-pressure urban areas, particularly in residential neighbourhoods adjacent to "
        "major transport corridors. The scheme proposed here rests on two rules that should "
        "be stated without qualification. Permits are limited to one per household, issued "
        "against a verified home address and vehicle ownership; and permits are charged, at "
        "a modest annual fee rather than free of charge. A second vehicle at the same "
        "address is not eligible for a resident rate and pays the standard tariff. Both "
        "rules matter for the same reason: a free or unlimited permit converts scarce kerb "
        "space into a zero-priced entitlement, which is what produces the long-stay, "
        "low-turnover pattern the corridor strategy is trying to avoid, and it is very much "
        "harder to price a permit later than to price it from the outset. The fee should be "
        "set well below the commercial tariff, so that it protects residents against the "
        "cost of the new regulation, but not at zero.")

    dx.set_text(
        dx.find(doc, "This permit arrangement should be understood as a transitional"),
        "The measure is designed to operate in tandem with an expansion of the paid parking "
        "zone onto the cross-streets perpendicular to the corridors. Removing on-corridor "
        "parking will push displaced demand onto adjacent residential streets, and unless "
        "those streets are brought into the paid regime they will absorb the spillover at no "
        "cost to non-residents. By pricing the cross-streets and giving residents a "
        "low-cost, one-per-household permit, the scheme places the cost of the new "
        "regulation on displaced commuters rather than on local households, while still "
        "requiring residents to make a positive choice about kerb use. As public transport "
        "and non-motorised modal shares rise and car dependency declines, the resident rate "
        "should converge on the standard tariff and the distinction should be phased out "
        "altogether.")

    dx.sub_doc(doc, r"adopts a lighter, transitional variant tailored to the initial phase of "
                    r"the reform — free for the first household permit, with a reduced annual "
                    r"fee for a second registered vehicle, and linked to an expansion of the "
                    r"paid zone onto cross-streets",
               "adopts a lighter variant tailored to the initial phase of the reform: one "
               "charged permit per household at a modest annual fee, no resident rate for a "
               "second vehicle, and a linked expansion of the paid zone onto the cross-streets")
    dx.sub_doc(doc, r"Resident permits are transitional\. The free-permit model is designed to "
                    r"cushion residents during the reform's initial phase and should be phased "
                    r"out in the medium-to-long term as PT and NMT modal shares rise\.",
               "Resident permits are charged, capped and transitional. One permit per "
               "household, priced at a modest annual fee rather than issued free, is what "
               "keeps the scheme from re-creating the zero-priced kerb it is meant to replace. "
               "The resident rate should converge on the standard tariff as public-transport "
               "and non-motorised modal shares rise.")
    # NOT renumbered. The reviewer's section numbers run one chapter higher than what
    # Word actually renders (their "6.5" is the rendered 5.5, their "Section 6.3" the
    # rendered 5.3), so the document's own "see Section 5.5" was already correct and
    # an earlier pass of this script wrongly "fixed" it to 6.5. Left as 5.5, which is
    # where the TOC puts "Mitigation Measures for Yerevan".


def add_new_measures(doc):
    """Three §6.5 measures the reviewer asked for: pricing to the 85% target, removal
    of the flat annual permit, and derelict vehicles."""
    anchor = dx.find(doc, "A dedicated implementation study.")

    over = A["over_capacity"]
    cur = dx.insert_block(anchor, [
        ("Normal", "**Adjust parking charges towards 85% occupancy"),
        ("Normal",
         f"The survey provides the evidence for a measure that was missing from this "
         f"framework: adjusting the existing parking charges to the level at which the kerb "
         f"actually clears. The international target is 85% occupancy, at which roughly one "
         f"space in seven is free and an arriving driver can find it without cruising. "
         f"Measured occupancy is well above that. Capacity-weighted peak occupancy across "
         f"the surveyed areas is {A['peak_pct']}%, and {over} zones are over capacity "
         f"outright. In "
         f"Kentron, which is entirely within Zone A, peak occupancy reaches "
         f"{F['areas']['kentron']['peak_pct']}%. A price that leaves the kerb that full is "
         f"below the market-clearing price, whatever else may be said about it."),
        ("Normal",
         "The measure is therefore to move Zone A and Zone B from fixed tariffs to "
         "occupancy-based tariffs: set the hourly rate zone by zone at the level that "
         "delivers 85% occupancy at the peak hour, review it against measured occupancy on a "
         "fixed cycle, and publish both the occupancy data and the resulting rate. Rates "
         "should be allowed to differ between zones and between times of day, because "
         "measured occupancy differs. This is not a general tariff increase: in the outer "
         "areas, where peak occupancy is 54% to 75%, the same rule implies no charge at all "
         "for the time being, and organising the free parking is the appropriate measure "
         "there instead."),
        ("Normal",
         "There is a second reason to adopt this rule, specific to Yerevan. The 2024 tariff "
         "reform was challenged in the courts, and the rulings questioned the empirical "
         "basis on which the increases were set. A tariff derived from published occupancy "
         "measurements against a stated target is far more defensible than one set by "
         "judgement, because the question it answers is factual. The survey supplies the "
         "first such measurement; extending it to the zones that remain would supply the "
         "rest."),
        ("Normal", "**Withdraw the flat annual parking permit"),
        ("Normal",
         "Among the subscription options offered alongside hourly payment is a flat annual "
         "zonal permit, bought once for unlimited use of a parking zone for the year. It "
         "works directly against the corridor strategy. A flat annual fee reduces the "
         "marginal cost of each additional hour parked to zero, so a permit holder has no "
         "financial reason to leave, and the measure that the data identifies as the binding "
         "lever on the corridor kerb is precisely turnover. A single permit holder occupying "
         "a Zone A space all day displaces the six or seven short-stay visitors that space "
         "would otherwise serve."),
        ("Normal",
         "The measure is to withdraw the flat annual permit and, with it, the weekly and "
         "monthly period tariffs, replacing them with hourly occupancy-based pricing and the "
         "charged resident permit described above. This is also what the 2022 Mott MacDonald "
         "strategy recommends: that parking fees use an hourly rate only, with all "
         "period-based fees withdrawn. Withdrawal should be phased, with notice to existing "
         "holders and no mid-term cancellation, and paired with the resident permit so that "
         "residents who currently rely on the annual permit have a defined alternative."),
        ("Normal",
         "One qualification is needed on the evidence. Parking City Service has not released "
         "permit-uptake or tariff-revenue data, so the share of drivers holding an annual "
         "permit, and the revenue at stake in withdrawing it, are not known to this study. "
         "That data should be requested from Parking City Service and the withdrawal "
         "designed against it, including its revenue effect. The direction of the measure "
         "does not depend on the data — a flat annual fee suppresses turnover whatever its "
         "uptake — but the phasing and the compensating tariff do."),
        ("Normal", "**Remove derelict and long-term abandoned vehicles"),
        ("Normal",
         f"A kerb-management framework should include a route for removing vehicles that are "
         f"not being used at all, and Yerevan currently has none that is specific to "
         f"parking. The measure is a defined procedure: a vehicle observed stationary in the "
         f"same on-street space beyond a stated period is tagged, its registered owner "
         f"notified through the existing ANPR and police database link, and the vehicle "
         f"removed to a municipal pound at the owner's cost if it has not moved after a "
         f"further notice period. Parking City Service can identify candidates from the ANPR "
         f"record, since a plate detected in the same location across successive days without "
         f"a payment session is exactly what the system already sees; removal itself sits "
         f"with the Road Police, which holds the towing power."),
        ("Normal",
         f"The scale of the problem should be stated honestly, because the survey was able to "
         f"test it and the answer was negative. A vehicle present in every hourly sweep of "
         f"the 17-hour window has not moved all day, which is the cheapest observable proxy "
         f"for a stored or derelict vehicle. Across all six areas only "
         f"{V['all']['stationary_all_window']} vehicles of the "
         f"{V['all']['distinct_plates']:,} observed met that test. On this evidence, "
         f"abandoned vehicles are not a material component of corridor kerb pressure in "
         f"Yerevan, and this measure should be adopted as a piece of routine housekeeping "
         f"that closes a gap in the framework, not as a response to a significant measured "
         f"problem. A confirmatory check over several consecutive days, which the survey "
         f"design could not provide, would settle it."),
    ])
    return cur


def promote_annual_permit_note(doc):
    """The stand-alone "flagged idea, not yet a measure" note is superseded by the
    measure added above; it is rewritten as a pointer rather than left contradicting
    it."""
    dx.set_text(
        dx.find(doc, "Phase out the flat annual permit"),
        "Withdrawal of the flat annual permit is set out as a measure above, together with "
        "the occupancy-based pricing that replaces it, and is no longer presented as a "
        "candidate idea. The permit-uptake data that Parking City Service should supply, so "
        "that the phasing and the revenue effect can be designed, is identified there.")
    dx.set_text(
        dx.find(doc, "One of these subscription options is a flat annual zonal-parking permit"),
        "One of these subscription options is a flat annual zonal-parking permit, bought "
        "once for unlimited use of a parking zone for the year. Because a flat annual fee "
        "removes the marginal cost of each additional hour parked, it works against the kerb "
        "turnover the corridor strategy depends on. This report recommends withdrawing it in "
        "favour of hourly, occupancy-based pricing and a charged resident permit; the "
        "measure, and the Parking City Service permit data needed to phase it, are set out "
        "in the mitigation-measures chapter.")


def add_mitigation_conclusion(doc):
    """Reviewer: "Section needs some sort of conclusion." """
    anchor = dx.find(doc, "Taken together, these measures form a layered mitigation package")
    dx.set_text(anchor,
                "Taken together, these measures form a layered mitigation package for "
                "Yerevan. They do not seek to preserve the existing parking situation "
                "unchanged. Rather, they aim to manage the transition created by bus priority "
                "investment in a way that protects access where necessary, improves order and "
                "turnover, and supports the broader shift toward more sustainable urban "
                "mobility.")
    head = dx.insert_after(anchor, "Conclusion of the mitigation framework", style="Heading 2")
    dx.insert_block(head, [
        ("Normal",
         f"Four conclusions follow from the framework set out above. First, the corridor "
         f"itself does most of the work, but less of it than is often assumed: improved "
         f"public transport reduces the number of trips needing to park, yet the "
         f"international evidence and the local measurement both point to a modest, gradual "
         f"contribution rather than a substitute for parking management. Second, the "
         f"arithmetic of displacement is favourable but conditional. Peak displaced demand "
         f"across the surveyed areas is {A['displaced_pct']:.0f}% of the supply removed "
         f"({A['displaced']:,} vehicles against {A['removed']:,} spaces), and aggregate "
         f"re-absorption approaches 100% — but {A['offstreet_dependency_pct']:.0f}% of "
         f"the absorptive capacity counted is off-street, and that stock is "
         f"{S['off_street_yard_facilities_pct']:.0f}% gated residential courtyard not yet "
         f"open. Opening it is the prerequisite on which the rest of the package rests."),
        ("Normal",
         f"Third, the measures are not interchangeable, and the measured behaviour "
         f"determines which ones bind where. Because about {A['stay']['shortPct']}% of stays "
         f"are already an hour or less and turnover already runs at {A['turnover_lo']} to "
         f"{A['turnover_hi']} vehicles per space per day, maximum-stay limits address a "
         f"problem the corridor kerb does not have, while pricing, delineation and "
         f"off-street supply address the problem it does have. The measures that do the "
         f"heaviest lifting are therefore paid-zone extension with occupancy-based tariffs, "
         f"the opening of residential yards, delivery bays sized to the measured freight "
         f"pockets, and the organisation of the "
         f"{pc(S['marking_no']):.0f}% of the corridor kerb that is currently unmarked."),
        ("Normal",
         "Fourth, sequence is a substantive requirement rather than an implementation "
         "detail. The pricing, the delineation and above all the opening of the courtyards "
         "must be in place before kerb capacity is removed, because the displaced demand the "
         "survey measures is real and will arrive whether or not there is somewhere for it "
         "to go. A package delivered after removal is not the same package delivered late; "
         "it is a different and worse outcome, because overflow parking patterns are far "
         "harder to reverse once established."),
        ("Normal",
         "The one area where the framework does not resolve the problem is Gai Avenue at "
         "Mega Mall, where displaced demand is effectively the entire removed supply and "
         "even filling every nearby facility leaves a residual. Its kerb parking is left in "
         "place for now and should be revisited as the area changes, whether through new "
         "mall parking or the planned BRT service."),
    ])


def move_measures_image(doc):
    """Reviewer p.22: the summary image of all the measures sits in the section about
    opening residential yards; it should be in Chapter 7 with the other package
    material."""
    # Identified by its media part rather than by position: the new measures inserted
    # above it have already moved it, and doc.paragraphs rebuilds its Paragraph
    # objects on every access, so positional identity is not reliable here.
    target = None
    for p in dx.picture_paragraphs(doc):
        rids = [e.get(qn("r:embed")) for e in p._p.iter() if e.get(qn("r:embed"))]
        for rid in rids:
            if str(doc.part.related_parts[rid].partname).endswith("image8.png"):
                target = p
                break
        if target is not None:
            break
    if target is None:
        raise LookupError("mitigation-summary picture (image8.png) not found")
    anchor = dx.find(doc, "Below table demonstrates mitigation measures grouped by")
    dx.set_text(anchor,
                "The measures above are applied selectively by sensitivity zone. The two "
                "figures below summarise the package: the first sets out every measure and "
                "the zones it applies to, the second maps the sensitivity zones themselves.")
    dx.move_after(target, anchor)
    cap = dx.insert_after(target, "Figure X - Summary of the mitigation measures",
                          style="Caption")
    return cap


def fix_komitas(doc):
    """Reviewer p.24: Komitas is in the high-sensitivity zone on the measured evidence,
    so it should be listed there and not among the medium zones."""
    dx.set_text(
        dx.find(doc, "High-sensitivity zones include the central sections of Corridor 1"),
        f"High-sensitivity zones include the central sections of Corridor 1 through the "
        f"Kentron district, where parking demand is intense and the side streets are "
        f"themselves under significant parking pressure, together with Komitas Avenue. In "
        f"these areas the potential for simple displacement to adjacent streets is limited "
        f"and more comprehensive management interventions are required. The Amiryan, "
        f"Nalbandyan and Tigran Mets segments fall into this category, as does Komitas "
        f"Avenue, which the field survey moved here from the medium band: it runs at "
        f"{F['areas']['komitas']['peak_pct']}% peak occupancy with "
        f"{F['areas']['komitas']['absorbed_onstreet_pct']}% of its displaced demand "
        f"re-absorbable on nearby streets, which is high-sensitivity behaviour on both "
        f"measures. Komitas also carries 522 of the {Z['zone_b']} Zone B spaces on the "
        f"corridors, so it is the single largest block of priced kerb affected.")

    dx.set_text(
        dx.find(doc, "Medium-sensitivity zones encompass corridor segments where parking"),
        "Medium-sensitivity zones encompass corridor segments where parking demand is "
        "moderate and some absorptive capacity exists on parallel or perpendicular streets "
        "within 100 metres. The mid-sections of Arshakunyats Avenue, the Kievyan segment and "
        "Garegin Nzhdeh fall into this category. Here, managed displacement to side streets, "
        "combined with improved delineation and enforcement, can accommodate a meaningful "
        "share of the removed parking demand.")

    dx.set_text(
        dx.find(doc, "The high-sensitivity zone covers the most pressured central sections"),
        "The high-sensitivity zone covers the most pressured sections: the Kentron CBD, "
        "including streets such as Nalbandyan, Amiryan and Tigran Mets, and Komitas Avenue. "
        "These are the areas where parking demand is highest, surrounding activity intensity "
        "is greatest, and the removal of corridor parking is most likely to create visible "
        "pressure on adjacent streets. For these locations the recommended measures are the "
        "strongest ones: extending paid zones with occupancy-based tariffs (the lead "
        "measure), opening residential yards as a prerequisite, introducing delivery spaces, "
        "and charged one-per-household resident permits, with visitor caps held as a "
        "targeted contingency for genuinely low-turnover spots rather than a blanket "
        "control. In these areas parking management needs to prioritise turnover, protect "
        "local residents, and maintain business servicing while preventing uncontrolled "
        "spillover into surrounding streets.")

    dx.set_text(
        dx.find(doc, "The medium-sensitivity zone includes segments such as Arshakunyats"),
        "The medium-sensitivity zone includes segments such as Arshakunyats, Kievyan and "
        "Garegin Nzhdeh, where parking pressure remains substantial but the surrounding "
        "context allows somewhat greater flexibility. These areas typically combine "
        "residential, commercial and arterial functions, and they may offer more nearby "
        "capacity than the central core. Here the preferred package includes extending paid "
        "zones, providing delivery spaces, and organising the currently informal parking on "
        "the surrounding streets. Compared with the highest-sensitivity areas, the objective "
        "is less the strict protection of the centre and more orderly redistribution and "
        "operational control.")

    dx.set_text(
        dx.find(doc, "Measured recalibration of the packages."),
        f"Measured recalibration of the packages. Komitas moves into the high-sensitivity "
        f"zone ({F['areas']['komitas']['peak_pct']}% peak, "
        f"{F['areas']['komitas']['absorbed_onstreet_pct']}% on-street absorption) and is "
        f"listed there rather than among the medium zones. The opening of residential yards "
        f"moves up into the high-sensitivity package as a prerequisite. Occupancy-based "
        f"pricing and withdrawal of the flat annual permit are added to the high and medium "
        f"packages. Park-and-ride is removed from all three packages, as the conceptual "
        f"design does not include it.", keep_lead_bold=True)

    dx.set_text(dx.find(doc, "Figure 10 (measures by zone) and the sensitivity map"),
                "The figures below are updated to match this recalibration.")
    cap = dx.maybe(doc, "mitigation measures grouped by sensitivity zones")
    if cap is not None and cap.style.name == "Caption":
        dx.set_text(cap, cap.text.replace("mitigation measures grouped",
                                          "Mitigation measures grouped"))


def add_institutional_section(doc):
    """Reviewer p.23: "A first step may need to be institutional: someone needs to
    manage these steps." """
    # Placed before "Further Studies Required", because the reviewer's point is that
    # the institutional step comes FIRST: "someone needs to manage these steps".
    anchor = dx.find(doc, "The demand side is now measured, not inferred.")
    head = dx.insert_after(anchor, "Institutional Responsibility for Delivery",
                           style="Heading 2")
    cur = dx.insert_block(head, [
        ("Normal",
         "The measures in this report have no single owner at present, and that is itself "
         "the first risk to implementation. Parking in Yerevan is governed by four bodies "
         "with distinct and non-overlapping powers: the Council of Elders sets tariffs and "
         "designates zones; the Municipality's Transport Department holds strategic "
         "coordination with public transport and the road network; Parking City Service CJSC "
         "executes operations, marking and ANPR enforcement; and the Road Police adjudicate "
         "violations and hold the towing power. No one of them can deliver the package "
         "alone, and none currently holds a mandate to sequence it against the corridor "
         "construction programme."),
        ("Normal",
         "The recommendation is therefore institutional before it is technical. The "
         "Municipality's Transport Department should be designated as the accountable owner "
         "of kerbside management for the corridor programme, with a standing kerb-management "
         "function — a small team, not a new agency — responsible for holding the measure "
         "sequence, commissioning the occupancy measurements that the tariff rule depends "
         "on, and reporting on delivery. The Project Implementation Unit should carry the "
         "coordination between that function and the corridor construction programme for the "
         "duration of the project, because the sequencing requirement is what fails if the "
         "two run independently."),
        ("Normal",
         "The table below assigns each measure to the body that must act and the instrument "
         "it requires. It is intended as the basis for a delivery agreement rather than as a "
         "description of current practice."),
    ])
    cap = dx.insert_after(cur, "Table X - Institutional responsibility for each measure",
                          style="Caption")
    rows = [
        ["Measure", "Accountable body", "Instrument required"],
        ["Extend paid zones onto cross-streets", "Council of Elders (designation); "
         "Parking City Service (delivery)", "Council decision on zone boundaries; marking "
         "and signage programme; ANPR coverage extension"],
        ["Occupancy-based tariffs to the 85% target", "Council of Elders",
         "Tariff decision embedding an occupancy rule and a published review cycle"],
        ["Withdraw the flat annual permit", "Council of Elders; Parking City Service",
         "Tariff decision; notice to existing holders; permit-uptake data release"],
        ["Charged resident permits, one per household",
         "Council of Elders (fee); Parking City Service (issue)",
         "Permit regulation defining eligibility, the fee and address verification"],
        ["Open residential yards (prerequisite)",
         "Municipality Transport Department, with homeowners' associations",
         "Feasibility and implementation study; standard municipal template; legal basis "
         "for courtyard ownership and revenue sharing"],
        ["Delivery bays sized to the freight pockets",
         "Municipality Transport Department; corridor design team",
         "Incorporation into the detailed corridor design; time-restriction enforcement"],
        ["Organise and delineate free parking",
         "Parking City Service", "Marking and signage programme"],
        ["Visitor caps (targeted contingency)",
         "Council of Elders; Parking City Service", "Zone-specific maximum-stay rule"],
        ["Remove derelict vehicles",
         "Road Police, on referral from Parking City Service",
         "Notice-and-removal procedure; municipal pound"],
        ["Sequencing against construction",
         "Project Implementation Unit", "Delivery agreement with the Transport Department"],
    ]
    tbl = dx.add_table_after(doc, cap, rows, widths=[1.65, 1.6, 2.85])
    return tbl


def insert_brt_modeshift(doc):
    """The short-form statement from the BRT mode-shift research, which qualifies the
    "primary mitigation is the corridor itself" claim. Its 55% figure is refreshed."""
    anchor = dx.find(doc, "In other words, The bus priority corridors are themselves")
    dx.set_text(anchor,
                "In other words, the bus priority corridors are themselves the primary "
                "mitigation: by delivering faster, more reliable public transport they reduce "
                "the mode share of private cars, and so the number of vehicles needing to "
                "park. Some users shift modes, some adjust trip timing, and some no longer "
                "park on the corridor at all. Every other measure in the chapters that follow "
                "complements that structural shift.")
    dx.insert_after(
        anchor,
        f"How much car travel the corridor absorbs. International experience indicates that "
        f"the corridor itself absorbs a real but modest share of private-car travel, and that "
        f"the size of that share depends on what the BRT replaces. Rider surveys on European "
        f"and North American corridors report that between 5% and 29% of passengers "
        f"previously made the same trip by car; Istanbul's Metrobus, the nearest regional "
        f"comparator, recorded 4 to 9% five years after opening. Where BRT is built over an "
        f"existing dense bus or minibus network, however, the figure falls to the low single "
        f"digits: 9% in Bogota, 4% in Lagos and Lahore, 1.4% in Guangzhou, and effectively "
        f"zero in the surveyed Soweto corridor of Johannesburg, because the great majority of "
        f"riders transfer from services they were already using rather than from cars. "
        f"Yerevan's corridors follow existing high-ridership public-transport spines and "
        f"should therefore be planned on the lower assumption. This is consistent with the "
        f"field survey, which found that genuine all-day commuters — the trips a BRT is best "
        f"able to absorb — account for only about {A['stay']['workerPct']}% of observed kerb "
        f"parking, against {A['stay']['shortPct']}% staying one hour or less. Modal shift "
        f"should accordingly be treated as a gradual, second-order contribution to relieving "
        f"parking pressure rather than as a substitute for the parking measures proposed "
        f"here; the case for the kerb reallocation rests on the directly measured finding "
        f"that peak displaced demand equals only {A['displaced_pct']:.0f}% of the spaces "
        f"removed.", bold_lead=True)


def add_precondition_definition(doc):
    """Reviewer p.19 and p.21: "committed pre-condition" and "load bearing committed
    precondition" are unexplained. Define the idea once, in plain words, at first use
    and use one term throughout."""
    # Terminology first, definition second. Inserting the definition before running
    # the substitutions rewrote the quoted old terms inside the definition itself,
    # leaving it saying the drafts used "prerequisite" and "load-bearing"
    # interchangeably — which is not what it means to say.
    dx.sub_doc(doc, r"committed pre-?conditions", "prerequisites")
    dx.sub_doc(doc, r"committed pre-?condition", "prerequisite")
    dx.sub_doc(doc, r"a core precondition", "a core prerequisite")
    dx.sub_doc(doc, r"load-bearing precondition", "prerequisite")
    dx.sub_doc(doc, r"'mitigation before removal' load-bearing rather than advisory",
               "'mitigation before removal' a prerequisite rather than advisory")
    anchor = dx.find(doc, "Fourth, and decisive for everything that follows")
    dx.insert_after(anchor, PRECONDITION_DEF, bold_lead=True)


def fix_soviet_estates_language(doc):
    """Reviewer p.19: the text blames Soviet-era estates for not having parking, with
    an implied entitlement. Keep the structural fact, drop the judgement."""
    dx.set_text(
        dx.find(doc, "Third, the Soviet-era urban form that characterises much of Yerevan"),
        "Third, the urban form of much of Yerevan, particularly the residential areas served "
        "by Corridor 2, means that on-street management alone cannot balance parking demand "
        "and supply. The microrayon blocks were laid out before mass car ownership and "
        "provide little allocated off-street parking, and as car ownership has risen the "
        "resulting demand has spread onto whatever surfaces were available, including "
        "footways, courtyards and green space. This is a description of how the stock was "
        "built, not a claim that residents are owed a parking space: the policy question is "
        "how to manage a scarce public resource fairly, and the answer proposed here is to "
        "price and organise it rather than to expand it. What the corridor project must "
        "avoid is making the position materially worse in places where residents have "
        "genuinely limited alternatives, which is why the sequencing of the yard opening "
        "matters most in exactly these areas.")


def fix_conclusions(doc):
    dx.set_text(
        dx.find(doc, "Parking loss is substantial and inherent to the design."),
        f"Parking loss is substantial and inherent to the design. On the v2 conceptual "
        f"design the cross-section removes {S['removed']:,} of the {OC:,} on-corridor "
        f"on-street spaces on Corridors 1 and 2 ({S['removed_pct']:.0f}%), retaining or "
        f"re-establishing {S['retained']:,}, consistent with the Mott MacDonald (2022) "
        f"strategy and the Yerevan Sustainable Urban Transport Strategy. The loss follows "
        f"from reallocating the full cross-section rather than from the median alignment as "
        f"such: kerb-aligned sections remove as much kerbside parking as median-aligned "
        f"ones. Corridor 3 is withheld pending its conceptual design, and these figures will "
        f"be updated when the design is final.", keep_lead_bold=True)

    dx.set_text(
        dx.find(doc, "Impacts are highly differentiated by zone."),
        f"Impacts are highly differentiated by zone. The Kentron CBD and Komitas Avenue face "
        f"the highest pressure — {F['areas']['kentron']['peak_pct']}% and "
        f"{F['areas']['komitas']['peak_pct']}% peak occupancy, with only "
        f"{F['areas']['kentron']['absorbed_onstreet_pct']}% and "
        f"{F['areas']['komitas']['absorbed_onstreet_pct']}% of displaced demand re-absorbable "
        f"on nearby streets — and Komitas is reclassified from medium to high sensitivity on "
        f"that evidence. Mid-corridor arterials face moderate pressure; outer residential "
        f"segments require lighter-touch reorganisation.", keep_lead_bold=True)

    dx.set_text(
        dx.find(doc, "The demand side is now measured, not inferred."),
        f"The demand side is now measured, not inferred. A targeted field occupancy survey of "
        f"six representative areas recorded capacity-weighted peak occupancy of "
        f"{A['peak_pct']}%, a "
        f"short-stay, high-turnover kerb (about {A['stay']['shortPct']}% of stays one hour or "
        f"less; turnover {A['turnover_lo']} to {A['turnover_hi']} per space per day), and "
        f"peak displaced demand equal to only {A['displaced_pct']:.0f}% of the spaces removed "
        f"({A['displaced']:,} against {A['removed']:,}). Aggregate re-absorption approaching "
        f"100% is achievable but conditional on opening the gated residential courtyards, "
        f"which supply {A['offstreet_dependency_pct']:.0f}% of the absorptive capacity "
        f"counted. The "
        f"measured behaviour recalibrates the zoning: Komitas behaves as high-sensitivity and "
        f"is reclassified, and Gai Avenue's kerb parking is left in place for now, to be "
        f"revisited as the area develops.", keep_lead_bold=True)

    dx.set_text(
        dx.find(doc, "Mitigation must be layered, not singular."),
        "Mitigation must be layered, not singular. No single measure resolves displacement. "
        "The recommended package combines paid-zone expansion with occupancy-based tariffs, "
        "withdrawal of the flat annual permit, charged one-per-household resident permits, "
        "loading bays sized to the measured freight pockets, organised free parking, the "
        "opening of residential yards, targeted visitor caps and a route for removing "
        "derelict vehicles — applied selectively by sensitivity zone, with the yard opening "
        "as the prerequisite the arithmetic depends on.", keep_lead_bold=True)

    # The hand-typed "7.1 / 7.2" labels were stale against the rendered numbering.
    # They are stripped and the headings attached to the real numbering list instead
    # (see fix_heading_numbering), so Word numbers them and they cannot go stale again.
    dx.sub_doc(doc, r"^7\.1 Key Conclusions", "Key Conclusions")
    dx.sub_doc(doc, r"^7\.2 Further Studies Required", "Further Studies Required")


def fix_heading_numbering(doc):
    """Attach every Heading 2 that lacks list numbering to the document's heading list.

    Every Heading 2 is forced onto the SAME list as its siblings. Headings created by
    restyling a paragraph inherit that paragraph's numbering — none (renders as
    "1.1") or an unrelated list (numId 32, which numbers out of sequence) — and the
    two in the Conclusions chapter carried numId 0 because their numbers used to be
    typed by hand.
    Without this the TOC shows "1.1 Conclusion of the mitigation framework" beside
    "5.5 Mitigation Measures for Yerevan", and the Conclusions subheadings show no
    number at all.
    """
    ref = None
    for p in doc.paragraphs:
        if p.style.name == "Heading 2" and "Rationale for Benchmarking" in p.text:
            ref = p
            break
    if ref is None:
        raise LookupError("no reference Heading 2 to copy numbering from")
    ref_el = ref._p.pPr.find(qn("w:numPr")).find(qn("w:numId"))
    ref_numid = ref_el.get(qn("w:val"))
    fixed = []
    for p in doc.paragraphs:
        if p.style.name != "Heading 2" or not p.text.strip():
            continue
        pr = p._p.pPr
        num = pr.find(qn("w:numPr")) if pr is not None else None
        numid = None
        if num is not None:
            el = num.find(qn("w:numId"))
            numid = el.get(qn("w:val")) if el is not None else None
        if numid != ref_numid:
            if dx.copy_numbering(p, ref):
                fixed.append(f"{p.text.strip()[:44]} (was numId {numid})")
    return fixed


# ---------------------------------------------------------------------------
def renumber_captions(doc):
    counters = {"Figure": 0, "Table": 0}
    for p in doc.paragraphs:
        if p.style.name != "Caption":
            continue
        for kind in ("Figure", "Table"):
            if p.text.strip().startswith(kind):
                counters[kind] += 1
                # Strip whatever separator the existing caption used. These files mix
                # "Figure 1 - Title", "Figure 4, Title" and "Figure 10. Title", so a
                # naive split on " - " leaves the old number embedded.
                rest = re.sub(rf"^{kind}\s*[A-Za-z0-9]*\s*[-–—.,:]?\s*", "",
                              p.text.strip())
                # Rebuilt WITH its SEQ field: the Lists of Figures and Tables collect
                # only paragraphs that carry one, so plain text would empty them.
                dx.set_caption(p, kind, rest, number=counters[kind])
                break
    return counters


def force_field_update(doc):
    settings = doc.settings.element
    for existing in settings.findall(qn("w:updateFields")):
        settings.remove(existing)
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


def main():
    shutil.copyfile(SRC, DST)
    doc = Document(DST)

    fix_enforcement(doc)
    refresh_numbers(doc)
    fix_impact_chapter(doc)
    fix_survey_chapter(doc)
    fix_soviet_estates_language(doc)
    add_precondition_definition(doc)
    insert_brt_modeshift(doc)
    remove_park_and_ride(doc)
    rewrite_resident_permits(doc)
    add_new_measures(doc)
    promote_annual_permit_note(doc)
    add_mitigation_conclusion(doc)
    move_measures_image(doc)
    fix_komitas(doc)
    # WITHDRAWN, 14 Aug 2026, at the user's direction. The institutional subsection
    # was removed from the rev document by hand: assigning delivery responsibility to
    # named authorities needs analysis this report does not carry. The reviewer's p.23
    # comment is being handled with the reviewer directly, not in the text.
    # add_institutional_section(doc)
    fix_conclusions(doc)
    renumbered = fix_heading_numbering(doc)
    counters = renumber_captions(doc)
    force_field_update(doc)

    doc.save(DST)
    print("WROTE:", DST)
    print(f"       {counters['Figure']} figures, {counters['Table']} tables")
    print(f"       heading numbering attached to: {renumbered}")

    also = os.path.join(rf.ROOT, "Field Surveys/Field Surveys Report",
                        os.path.basename(DST))
    shutil.copyfile(DST, also)
    print("COPIED:", also)


if __name__ == "__main__":
    main()
