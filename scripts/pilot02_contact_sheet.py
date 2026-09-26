"""Optional evidence utility: requires Pillow; not part of generation/build."""
from pathlib import Path
from PIL import Image, ImageDraw
root=Path('docs/evidence/pilot-02')
for phase in ['before','after']:
    variants=[''] if phase=='before' else ['no-preference-light-','reduce-light-','no-preference-dark-','reduce-dark-']
    for width in [1440,390]:
        for variant in variants:
            files=[root/phase/f'{i}-{width}-{variant}{state}.jpg' for i in [111,93,134,30,55,69] for state in ['initial','active']]
            tile_height=210 if width==1440 else 330
            image_height=188 if width==1440 else 300
            sheet=Image.new('RGB',(1200,3*tile_height),'#e9e9e6');draw=ImageDraw.Draw(sheet)
            for i,f in enumerate(files):
                im=Image.open(f);im.thumbnail((300,image_height));x=(i%4)*300;y=(i//4)*tile_height;sheet.paste(im,(x,y));draw.text((x+5,y+image_height+4),f'ds-{f.name.split("-")[0]} / {f.stem.split("-")[-1]}',fill='black')
            sheet.save(root/f'{phase}-{width}-{variant}contact.jpg',quality=90)

files=[root/'fallback'/f'{i}-390-no-preference-light-active.jpg' for i in [111,93,55,69]]
if all(f.exists() for f in files):
    sheet=Image.new('RGB',(800,455),'#e9e9e6')
    for i,f in enumerate(files):
        im=Image.open(f);im.thumbnail((200,430));sheet.paste(im,(i*200,0))
        ImageDraw.Draw(sheet).text((i*200+5,435),f'ds-{f.name.split("-")[0]} / simulated fallback',fill='black')
    sheet.save(root/'fallback-mobile-contact.jpg')
