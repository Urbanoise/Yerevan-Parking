# -*- coding: utf-8 -*-
"""Fill the Consultant Response column of the reviewer's comments spreadsheet.

Reads  Final Presentation/Parking Reports Comments spreadsheet.xlsx
Writes Final Presentation/Parking Reports Comments spreadsheet - responses 30072026.xlsx

The reviewer's own file is left untouched; the response copy is what goes back. Each
response is matched to its row by a distinctive fragment of the Issue text rather than
by row number, so a re-ordered or edited source sheet fails loudly instead of writing
answers against the wrong comments.
"""
import os
import shutil

import openpyxl
from openpyxl.styles import Alignment, Font

import report_figures as rf

FP = os.path.join(rf.ROOT, "Final Presentation")
SRC = os.path.join(FP, "Parking Reports Comments spreadsheet.xlsx")
DST = os.path.join(FP, "Parking Reports Comments spreadsheet - responses 30072026.xlsx")

S, F, V = rf.supply(), rf.survey(), rf.vehicles()
A = F["all"]
OC = S["on_corridor"]

O8 = "Output 8 - Parking Surveys and Analysis Report 12082026 (rev).docx"
O10 = "Output 10 - Parking Analysis Report - 30072026 (rev).docx"

# key fragment of the Issue cell -> response
RESPONSES = {
    # ---------------- Output 8 ----------------
    # verbatim from the workbook the user edited on 12 Aug 2026 - do not
    # reword these; the house style below is derived from them
    'number of parking spaces removed data is not consistent':
        "Addressed. Every impact figure has been re-derived from the latest "
        "conceptual design. Total spaces retained: 1,220",

    'Oversimplifies the impact of BRT cross section on parking':
        "Agreed and corrected. 'Nature of the Impact' has been rewritten.",

    'Mistakenly asserts that the BRT configuration "leaves no room for parking"':
        "Agreed and corrected. The text now states that where the right-of-way is "
        "fully consumed no kerbside parking can be retained, but that between "
        "stations the cross-section is less demanding and in most such sections "
        "room for parking remains which is why 1,220 spaces are retained or "
        "re-established.",

    "I don't understand what the 55% represents":
        "Clarified, and the figure is now 59% on the refreshed data. The ratio is "
        "defined in full at first use.",

    'Occupancy rates of >100% are sighted':
        "Clarified with a dedicated explanation at first use.",

    'Minimal information on the occupancy surveys':
        "Addressed. New chapter, 'Field Occupancy Survey: Methodology, Locations "
        "and Results', reporting the survey location by location.",

    # ---------------- Output 10 ----------------
    "it mentions 'patrol vehicles'":
        "Clarified: enforcement is entirely pole-fixed ANPR camera based. The "
        "'patrol vehicle' reference has been removed and Section 2.9 rewritten.",

    'yet there are no details in Output 8':
        "Addressed. Output 8 now carries a full field occupancy survey chapter: "
        "methodology, the six locations, and results by area.",

    'the first Par. Of Chapter 5 still blames the loss of parking':
        "Agreed and corrected. The chapter opening now attributes the loss to "
        "reallocating the full right-of-way, not to the median alignment.",

    'Parking units retained after implementatoin of BRT needs to be caveated':
        f"Addressed. The retention figure is refreshed to {S['retained']:,} spaces "
        f"of {OC:,} ({S['retained_pct']:.0f}%) on the latest conceptual design.",

    'Report says that there is no parking in the public housing estates':
        f"Agreed and corrected. The text now records the substantial informal "
        f"parking between the blocks; Malatia-Sebastia has the lowest peak kerb "
        f"pressure of the six areas ({F['areas']['malatia']['peak_pct']}%).",

    'The text overstates the lack of parking along Arshakuniats':
        f"Agreed and corrected. The claim has been removed; parking is retained "
        f"where the right-of-way allows. Corridor 1 retains "
        f"{S['corridors']['Corridor 01']['retained']} spaces.",

    'Conceptual designs must incorporate designated loading bays':
        "Clarified - they do. The sentence now states that the designs provide "
        "designated loading bays at commercial concentrations, sized to the measured "
        "freight pockets.",

    'It seems like the annual passes could be a problem':
        "Agreed. New measure added: 'Withdraw the flat annual parking permit'. "
        "Uptake data has not been released by Parking City Service.",

    'park and ride is recommended':
        "Agreed and removed. All references deleted, including from Figure 10; one "
        "sentence records that it was considered and is not recommended.",

    'Section needs some sort of conclusion':
        "Addressed. New closing subsection, 'Conclusion of the mitigation "
        "framework'. The summary image has been moved to Chapter 7.",

    'no mention of adjusting existing parking charges to achieve 85% occupancy':
        "Agreed. New measure added: 'Adjust parking charges towards 85% "
        "occupancy', with tariffs set zone by zone against the target.",

    'Later removing the annual pass is mentioned tepidly':
        "Agreed. It is now a full measure in the framework; the earlier note has "
        "been rewritten to point at it.",

    'Does Yerevan have the same issue of abandoned vehicles':
        f"Addressed. New measure added: 'Remove derelict and long-term abandoned "
        f"vehicles'. The survey found only {V['all']['stationary_all_window']} such "
        f"vehicles of {V['all']['distinct_plates']:,} observed.",

    'text blames soviet era housing estates for not having parking':
        "Agreed and removed. The paragraph now keeps only the structural fact that "
        "the blocks were laid out before mass car ownership.",

    "'open residential yards' are a 'committed pre-condition'":
        "Explained. A short definition is added at first use, and 'prerequisite' is "
        "now used throughout.",

    'resident parking permits be limited to 1 per household and charged':
        "Agreed and rewritten as directed: one permit per household, charged at a "
        "modest annual fee. A second vehicle pays the standard tariff.",

    'What is a "Load Bearing committed precondition"':
        "Explained, and the term retired. 'Prerequisite' is now used throughout.",

    'summary image about mitigation measures is in the section about open residential':
        "Agreed and moved. The image now sits in Chapter 7 beside Figure 10.",

    'A first step may need to be institutional':
        "Agreed. New subsection added, 'Institutional Responsibility for Delivery', "
        "recommending the Transport Department as accountable owner, with a table "
        "assigning each measure.",

    "you've moved Komitas into a high rather than medium sensitivity zone":
        f"Agreed and corrected throughout. Komitas runs at "
        f"{F['areas']['komitas']['peak_pct']}% peak occupancy with "
        f"{F['areas']['komitas']['absorbed_onstreet_pct']}% on-street absorption, and "
        f"is shown as High in Figure 10 and in Output 8.",

    'Park and ride still mentioned':
        "Agreed and removed. The lower-sensitivity package no longer lists it.",

}


def main():
    shutil.copyfile(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    used, filled = set(), 0

    for ws in wb.worksheets:
        # locate the header row and the Issue / Consultant Response columns
        head_row = issue_col = resp_col = None
        for r in range(1, 6):
            vals = {str(ws.cell(r, c).value).strip().lower(): c
                    for c in range(1, ws.max_column + 1) if ws.cell(r, c).value}
            if "issue" in vals:
                head_row, issue_col = r, vals["issue"]
                resp_col = vals.get("consultant response")
                break
        if issue_col is None:
            continue
        if resp_col is None:
            resp_col = ws.max_column + 1
            ws.cell(head_row, resp_col, "Consultant Response")

        ws.column_dimensions[ws.cell(head_row, resp_col).column_letter].width = 85

        for r in range(head_row + 1, ws.max_row + 1):
            issue = ws.cell(r, issue_col).value
            if not issue:
                continue
            issue = " ".join(str(issue).split())
            match = next((k for k in RESPONSES
                          if " ".join(k.split()).lower() in issue.lower()), None)
            if match is None:
                print(f"  !! no response for {ws.title} row {r}: {issue[:70]}")
                continue
            used.add(match)
            cell = ws.cell(r, resp_col, RESPONSES[match])
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.font = Font(size=9)
            filled += 1

    unused = set(RESPONSES) - used
    if unused:
        print("  !! responses that matched no row:")
        for u in unused:
            print("     -", u[:70])

    wb.save(DST)
    print(f"WROTE: {DST}")
    print(f"       {filled} responses written, {len(unused)} unmatched")


if __name__ == "__main__":
    main()
