"""Optional Pillow evidence layout; not part of the catalogue build."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path('docs/evidence/pilot-06')
for phase in ('before', 'after'):
    sheet = Image.new('RGB', (1200, 1560), '#eee')
    draw = ImageDraw.Draw(sheet)
    for i, spell in enumerate((97, 117, 131)):
        for j, width in enumerate((1440, 390)):
            for k, state in enumerate(('initial', 'active')):
                image = Image.open(root / f'{phase}-ds-{spell}-{width}-hosted-{state}.png')
                image.thumbnail((575, 232))
                x = k * 600 + (600 - image.width) // 2
                y = (i * 2 + j) * 260
                sheet.paste(image, (x, y))
                draw.text((x, y + 235), f'ds-{spell} / {width} / {state}', fill='black')
    sheet.save(root / f'{phase}-contact-sheet.png')

dark = Image.new('RGB', (800, 780), '#eee')
draw = ImageDraw.Draw(dark)
for i, spell in enumerate((97, 117, 131)):
    for k, state in enumerate(('initial', 'active')):
        image = Image.open(root / f'after-dark-ds-{spell}-390-hosted-{state}.png')
        image.thumbnail((370, 228))
        x = k * 400 + (400 - image.width) // 2
        y = i * 260
        dark.paste(image, (x, y))
        draw.text((x, y + 232), f'ds-{spell} / dark / {state}', fill='black')
dark.save(root / 'after-dark-contact-sheet.png')
