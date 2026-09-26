"""Optional evidence utility: requires Pillow; not part of generation/build."""
from pathlib import Path
from PIL import Image, ImageDraw
root=Path('docs/evidence/pilot-02')
for phase in ['before','after']:
    variants=[''] if phase=='before' else ['no-preference-light-','reduce-light-','no-preference-dark-','reduce-dark-']
    for width in [1440,390]:
        for variant in variants:
            files=[root/phase/f'{i}-{width}-{variant}{state}.jpg' for i in [111,93,134,30,55,69] for state in ['initial','active']]
            sheet=Image.new('RGB',(1200,3*330),'#e9e9e6');draw=ImageDraw.Draw(sheet)
            for i,f in enumerate(files):
                im=Image.open(f);im.thumbnail((300,300));x=(i%4)*300;y=(i//4)*330;sheet.paste(im,(x,y));draw.text((x+5,y+304),f.name,fill='black')
            sheet.save(root/f'{phase}-{width}-{variant}contact.jpg',quality=90)
