"""Optional evidence utility: requires Pillow; not part of generation/build.

Builds before/after contact sheets for Pilot 05 (ds-66, ds-75, ds-77, ds-106)
from the raw captures in docs/evidence/pilot-05. Each sheet is an 8x4 grid:
columns = 1440 initial/active/fallback/reduced-active then 390
initial/active/fallback/reduced-active, rows = the four spells.
Deterministic for a given set of source captures.
"""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path('docs/evidence/pilot-05')
spells = [66, 75, 77, 106]
states = ['initial', 'active', 'fallback', 'reduced-active']
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
