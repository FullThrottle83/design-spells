"""Optional evidence utility: requires Pillow; not part of generation/build.

Builds before/after contact sheets for Pilot 04 (ds-79, ds-89, ds-142) from
the raw captures in docs/evidence/pilot-04. Each sheet is a 6x3 grid:
columns = 1440 initial/active/fallback then 390 initial/active/fallback,
rows = the three spells. Deterministic for a given set of source captures.
"""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path('docs/evidence/pilot-04')
spells = [79, 89, 142]
states = ['initial', 'active', 'fallback']
widths = [1440, 390]

cell_w, cell_h = 200, 300
label_h = 18
cols = len(widths) * len(states)
sheet_size = (cols * cell_w, len(spells) * (cell_h + label_h))

for phase in ['before', 'after']:
    sheet = Image.new('RGB', sheet_size, '#e9e9e6')
    draw = ImageDraw.Draw(sheet)
    for r, spell in enumerate(spells):
        for c, (w, state) in enumerate(
            [(w, s) for w in widths for s in states]
        ):
            f = root / f'{phase}-ds-{spell}-{w}-{state}.png'
            if not f.exists():
                draw.text((c * cell_w + 5, r * (cell_h + label_h) + 5),
                          f'missing {f.name}', fill='#a00')
                continue
            im = Image.open(f).convert('RGB')
            im.thumbnail((cell_w - 8, cell_h - 8))
            x = c * cell_w + (cell_w - im.width) // 2
            y = r * (cell_h + label_h) + (cell_h - im.height) // 2
            sheet.paste(im, (x, y))
            draw.rectangle([c * cell_w, r * (cell_h + label_h) + cell_h,
                            (c + 1) * cell_w, r * (cell_h + label_h) + cell_h + label_h],
                           fill='#e9e9e6')
            draw.text((c * cell_w + 5, r * (cell_h + label_h) + cell_h + 3),
                      f'ds-{spell} {w}px {state}', fill='black')
    out = root / f'{phase}-contact-sheet.png'
    sheet.save(out)
    print('wrote', out)
