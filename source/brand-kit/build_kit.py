# eki.labs brand kit: logos, colour, type and social formats in one folder and one zip.
# Run: python3 build_kit.py <out_dir>   → <out_dir>/eki-labs-brand-kit/ and <out_dir>/eki-labs-brand-kit.zip
import json, os, shutil, struct, subprocess, sys, zipfile
from PIL import Image, ImageDraw, ImageFont
import logos, social

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, 'fonts_dl')

# The 16 tokens of /brand, with the job each one does (same names and values as the site).
COLOURS = [
    ('Brand', [('sol', '#FFD54A', 'Energy. The key figure, once per piece, and the horizon of the logo\u2019s sun gradient. Never a button or a text colour.'),
               ('yerba', '#58E9AE', 'Crops, and actions on dark: the one colour you can press.'),
               ('tierra', '#CF8166', 'Land and rural life, on dark grounds.'),
               ('noche', '#0A100C', 'Ink, infrastructure and dark chapters. Our black, with a green cast.')]),
    ('Deep', [('yerba honda', '#056C4A', 'Yerba as text and labels on light grounds.'),
              ('tierra honda', '#964A2F', 'Tierra as text and data on light grounds.'),
              ('origen', '#311D16', 'Deep ground for origins and the farmer chapters.'),
              ('bosque', '#0A281A', 'Deep green ground for food and crops.')]),
    ('Base', [('arena', '#F4F2EC', 'Page background: the open field.'),
              ('piedra', '#EBE6D8', 'Surfaces, cards and bands.'),
              ('linea', '#D6D1C3', 'Rules and borders on light grounds.'),
              ('pizarra', '#555A52', 'Secondary text on light grounds.'),
              ('grafito', '#141B16', 'Surfaces on dark grounds.'),
              ('acero', '#2B332D', 'Rules and borders on dark grounds.'),
              ('niebla', '#A1A69F', 'Secondary text on dark grounds.'),
              ('blanco', '#FFFFFF', 'Only inside other people’s surfaces (email, documents). Never as our background.')]),
]


def rgb(hx): return tuple(int(hx[i:i + 2], 16) for i in (1, 3, 5))
def slug(n): return n.replace(' ', '-')


def write_ase(path):
    """Adobe Swatch Exchange: one group per family, global RGB swatches."""
    def ustr(s):
        s = s + '\0'
        return struct.pack('>H', len(s)) + s.encode('utf-16-be')
    blocks = []
    for group, items in COLOURS:
        name = ustr(f'eki.labs · {group}')
        blocks.append(struct.pack('>HI', 0xC001, len(name)) + name)
        for n, hx, _ in items:
            r, g, b = (v / 255 for v in rgb(hx))
            body = ustr(n) + b'RGB ' + struct.pack('>fffH', r, g, b, 0)
            blocks.append(struct.pack('>HI', 0x0001, len(body)) + body)
        blocks.append(struct.pack('>HI', 0xC002, 0))
    open(path, 'wb').write(b'ASEF' + struct.pack('>HHI', 1, 0, len(blocks)) + b''.join(blocks))


def write_colours(d):
    os.makedirs(d, exist_ok=True)
    write_ase(os.path.join(d, 'eki-labs-colours.ase'))
    css = ['/* eki.labs colours · one name, one job each. Same values as ekilabs.com/brand. */', ':root {']
    data = {'name': 'eki.labs colours', 'source': 'ekilabs.com/brand', 'groups': []}
    for group, items in COLOURS:
        css.append(f'  /* {group} */')
        g = {'group': group, 'colours': []}
        for n, hx, use in items:
            css.append(f'  --eki-{slug(n)}: {hx};  /* {use} */')
            g['colours'].append({'name': n, 'token': f'--eki-{slug(n)}', 'hex': hx, 'rgb': list(rgb(hx)), 'use': use})
        data['groups'].append(g)
    g = lambda stops: ', '.join(f'{c} {round(o * 100)}%' for o, c in stops)
    css.append('  /* Logo only, top to bottom of the symbol\'s circle. Not palette colours. */')
    css.append(f'  --eki-logo-sun: linear-gradient(180deg, {g(logos.SUN_STOPS)});  /* the sun (and the horizon sun) */')
    css.append(f'  --eki-logo-sun-full: linear-gradient(180deg, {g(logos.FULL_STOPS)});  /* option: the whole symbol */')
    data['logo_gradients'] = {
        'use': 'Logo and horizon sun only, top to bottom of the symbol circle. Not palette colours.',
        'sun': [{'offset': o, 'hex': c} for o, c in logos.SUN_STOPS],
        'full': [{'offset': o, 'hex': c} for o, c in logos.FULL_STOPS]}
    css.append('}')
    open(os.path.join(d, 'eki-labs-colours.css'), 'w', encoding='utf-8').write('\n'.join(css) + '\n')
    open(os.path.join(d, 'eki-labs-colours.json'), 'w', encoding='utf-8').write(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    # a swatch card to see them at a glance
    W, pad, cw, ch, gap = 2400, 120, 495, 300, 40
    H = pad * 2 + 90 + sum(110 + ((len(it) + 3) // 4) * (ch + 150) for _, it in COLOURS)
    im = Image.new('RGB', (W, H), '#F4F2EC'); dr = ImageDraw.Draw(im)
    zs = ImageFont.truetype(os.path.join(FD, 'zillaslab_ZillaSlab-Regular.ttf'), 72)
    gm = ImageFont.truetype(os.path.join(FD, 'geistmono_GeistMono[wght].ttf'), 26); gm.set_variation_by_axes([500])
    ws = ImageFont.truetype(os.path.join(FD, 'worksans_WorkSans[wght].ttf'), 34)
    dr.text((pad, pad), 'eki.labs · colours', font=zs, fill='#0A100C')
    y = pad + 150
    for group, items in COLOURS:
        dr.text((pad, y), group.upper(), font=gm, fill='#555A52'); y += 60
        for i, (n, hx, _) in enumerate(items):
            x = pad + (i % 4) * (cw + gap); yy = y + (i // 4) * (ch + 150)
            dr.rounded_rectangle((x, yy, x + cw, yy + ch), 24, fill=hx, outline='#D6D1C3' if hx in ('#FFFFFF', '#F4F2EC', '#EBE6D8') else None, width=2)
            dr.text((x, yy + ch + 22), n, font=ws, fill='#0A100C')
            r, g, b = rgb(hx)
            dr.text((x, yy + ch + 70), f'{hx}  ·  {r} {g} {b}', font=gm, fill='#555A52')
        y += ((len(items) + 3) // 4) * (ch + 150) + 50
    im.save(os.path.join(d, 'eki-labs-colours.png'), optimize=True)


TYPE = [('zilla-slab', 'Zilla Slab', ['zillaslab_ZillaSlab-Light.ttf', 'zillaslab_ZillaSlab-Regular.ttf', 'zillaslab_ZillaSlab-Italic.ttf', 'zillaslab_ZillaSlab-Medium.ttf'], 'zillaslab_OFL.txt'),
        ('work-sans', 'Work Sans', ['worksans_WorkSans[wght].ttf', 'worksans_WorkSans-Italic[wght].ttf'], 'worksans_OFL.txt'),
        ('geist-mono', 'Geist Mono', ['geistmono_GeistMono[wght].ttf'], 'geistmono_OFL.txt')]


def write_type(d):
    for folder, fam, files, lic in TYPE:
        fd = os.path.join(d, folder); os.makedirs(fd, exist_ok=True)
        for f in files: shutil.copy(os.path.join(FD, f), os.path.join(fd, f.split('_', 1)[1]))
        shutil.copy(os.path.join(FD, lic), os.path.join(fd, 'OFL.txt'))


def render_social(files):
    import re
    jobs = []
    for svgp, sizes in files:
        s = open(svgp, encoding='utf-8').read()
        w, h = (int(v) for v in re.search(r'width="(\d+)" height="(\d+)"', s).groups())
        if sizes:
            for px in sizes:
                jobs.append({'svg': svgp, 'out': svgp[:-4] + f'-{px}px.png', 'w': px, 'h': px, 'scale': 1, 'fit': True})
        else:
            jobs.append({'svg': svgp, 'out': svgp[:-4] + '.png', 'w': w, 'h': h, 'scale': 1})
    jp = os.path.join(HERE, 'jobs_kit.json'); json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'render_svgs.mjs'), jp], check=True)


def main(out):
    root = os.path.join(out, 'eki-labs-brand-kit')
    shutil.rmtree(root, ignore_errors=True); os.makedirs(root)
    logos.build(os.path.join(root, '01-logo'))
    write_colours(os.path.join(root, '02-colour'))
    write_type(os.path.join(root, '03-type'))
    files = social.build(os.path.join(root, '04-social'))
    render_social(files)
    shutil.copy(os.path.join(HERE, 'README.md'), os.path.join(root, 'README.md'))
    shutil.copy(os.path.join(HERE, 'SOCIAL-SIZES.md'), os.path.join(root, '04-social', 'SIZES.md'))
    zp = os.path.join(out, 'eki-labs-brand-kit.zip')
    if os.path.exists(zp): os.remove(zp)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for dp, _, fs in os.walk(root):
            for f in sorted(fs):
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, out))
    # one zip per part, for the download cards on /brand
    for part, name in (('01-logo', 'eki-labs-logos'), ('02-colour', 'eki-labs-colours'), ('03-type', 'eki-labs-type'), ('04-social', 'eki-labs-social')):
        zp2 = os.path.join(out, name + '.zip')
        if os.path.exists(zp2): os.remove(zp2)
        with zipfile.ZipFile(zp2, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            z.write(os.path.join(root, 'README.md'), os.path.join(name, 'README.md'))
            for dp, _, fs in os.walk(os.path.join(root, part)):
                for f in sorted(fs):
                    full = os.path.join(dp, f)
                    z.write(full, os.path.join(name, os.path.relpath(full, root)))
        print(name, round(os.path.getsize(zp2) / 1e6, 2), 'MB')
    n = sum(len(fs) for _, _, fs in os.walk(root))
    print('kit', root, 'files', n, 'zip MB', round(os.path.getsize(zp) / 1e6, 1))


if __name__ == '__main__':
    main(sys.argv[1])
