#!/usr/bin/env python
"""Draft subchapter for Output 10: how much private-car travel a BRT corridor
actually absorbs — international evidence.

Written to answer a standing gap: Output 8/10 and the audit memo repeatedly
frame the corridor itself (M0) and the commuter tail as a "BRT mode-shift
opportunity", but carry NO quantified international figure for how much car
travel a BRT absorbs. This note supplies that evidence, with the timing of each
measurement relative to the corridor's opening, and the caveats attached.

Evidence base: a NotebookLM deep-research pass (notebook "BRT Mode Shift
Evidence - Car Absorption", 434a5ad1-f0d0-4698-9aea-65eee19c9ed4, 50 web
sources, 24 Jul 2026).

PROVENANCE DISCIPLINE — the deep-research pass also produced its own synthesis
document ("Strategic Evaluation of Bus Rapid Transit Mode Shift...") which has
no URL and is NOT a published source. Figures traceable only to it are
quarantined in Table 4 and must not be cited in a client deliverable without
verification. The same flag-don't-average rule as the residential-yards note.

Output: Field Surveys/Field Surveys Report/
        BRT Mode Shift - Draft Subchapter for Output 10.docx
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = (r"C:/Users/user/Yerevan-Parking/Field Surveys/Field Surveys Report/"
       r"BRT Mode Shift - Draft Subchapter for Output 10.docx")

NAVY = RGBColor(0x14, 0x2A, 0x4A)
ACCENT = RGBColor(0x00, 0x6D, 0x77)
RED = RGBColor(0xC0, 0x2A, 0x2A)
GREY = RGBColor(0x55, 0x55, 0x55)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)


def _shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), hex_)
    tcPr.append(sh)


def title(text, sub=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(17)
    r.font.color.rgb = NAVY
    if sub:
        p2 = doc.add_paragraph()
        r2 = p2.add_run(sub)
        r2.italic = True
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = ACCENT


def heading(text, level=1):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.color.rgb = NAVY if level == 1 else ACCENT
    r.font.size = Pt(13 if level == 1 else 11.5)
    p.paragraph_format.space_before = Pt(10)
    return p


def body(text, bold_lead=None, color=None, size=None):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        r.font.color.rgb = color or NAVY
        if size:
            r.font.size = Pt(size)
    r = p.add_run(text)
    if color:
        r.font.color.rgb = color
    if size:
        r.font.size = Pt(size)
    return p


def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
    p.add_run(text)
    return p


def caption(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = ACCENT
    p.paragraph_format.space_before = Pt(8)
    return p


def table(headers, rows, widths=None, hdr_fill="142A4A"):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = 1
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]
        c.text = ""
        rr = c.paragraphs[0].add_run(h)
        rr.bold = True
        rr.font.size = Pt(8.5)
        rr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        _shade(c, hdr_fill)
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            cells[j].text = ""
            rr = cells[j].paragraphs[0].add_run(str(val))
            rr.font.size = Pt(8.5)
    if widths:
        for row in t.rows:
            for j, w in enumerate(widths):
                row.cells[j].width = Inches(w)
    return t


def callout(text, lead="Caveat. "):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.15)
    r = p.add_run(lead)
    r.bold = True
    r.font.color.rgb = RED
    r.font.size = Pt(9.5)
    r2 = p.add_run(text)
    r2.italic = True
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = GREY
    return p


def source_note(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(8)
    r.font.color.rgb = GREY
    return p


# ============================================================ HEADER
title("How Much Car Travel Does the Corridor Itself Absorb?",
      "Draft subchapter proposed for Output 10 — international evidence on BRT mode shift "
      "from the private car, with the timing of each measurement. Draft for review; not yet "
      "inserted into the report.")

t = doc.add_table(rows=4, cols=2)
t.style = "Table Grid"
meta = [
    ("Status", "DRAFT for client review. Proposed as a new subchapter under the mitigation "
               "measures discussion, supporting measure M0 (the corridor itself / modal shift)."),
    ("Gap it closes", "Output 8, Output 10 and the Mitigation Measures Audit all frame the "
                      "corridor and the commuter tail as a \u201cBRT mode-shift opportunity\u201d but "
                      "attach no international figure to it. This supplies the figure \u2014 and its limits."),
    ("Evidence basis", "Structured review of 50 international sources (NotebookLM deep-research "
                       "pass, 24 July 2026). Primary-source figures in Tables 1\u20133; unverified "
                       "secondary figures quarantined in Table 4."),
    ("Bottom line", "Car diversion is real but modest, and is far lower where BRT mainly replaces "
                    "existing bus and minibus services \u2014 which is Yerevan\u2019s situation. The corridor "
                    "should not be presented as a self-financing solution to displaced parking demand."),
]
for i, (k, v) in enumerate(meta):
    cells = t.rows[i].cells
    cells[0].text = ""
    rr = cells[0].paragraphs[0].add_run(k)
    rr.bold = True
    rr.font.size = Pt(9)
    rr.font.color.rgb = NAVY
    cells[1].text = ""
    rr2 = cells[1].paragraphs[0].add_run(v)
    rr2.font.size = Pt(9)
    cells[0].width = Inches(1.5)
    cells[1].width = Inches(5.2)

# ============================================================ 1. THE QUESTION
heading("1. The question, and why the answer is not a single number")
body("The corridor itself is the primary mitigation measure in this strategy: if the BRT moves "
     "enough trips out of private cars, the parking removed along the alignment matters less, "
     "because part of the demand for it disappears rather than relocating. That proposition has "
     "so far been asserted rather than quantified. The international record allows it to be "
     "quantified \u2014 but only if three quite different measurements are kept apart, because they "
     "are routinely conflated in the literature and produce very different-looking numbers for "
     "the same corridor.")
bullet("the share of BRT riders who report that they previously made the same trip by private "
       "car. This is the figure almost always quoted. It is a property of the riders, not of the "
       "city\u2019s traffic.", bold_lead="Rider previous-mode share \u2014 ")
bullet("the change in the share of all trips made by car, city-wide or corridor-wide, measured "
       "in percentage points by household or origin\u2013destination survey. This is the policy-"
       "relevant figure and it is almost always much smaller.", bold_lead="Car mode-share change \u2014 ")
bullet("the change in vehicles counted on the corridor after opening. Objective, but it cannot "
       "distinguish drivers who switched to the bus from drivers who simply re-routed to a "
       "parallel street.", bold_lead="Traffic-volume change \u2014 ")
callout("A corridor can show 25\u201330% of its riders as former car users while the city\u2019s car mode "
        "share barely moves \u2014 because the BRT carries a small share of all city trips. Quoting a "
        "rider-survey percentage as though it were a reduction in car use is the single most common "
        "error in this literature, and the sources warn against it explicitly.")

# ============================================================ 2. TABLE 1 EUROPE
heading("2. European and high-car-ownership corridors")
body("These are the corridors most comparable to Yerevan in vehicle ownership and in the "
     "existence of a real car alternative, and they show the highest car-diversion figures in "
     "the record \u2014 broadly 5% to 29% of riders. The European BHLS corridors in particular are "
     "the precedent already invoked in Output 8\u2019s displacement chapter.")
caption("Table 1 \u2014 Share of BRT riders who previously made the trip by private car: European "
        "and high-car-ownership corridors")
table(
    ["City / corridor", "Riders previously by car", "When measured, relative to opening", "Source"],
    [["Nantes, Busway Line 4 (France)", "29%", "Opened 2006; survey year not stated (figure cited in a 2010 report) \u2014 within ~4 years",
      "DTU international review"],
     ["Kent Thameside, Fastrack (UK)", "19%", "Not stated (figure cited in a 2011 review)", "DTU international review"],
     ["Dublin, Malahide QBC (Ireland)", "17%", "Survey 2002; opening year not stated", "DTU international review"],
     ["Madrid, Bus-VAO (Spain)", "15%", "Not stated", "DTU international review"],
     ["Helsinki, Jokeri line (Finland)", "12%", "Not stated (figure cited in a 2011 review)", "DTU international review"],
     ["Beijing, BRT Line 1 (China)", "12%", "Opened 2004; survey year not stated (cited in 2012\u201313 reviews)", "DTU international review"],
     ["Paris, Trans-Val-de-Marne (France)", "8%", "Opened 1993; survey year not stated", "DTU international review"],
     ["Istanbul, Metrob\u00fcs (T\u00fcrkiye)", "4\u20139%", "Opened 2007; survey 2012 \u2014 about 5 years after opening", "DTU international review (Alpkokin & Ergun, 2012)"],
     ["Stockholm, Stombuss (Sweden)", "5%", "Not stated (figure cited in a 2011 review)", "DTU international review"]],
    widths=[1.9, 1.05, 2.5, 1.35])
source_note("Source: \u201cEffects of new bus and rail rapid transit systems \u2013 an international review\u201d "
            "(Technical University of Denmark, peer-reviewed). All figures are self-reported previous "
            "mode from rider surveys.")
callout("Istanbul is the nearest regional comparator and the most cautionary entry in this table: "
        "4\u20139%, measured five years after opening, on a corridor with far higher ridership than "
        "Yerevan\u2019s will carry. A second source in the review set reports 40% for Istanbul; that "
        "figure appears only in a secondary table and is irreconcilable with the peer-reviewed "
        "value. It should not be used.")

# ============================================================ 3. TABLE 2 US
heading("3. North American corridors \u2014 the effect of survey timing")
body("The United States evaluations matter less for their absolute values than for what they "
     "show about timing: they were carried out on a consistent onboard-survey method, and the "
     "interval between opening and survey is documented in every case. They cluster in a narrow "
     "band of roughly 15% to 25% regardless of whether the survey ran three months or six years "
     "after opening.")
caption("Table 2 \u2014 Share of BRT riders who previously made the trip by private car: US onboard surveys")
table(
    ["City / corridor", "Riders previously by car", "When measured, relative to opening", "Survey year"],
    [["Los Angeles, Orange Line", "16.9% (drive alone)", "Opened Oct 2005; surveyed Jan 2006 \u2014 3 months after opening", "2006"],
     ["Los Angeles, Orange Line", "25% (16% alone + 9% carpool)", "Same corridor, surveyed Jun 2009 \u2014 nearly 4 years after opening", "2009"],
     ["Oakland, San Pablo Rapid", "24.3%", "Opened Jun 2003; surveyed 2004 \u2014 about 1 year after opening", "2004"],
     ["Kansas City, MAX", "24.3%", "Opening year not stated in sources", "2005"],
     ["Boston, Silver Line Waterfront", "22.1%", "Opened 2004; surveyed 2006 \u2014 about 2 years after opening", "2006"],
     ["Miami, South Miami-Dade Busway", "20.8%", "Opened 1997; surveyed 2003 \u2014 about 6 years after opening", "2003"],
     ["Las Vegas, MAX", "18.5%", "Opening year not stated in sources", "2005"],
     ["Cleveland, HealthLine", "17.5%", "Opened 2008; surveyed 2009 \u2014 about 1 year after opening", "2009"],
     ["Eugene, EmX Franklin corridor", "15.6%", "Opened Jan 2007; surveyed 2008 \u2014 about 1 year after opening", "2008"]],
    widths=[1.9, 1.35, 2.55, 0.85])
source_note("Source: Federal Transit Administration, \u201cMetro Orange Line BRT Project Evaluation\u201d "
            "(FTA Report No. 0004), consolidated onboard-survey table. Boston figure corroborated by "
            "the FTA Boston Silver Line report.")
body("The two Los Angeles rows are the only true before-and-after pair in the record, and they "
     "are worth reading carefully rather than as a trend. Drive-alone diversion was 16.9% at "
     "three months and 16% at four years \u2014 essentially unchanged; the higher 2009 headline is "
     "explained by the later survey also counting former carpool passengers. The honest reading "
     "is that car diversion on this corridor was stable over four years, not that it grew.",
     bold_lead="On durability. ")

# ============================================================ 4. TABLE 3 DEVELOPING
heading("4. Cities where BRT replaces existing bus and minibus services")
body("This is the decisive group for Yerevan. Where a BRT is built over an existing dense bus or "
     "minibus network, the overwhelming majority of its riders transfer from those services, and "
     "car diversion collapses to low single digits \u2014 not because the BRT is worse, but because "
     "the people it carries were never in cars to begin with.")
caption("Table 3 \u2014 Car diversion and previous-mode composition where BRT replaces existing bus / paratransit")
table(
    ["City / corridor", "Riders previously by car", "When measured, relative to opening", "Where the riders actually came from"],
    [["Bogot\u00e1, TransMilenio (Colombia)", "9%", "Opened Dec 2000; rider survey 2005 \u2014 about 5 years after opening", "City-wide private-vehicle trip share fell 18% \u2192 11%, 1999\u20132005"],
     ["Bogot\u00e1, TransMilenio corridor", "~10% of corridor trips", "Corridor study 2001 \u2014 about 1 year after opening", "Trips that would otherwise have been made by private vehicle"],
     ["Jakarta, TransJakarta Corridor 1", "14% from cars (20% from all private motorised modes)", "Opened Jan 2004; surveyed early 2004 \u2014 less than 1 year after opening", "35% from non-AC buses, 32% from AC buses, 6% from motorcycles (n = 320)"],
     ["Lagos, BRT-Lite (Nigeria)", "4%", "Opened Mar 2008; surveyed late 2008 \u2014 less than 1 year after opening", "85% transferred from informal minibus taxis (danfos); 11% induced new trips"],
     ["Lahore, Metrobus (Pakistan)", "4%", "Opened Feb 2013; surveyed Feb 2015 \u2014 exactly 2 years after opening", "Questionnaire survey of 760 passengers"],
     ["Johannesburg, Rea Vaya (South Africa)", "~4% city-wide; 0% in the Soweto corridor survey", "Opened Aug 2009; surveyed 2011 \u2014 about 2 years after opening", "66% transferred from minibus taxis; remainder from conventional bus or rail"],
     ["Guangzhou, BRT (China)", "1.4%", "Opened Feb 2010; survey year not stated (cited in a 2012 report)", "84.6% from existing bus / paratransit; 11% from metro"]],
    widths=[1.75, 1.3, 2.15, 1.6])
source_note("Sources: FTA Bogot\u00e1 TransMilenio applicability study (2006); ITDP Bus Rapid Transit "
            "Planning Guide (2007); Clean Air Asia, \u201cInitiating Bus Rapid Transit in Jakarta\u201d; Lagos "
            "BRT-Lite scheme evaluation; Lahore School of Economics (Batool et al.); Venter and Vaz "
            "(2011) for Rea Vaya; secondary reporting for Guangzhou.")
callout("Johannesburg is the clearest warning in the whole record. The corridor survey in Soweto "
        "found zero riders diverted from private cars while two thirds came off minibus taxis \u2014 and "
        "the city-wide shift from cars remained around 4%. A corridor can be a ridership success and "
        "a car-diversion failure at the same time.", lead="Read this one. ")

# ============================================================ 5. WHAT IT MEANS FOR YEREVAN
heading("5. What this means for the Yerevan corridors")
body("Yerevan sits between the two groups, and closer to the second. Car ownership and the "
     "presence of a genuine driving alternative resemble the European cases; but the corridors "
     "selected for BRT are the city\u2019s existing high-frequency public-transport spines, already "
     "carrying substantial bus and minibus volumes, which is precisely the condition that "
     "produces low car diversion in Bogot\u00e1, Guangzhou, Lagos and Johannesburg. The defensible "
     "planning assumption is therefore a car-diversion share at the lower end of the "
     "international range, in the order of 5\u201310% of corridor riders, and a city-wide car "
     "mode-share change of a few percentage points at most in the first years of operation.")
body("The measured Yerevan field survey supports treating this cautiously rather than "
     "optimistically. The daytime kerb is dominated by short-stay visitors \u2014 about 63% of "
     "vehicles stay one hour or less and 77% two hours or less \u2014 while genuine all-day "
     "commuters, the group most readily moved to transit, are only around 6% of observed "
     "vehicles. The commuter trips that a BRT is best placed to absorb are therefore a small "
     "fraction of the demand competing for the kerb. Mode shift is a real but slow-acting "
     "contribution to relieving parking pressure; it is not a substitute for the parking "
     "measures set out in this report.",
     bold_lead="Consistency with the local measurement. ")
body("The case for removing kerb parking along the alignment does not rest on mode shift and "
     "should not be made to. It rests on the directly measured finding that peak displaced "
     "demand across the surveyed areas was 908 vehicles against 1,643 spaces removed \u2014 55% \u2014 so "
     "the displaced demand is materially smaller than the supply withdrawn, provided the "
     "absorbing capacity is actually made available. Mode shift is a second-order benefit that "
     "accrues on top of that, over years rather than months, and it should be presented as such.",
     bold_lead="Where the argument should rest instead. ")

# ============================================================ 6. RELIABILITY
heading("6. Reliability of these figures")
body("Every percentage in Tables 1 to 3 derives from a rider reporting, after the fact, what "
     "they used to do. The sources are explicit that this method has systematic biases, all of "
     "which push in the same direction \u2014 towards overstating car diversion.")
bullet("respondents retrospectively overestimate how bad the old car trip was, to rationalise "
       "the switch they have already made.", bold_lead="Recall and rationalisation bias \u2014 ")
bullet("riders over-report having switched from driving alone, to present an environmentally "
       "conscious choice to the surveyor.", bold_lead="Social-desirability bias \u2014 ")
bullet("onboard surveys reach only the people still using the system. Those who tried the BRT and "
       "went back to driving \u2014 because of crowding or unreliability \u2014 are invisible, which "
       "inflates the apparent shift.", bold_lead="Survivor bias \u2014 ")
bullet("surveys run soon after opening can capture novelty behaviour that reverts once traffic "
       "reaches a new equilibrium. This is why the interval in the third column of each table "
       "matters, and why the Los Angeles pair is instructive.", bold_lead="Honeymoon effect \u2014 ")
bullet("a rider survey measures a share of people or trips, not distance travelled or vehicle-"
       "kilometres removed. Household travel surveys give the complete picture; traffic counts "
       "give objective volumes but cannot attribute them to mode switching.",
       bold_lead="What the metric is not \u2014 ")
callout("The sources caution specifically against using corridor rider-survey percentages to claim "
        "a city-wide reduction in car use. Any figure carried into the report should be labelled "
        "with what it measures, when it was measured, and how long after opening.")

# ============================================================ 7. QUARANTINE
heading("7. Figures encountered but not recommended for citation")
body("The literature search returned the following additional figures that could not be traced "
     "to an identifiable primary source, or that contradict a peer-reviewed value for the same "
     "corridor. They are recorded here so the project file is complete, and so they are not "
     "re-discovered later and used in good faith. They should not appear in the report.",
     color=GREY, size=10)
caption("Table 4 \u2014 Untraceable or contradicted figures (do not cite)")
table(
    ["City / corridor", "Figure reported", "Why it is not used"],
    [["Istanbul, Metrob\u00fcs", "40% of riders previously by car", "Contradicts the peer-reviewed 4\u20139% for the same corridor; appears only in a secondary table"],
     ["Adelaide, O-Bahn", "40%", "Traceable only to an unpublished synthesis document with no source URL"],
     ["Bogot\u00e1, TransMilenio", "2.4%", "Same unpublished synthesis; contradicts the 9% in the FTA study"],
     ["Nantes, Busway", "30%", "Same unpublished synthesis; the peer-reviewed value for the same corridor is 29%"],
     ["Curitiba, RIT", "9%, and \u201cone third of residents\u201d", "Same unpublished synthesis; no survey year, and Curitiba opened in 1974"],
     ["Mexico City, Metrob\u00fas", "6%", "Same unpublished synthesis; no survey year stated"],
     ["Beijing, BRT Line 1", "25%", "Secondary table; contradicts the 12% in the peer-reviewed review"],
     ["Houston / Vancouver / Las Vegas / Nagoya", "23%, 23%, 23%, 10%", "Secondary compilation table with no year or method for any entry"]],
    widths=[1.75, 1.7, 3.35], hdr_fill="8A2020")
callout("One further source imported by the automated search was an AI-generated encyclopaedia "
        "page. It contributed no figure used above and should be disregarded entirely.",
        lead="Source hygiene. ")

# ============================================================ 8. PROPOSED TEXT
heading("8. Proposed insertion text (short form)")
body("If a single paragraph is preferred to the full subchapter, the following is the minimum "
     "defensible statement and can be inserted directly into the mitigation-measures discussion "
     "under M0.", color=GREY, size=10)
p = doc.add_paragraph()
p.paragraph_format.left_indent = Inches(0.25)
p.paragraph_format.right_indent = Inches(0.25)
r = p.add_run(
    "International experience indicates that the corridor itself absorbs a real but modest share "
    "of private-car travel, and that the size of that share depends on what the BRT replaces. "
    "Rider surveys on European and North American corridors report that between 5% and 29% of "
    "passengers previously made the same trip by car \u2014 Istanbul\u2019s Metrob\u00fcs, the nearest regional "
    "comparator, recorded 4\u20139% five years after opening. Where BRT is built over an existing "
    "dense bus or minibus network, however, the figure falls to the low single digits: 9% in "
    "Bogot\u00e1, 4% in Lagos and Lahore, 1.4% in Guangzhou, and effectively zero in the surveyed "
    "Soweto corridor of Johannesburg, because the great majority of riders transfer from services "
    "they were already using rather than from cars. Yerevan\u2019s corridors follow existing "
    "high-ridership public-transport spines and should therefore be planned on the lower "
    "assumption. This is consistent with the field survey, which found that genuine all-day "
    "commuters \u2014 the trips a BRT is best able to absorb \u2014 account for only about 6% of observed "
    "kerb parking, against 63% staying one hour or less. Modal shift should accordingly be "
    "treated as a gradual, second-order contribution to relieving parking pressure rather than as "
    "a substitute for the parking measures proposed here; the case for the kerb reallocation "
    "rests on the directly measured finding that peak displaced demand equals only 55% of the "
    "spaces removed.")
r.font.size = Pt(10)
r.italic = True

heading("Sources", level=2)
for s in [
    "Effects of new bus and rail rapid transit systems \u2013 an international review. Technical "
    "University of Denmark (peer-reviewed).",
    "Federal Transit Administration, Metro Orange Line BRT Project Evaluation, FTA Report No. 0004.",
    "Federal Transit Administration, Applicability of Bogot\u00e1\u2019s TransMilenio BRT System to the "
    "United States (2006).",
    "Federal Transit Administration, Boston Silver Line BRT report.",
    "ITDP, Bus Rapid Transit Planning Guide (2007), and the online BRT Planning Guide chapters on "
    "corridor selection and traffic-volume estimation.",
    "Clean Air Asia, Initiating Bus Rapid Transit in Jakarta, Indonesia.",
    "Lagos BRT-Lite: Africa\u2019s First Bus Rapid Transit Scheme \u2014 Scheme Evaluation Summary Report.",
    "Batool et al., A Policy Move towards Sustainable Urban Transport in Pakistan: Measuring the "
    "Social, Environmental and Economic Impacts of the Lahore BRT System. Lahore School of Economics.",
    "Impact of \u2018light\u2019 bus rapid transit (BRT-light) on traffic and emissions in a travel corridor.",
    "Wilshire BRT Before and After Report (2017).",
]:
    b = doc.add_paragraph(style="List Bullet")
    rr = b.add_run(s)
    rr.font.size = Pt(8.5)
    rr.font.color.rgb = GREY

source_note("Compiled 24 July 2026 from a structured review of 50 international sources. "
            "Figures are reproduced as stated in the sources; where a source did not state a survey "
            "year or an opening year, this is shown rather than inferred.")

doc.save(OUT)
print("Saved:", OUT)
