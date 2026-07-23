# Builds "Parking Slides - 23072026.pptx" from the 22 Jul deck by applying the
# Corridor 1+2-only figure set. Targeted python-pptx edits on a copy — the deck carries
# hand edits that a regenerate would destroy, so the generator is deliberately not used.
#
# Scope change behind every number here: Corridor 03 is withheld pending its conceptual
# design, and the Nalbandyan016 segment (14 Zone A spaces, tagged impact=corridor but
# lying wholly outside every corridor boundary) is excluded. All figures are derived
# from the same GeoJSON the web app serves.
import shutil
from pptx import Presentation
from pptx.util import Inches

SRC = r'C:/Users/user/Yerevan-Parking/Final Presentation/Parking Slides - 22072026.pptx'
DST = r'C:/Users/user/Yerevan-Parking/Final Presentation/Parking Slides - 23072026.pptx'

# --- figures (C1+C2 only) -----------------------------------------------------------
ON_CORRIDOR = 6095          # impact=corridor, C1+C2
ON_STREET, ON_SEGS = 7825, 606      # corridor + buffer, matching the old 8,862 basis
OFF_STREET, OFF_FAC = 6732, 239     # excludes the withdrawn NalbandyanPavstocByuzand
TOTAL = ON_STREET + OFF_STREET      # 14,557
# per-corridor removal, derived rather than typed: this line drifted out of step with
# the total once Nalbandyan016's 14 spaces left the Corridor 1 base (2,363 -> 2,349),
# leaving the deck showing 1,494 + 3,395 = 4,889 beside a card reading 4,875.
C1_EXISTING, C1_RETAINED = 2349, 869
C2_EXISTING, C2_RETAINED = 3746, 351
C1_REMOVED = C1_EXISTING - C1_RETAINED      # 1,480
C2_REMOVED = C2_EXISTING - C2_RETAINED      # 3,395
REMOVED, RETAINED = C1_REMOVED + C2_REMOVED, C1_RETAINED + C2_RETAINED
assert (REMOVED, RETAINED) == (4875, 1220), (REMOVED, RETAINED)
FREE, ZONE_B, ZONE_A, TAXI = 5248, 534, 246, 67
assert FREE + ZONE_B + ZONE_A + TAXI == ON_CORRIDOR == C1_EXISTING + C2_EXISTING

pc = lambda v: 100.0 * v / ON_CORRIDOR

TEXT_EDITS = {
    2: {
        'TextBox 3':  'Across Corridors 1 and 2 and 100 m buffer',
        'TextBox 8':  f'{TOTAL:,}',
        'TextBox 12': f'{ON_STREET:,}',
        'TextBox 13': f'On-street, across {ON_SEGS} segments',
        'TextBox 16': f'{ON_CORRIDOR:,}',
        'TextBox 20': f'{OFF_STREET:,}',
        'TextBox 21': f'Off-street, across {OFF_FAC} facilities',
        'TextBox 22': f'On-corridor on-street supply by regulatory zone ({ON_CORRIDOR:,} spaces)',
        'TextBox 28': f'Free / unregulated  {FREE:,} ({pc(FREE):.1f}%)',
        'TextBox 30': f'Zone B (blue) – paid  {ZONE_B} ({pc(ZONE_B):.1f}%)',
        'TextBox 32': f'Zone A (red) – paid  {ZONE_A} ({pc(ZONE_A):.1f}%)',
        'TextBox 34': f'Taxi  {TAXI} ({pc(TAXI):.1f}%)',
        'TextBox 37': f'{pc(FREE):.0f}% of corridor parking is free of charge — and barely organized',
        # markings rises 12% -> 14% because every marked space is on C1+C2; Nalbandyan
        # drops 83 -> 69 with the out-of-boundary segment gone.
        'TextBox 38': ('•  Only 20% has signage and 14% has markings. Zone A is concentrated in '
                       'Kentron (Nalbandyan 69, Abovyan 46, Amiryan 43); Zone B is almost entirely '
                       'Komitas Avenue (522 of 534).'),
    },
    6: {
        'TextBox 3':  f'The conceptual cross-section removes {100 * REMOVED / ON_CORRIDOR:.0f}% of on-corridor parking',
        'TextBox 6':  'CORRIDORS 1 & 2 · impact of the conceptual design',
        'TextBox 7':  f'Corridor 1: {C1_REMOVED:,}  ·  Corridor 2: {C2_REMOVED:,}',
        'TextBox 10': f'{ON_CORRIDOR:,}',
        'TextBox 14': f'{REMOVED:,}',
        'TextBox 18': f'{100 * REMOVED / ON_CORRIDOR:.0f}%',
        'TextBox 22': f'{RETAINED:,}',
        'TextBox 42': ('The 55% is the displaced demand set against the spaces removed in the same six '
                       'areas (908 vehicles ÷ 1,643 spaces): the kerb is not full at the moment, so '
                       'fewer vehicles need re-homing than spaces are lost. Corridor-wide figures cover '
                       'Corridors 1 and 2 only — Corridor 3 is excluded pending its conceptual design '
                       '— and will be updated once that design is finalized.'),
    },
}

# Stacked regulatory bar on slide 2: the segment widths encode the shares, so the text
# edits above are not enough on their own. Rebuilt left-to-right across the same span.
BAR_L, BAR_W = 0.240, 9.520
BAR_SEGMENTS = [('Rectangle 23', FREE), ('Rectangle 24', ZONE_B),
                ('Rectangle 25', ZONE_A), ('Rectangle 26', TAXI)]


def set_text(shape, new):
    """Replace a shape's text, keeping the first run's formatting.

    Hand-editing in PowerPoint has split these paragraphs into several runs that all
    share the same size/bold/colour, so collapsing to one run is lossless here — and
    far safer than text_frame.text, which drops formatting entirely.
    """
    para = shape.text_frame.paragraphs[0]
    if not para.runs:
        raise ValueError(f'{shape.name}: no runs to inherit formatting from')
    para.runs[0].text = new
    for run in para.runs[1:]:
        run._r.getparent().remove(run._r)


shutil.copyfile(SRC, DST)
prs = Presentation(DST)

applied, missing = 0, []
for idx, edits in TEXT_EDITS.items():
    slide = prs.slides[idx - 1]
    by_name = {sh.name: sh for sh in slide.shapes}
    for name, new in edits.items():
        if name not in by_name:
            missing.append(f'slide {idx} / {name}')
            continue
        before = by_name[name].text_frame.text
        set_text(by_name[name], new)
        if before != new:
            print(f'  s{idx} {name:<12} {before[:58]!r}\n       -> {new[:58]!r}')
        applied += 1

# rebuild the stacked bar
slide2 = {sh.name: sh for sh in prs.slides[1].shapes}
cursor = BAR_L
for name, value in BAR_SEGMENTS:
    if name not in slide2:
        missing.append(f'slide 2 / {name}')
        continue
    width = BAR_W * value / ON_CORRIDOR
    slide2[name].left = Inches(cursor)
    slide2[name].width = Inches(width)
    print(f'  s2 {name:<12} L={cursor:.3f}" W={width:.3f}"  ({value} = {pc(value):.1f}%)')
    cursor += width
assert abs(cursor - (BAR_L + BAR_W)) < 1e-6, f'bar segments end at {cursor}, expected {BAR_L + BAR_W}'

prs.save(DST)
print(f'\n{applied} text edits applied; bar rebuilt.')
if missing:
    print('MISSING SHAPES (nothing written for these):')
    for m in missing:
        print('   ', m)
print('Saved ->', DST)
