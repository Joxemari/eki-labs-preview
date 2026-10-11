# eki.labs brand kit · logo files.
# Masters in ./masters: eki-labs-dia.svg (symbol + wordmark, outlined) and the lockups (logo + tagline, outlined).
# Every file is cropped tight to the artwork; the clear space rule (¼ of the symbol's diameter) is in the README.
import io, os, re
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(HERE, 'masters')
SOL, NOCHE, ARENA, WHITE = '#FFD54A', '#0A100C', '#F4F2EC', '#FFFFFF'
WAYS = {  # colourway: (sun, ink)
    'day': (SOL, NOCHE), 'night': (SOL, ARENA), 'black': (NOCHE, NOCHE), 'white': (WHITE, WHITE)}


def _read(p):
    return open(os.path.join(MASTERS, os.path.basename(p)), encoding='utf-8').read()


MASTER = _read('revision/assets/eki-labs-dia.svg')
SYM_G = re.search(r'(<g transform="translate\(0 -816\.5\) scale\(9\.23\)">.*?</g>)', MASTER, re.S).group(1)
WORD_G = re.search(r'(<g transform="translate\(1278 0\)">.*?</g>)', MASTER, re.S).group(1)
SYM_PATHS = re.findall(r'<path d="[^"]+" fill="[^"]+"/>', SYM_G)
assert len(SYM_PATHS) == 4


def recolour(svg_body, sun, ink):
    # the sun is the only #ffd54a shape in every master; everything else is ink
    out = re.sub(r'fill="#(?:ffd54a|FFD54A)"', 'fill="@@SUN"', svg_body)
    out = re.sub(r'fill="#(?:0a100c|0A100C|f4f2ec|F4F2EC)"', f'fill="{ink}"', out)
    return out.replace('@@SUN', sun)


def tight_viewbox(body, vb, probe=4000):
    """Crop a viewBox to the drawn pixels (rendered on transparent ground)."""
    x, y, w, h = vb
    W = probe; H = round(probe * h / w)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{W}" height="{H}">{body}</svg>'
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
    bx = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    sx, sy = w / W, h / H
    return (round(x + bx[0] * sx, 2), round(y + bx[1] * sy, 2), round((bx[2] - bx[0]) * sx, 2), round((bx[3] - bx[1]) * sy, 2))


def lockup_body(name):
    s = _read(f'lockup/out/{name}')
    s = re.sub(r'<rect [^>]*/>', '', s, count=1)  # drop the ground: kit files are transparent
    vb = tuple(float(v) for v in re.search(r'viewBox="([^"]+)"', s).group(1).split())
    body = s[s.find('>') + 1:s.rfind('</svg>')]
    return body, vb


def band(y1, y2):
    import math
    def xs(y):
        d = math.sqrt(max(0, 50 * 50 - (y - 50) ** 2)); return 50 - d, 50 + d
    a1, b1 = xs(y1); a2, b2 = xs(y2)
    return f'M{a1:.2f} {y1:.2f}L{b1:.2f} {y1:.2f}A50 50 0 0 1 {b2:.2f} {y2:.2f}L{a2:.2f} {y2:.2f}A50 50 0 0 1 {a1:.2f} {y1:.2f}Z'


# below 32 px the symbol keeps two rows so it stays sharp (same rule as /brand)
SMALL = '<path d="M0 50A50 50 0 0 1 100 50Z" fill="#ffd54a"/>' + ''.join(
    f'<path d="{band(a, b)}" fill="#0a100c"/>' for a, b in [(59.21, 75.0), (84.21, 100)])

MARKS = {
    # name: (body in day colours, viewBox before cropping, png widths)
    'logo': (SYM_G + WORD_G, (0, -816.5, 5042, 923), (1200, 4000)),
    'symbol': (''.join(SYM_PATHS), (0, 0, 100, 100), (512, 2048)),
    'symbol-small': (SMALL, (0, 0, 100, 100), (16, 32, 48, 64)),
    'signature': (lockup_body('lockup-firma-dia.svg')[0], lockup_body('lockup-firma-dia.svg')[1], (1600, 4000)),
    'signature-vertical': (lockup_body('lockup-firma-vertical-dia.svg')[0], lockup_body('lockup-firma-vertical-dia.svg')[1], (1200, 3000)),
}


def svg_file(body, vb, width_px=None):
    x, y, w, h = vb
    wpx = width_px or 480
    hpx = round(wpx * h / w, 2)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{wpx}" height="{hpx}">'
            f'<title>eki.labs</title>{body}</svg>\n')


def build(out_dir):
    made = []
    tight = {k: (vb if k.startswith('symbol') else tight_viewbox(b, vb)) for k, (b, vb, _) in MARKS.items()}
    for mark, (body, _, widths) in MARKS.items():
        d = os.path.join(out_dir, mark); os.makedirs(d, exist_ok=True)
        for way, (sun, ink) in WAYS.items():
            b = recolour(body, sun, ink)
            svg = svg_file(b, tight[mark], 120 if mark.startswith('symbol') else 480)
            base = os.path.join(d, f'eki-labs-{mark}-{way}')
            open(base + '.svg', 'w', encoding='utf-8').write(svg)
            cairosvg.svg2pdf(bytestring=svg.encode(), write_to=base + '.pdf')
            for wpx in widths:
                cairosvg.svg2png(bytestring=svg.encode(), write_to=f'{base}-{wpx}px.png', output_width=wpx)
            made.append(base)
    return made, tight


def body_for(mark, way):
    """Recoloured body + tight viewBox, for the social templates and the guide."""
    body, vb, _ = MARKS[mark]
    sun, ink = WAYS[way]
    return recolour(body, sun, ink), tight_viewbox(body, vb)


if __name__ == '__main__':
    import sys
    made, tight = build(sys.argv[1])
    print(len(made), 'masters;', tight)
