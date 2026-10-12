# eki.labs brand kit · logo files.
# The symbol is one circle of 100: the sun above the horizon, in the sun gradient (orange crown, sol on the
# horizon, a nod to the first eki logo), and three rows below in the ink of the name.
# The wordmark is «eki.» in Geist 600 plus the second name in Geist 400 (wordmark.py), in curves.
# Proportion: the symbol's circle is 923 units against 1000 font units, the name sits centred on it
# (ascender to baseline) and starts a quarter of the diameter after the circle.
# The signatures keep the tagline of ./masters, re-fitted to the width of the new logo.
# Every file is cropped tight to the artwork; the clear space rule (¼ of the symbol's diameter) is in the README.
import io, os, re
import cairosvg
from PIL import Image
import wordmark

HERE = os.path.dirname(os.path.abspath(__file__))
MASTERS = os.path.join(HERE, 'masters')
NOCHE, ARENA, WHITE = '#0A100C', '#F4F2EC', '#FFFFFF'

# The sun gradient, on the circle's 0–100 box: orange (logo only) in the crown, sol on the horizon. Only the sun takes it.
SUN_STOPS = ((0, '#FF8F00'), (0.1, '#FF8F00'), (0.42, '#FFD54A'), (1, '#FFD54A'))  # orange crown, sol on the horizon
SUN_ID, FULL_ID = 'eki-sun', 'eki-sun-full'
SUN, FULL = f'url(#{SUN_ID})', f'url(#{FULL_ID})'
# Option A, the full gradient: the whole symbol, sun and rows, from the orange crown through sol to yerba at the foot.
FULL_STOPS = ((0, '#FF8F00'), (0.1, '#FF8F00'), (0.42, '#FFD54A'), (0.66, '#FFD54A'), (1, '#58E9AE'))


def _grad(gid, stops):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="100">'
            + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient>')


SUN_DEFS = '<defs>' + _grad(SUN_ID, SUN_STOPS) + '</defs>'
FULL_DEFS = '<defs>' + _grad(FULL_ID, FULL_STOPS) + '</defs>'

WAYS = {  # colourway: (sun, rows, letters)
    'day-full': (FULL, FULL, NOCHE), 'night-full': (FULL, FULL, ARENA),    # the default pair: the whole symbol in the full gradient
    'day': (SUN, NOCHE, NOCHE), 'night': (SUN, ARENA, ARENA),              # alternative: sun in gradient, rows in ink (small sizes, low contrast)
    'black': (NOCHE, NOCHE, NOCHE), 'white': (WHITE, WHITE, WHITE)}         # one ink

SYM_SCALE, SYM_Y = 9.23, -816.5  # symbol 923 units tall, bottom 106.5 under the baseline
# The name starts a quarter of the symbol's diameter after the circle (the same unit as the clear space
# and the tagline gap), measured to the ink of the «e» (its left side bearing is 39 units).
WORD_X = round(100 * SYM_SCALE * 1.25 - 39)
MASTER_WORD_X = 1278  # where the name sat in the masters the taglines were drawn for


def band(y1, y2):
    import math
    def xs(y):
        d = math.sqrt(max(0, 50 * 50 - (y - 50) ** 2)); return 50 - d, 50 + d
    a1, b1 = xs(y1); a2, b2 = xs(y2)
    return f'M{a1:.2f} {y1:.2f}L{b1:.2f} {y1:.2f}A50 50 0 0 1 {b2:.2f} {y2:.2f}L{a2:.2f} {y2:.2f}A50 50 0 0 1 {a1:.2f} {y1:.2f}Z'


HALF_SUN = 'M0 50A50 50 0 0 1 100 50Z'
ROWS = [(56.14, 66.67), (72.81, 83.33), (89.47, 100)]
ROWS_SMALL = [(59.21, 75.0), (84.21, 100)]  # below 32 px the symbol keeps two rows so it stays sharp


def symbol(rows=ROWS):
    """The symbol in a 0–100 box: the sun takes @@SUN and the rows @@ROWS."""
    return (f'<path d="{HALF_SUN}" fill="@@SUN"/>'
            + ''.join(f'<path d="{band(a, b)}" fill="@@ROWS"/>' for a, b in rows))


def word(second=''):
    ds, xmax = wordmark.name(second)
    return ''.join(f'<path d="{d}" fill="@@INK"/>' for d in ds), xmax


def logo(second='labs'):
    w, xmax = word(second)
    body = (f'<g transform="translate(0 {SYM_Y}) scale({SYM_SCALE})">{symbol()}</g>'
            f'<g transform="translate({WORD_X} 0)">{w}</g>')
    return body, (0, SYM_Y, WORD_X + xmax, 100 * SYM_SCALE)


def tight_viewbox(body, vb, probe=4000):
    """Crop a viewBox to the drawn pixels (rendered on transparent ground)."""
    x, y, w, h = vb
    W = probe; H = round(probe * h / w)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{W}" height="{H}">{body}</svg>'
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')
    bx = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    sx, sy = w / W, h / H
    return (round(x + bx[0] * sx, 2), round(y + bx[1] * sy, 2), round((bx[2] - bx[0]) * sx, 2), round((bx[3] - bx[1]) * sy, 2))


def _tagline(master):
    """The tagline path of a signature master, and the logo width it was fitted to."""
    s = open(os.path.join(MASTERS, master), encoding='utf-8').read()
    tag = re.findall(r'<path d="[^"]+" fill="[^"]+"/>', s)[-1]
    return re.search(r'd="([^"]+)"', tag).group(1)


def _bbox(d):
    """Bounding box of a path, measured on a render (same method as tight_viewbox)."""
    nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', d)]
    xs, ys = nums[0::2], nums[1::2]
    vb = (min(xs) - 50, min(ys) - 50, max(xs) - min(xs) + 100, max(ys) - min(ys) + 100)
    return tight_viewbox(f'<path d="{d}" fill="#000"/>', vb)


OLD_WORD_W = wordmark.paths([('eki.labs', 600)])[1]  # the name the master taglines were drawn for
LABS_WORD_W = wordmark.name('labs')[1]                  # «eki.labs» with the second name in regular

# The tagline is always the same and always the same size against the symbol: as wide as the
# eki.labs logo. Under a shorter or longer name it keeps that size, aligned left (horizontal) or
# centred (stacked), so it reads the same in every lockup.
TAGLINE = 'Farming soil & sun, together'
TAG_FONT = os.path.join(HERE, 'fonts_dl', 'zillaslab_ZillaSlab-Regular.ttf')


def tagline(width, top):
    """The tagline in curves (Zilla Slab 400, with its kerning), as wide as `width`, its ink starting at x = 0
    and its tallest letter at y = `top`. Returns (path data, (x, y, w, h) of the ink)."""
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen
    font = TTFont(TAG_FONT); gs = font.getGlyphSet(); order = font.getGlyphOrder()
    face = hb.Face(hb.Blob.from_file_path(TAG_FONT)); hf = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(TAGLINE); buf.guess_segment_properties(); hb.shape(hf, buf)
    placed, x = [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        placed.append((order[info.codepoint], x + pos.x_offset)); x += pos.x_advance
    bp = BoundsPen(gs)
    for name, gx in placed:
        gs[name].draw(TransformPen(bp, (1, 0, 0, 1, gx, 0)))
    x0, y0, x1, y1 = bp.bounds  # font units, y up
    k = width / (x1 - x0)
    pen = SVGPathPen(gs, ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
    for name, gx in placed:
        gs[name].draw(TransformPen(pen, (k, 0, 0, -k, (gx - x0) * k, top + y1 * k)))
    return pen.getCommands(), (0.0, top, width, (y1 - y0) * k)


_OLD_TAG_TOP_H = _bbox(_tagline('lockup-firma-dia.svg'))[1]           # a quarter of the symbol under the logo
_OLD_TAG_TOP_V = _bbox(_tagline('lockup-firma-vertical-dia.svg'))[1]
TAG_H, TAG_H_BOX = tagline(WORD_X + LABS_WORD_W, _OLD_TAG_TOP_H)       # as wide as the eki.labs logo
TAG_V, TAG_V_BOX = tagline(LABS_WORD_W, _OLD_TAG_TOP_V)                # stacked: as wide as the name
TAG_H_K = TAG_V_K = 1.0

V_SYM_SCALE, V_WORD_Y = 13.49, 2449.5  # stacked: symbol 1349 tall on top, name below


def _tag(d, box, k, dx=0.0):
    tx, ty, tw, th = box
    return (f'<g transform="translate({tx + dx:.2f} {ty:.2f}) scale({k:.5f}) translate({-tx:.2f} {-ty:.2f})">'
            f'<path d="{d}" fill="@@INK"/></g>')


def signature(second='labs'):
    body, (x, y, w, h) = logo(second)
    tx, ty, tw, th = TAG_H_BOX
    return body + _tag(TAG_H, TAG_H_BOX, TAG_H_K), (x, y, max(w, tw * TAG_H_K), (ty + th * TAG_H_K) - y)


def signature_vertical(second='labs'):
    w, xmax = word(second)
    tx, ty, tw, th = TAG_V_BOX
    tagw = tw * TAG_V_K
    block = max(xmax, tagw, 100 * V_SYM_SCALE)
    sx = block / 2 - 50 * V_SYM_SCALE           # symbol centred
    wx = (block - xmax) / 2                       # name centred
    dx = (block - tagw) / 2 - tx                  # tagline centred
    body = (f'<g transform="translate({sx:.2f} 0) scale({V_SYM_SCALE})">{symbol()}</g>'
            f'<g transform="translate({wx:.2f} {V_WORD_Y})">{w}</g>'
            + _tag(TAG_V, TAG_V_BOX, TAG_V_K, dx))
    return body, (0, 0, block, ty + th * TAG_V_K)


def recolour(svg_body, sun, ink, rows=None):
    out = svg_body.replace('@@SUN', sun).replace('@@ROWS', rows or ink).replace('@@INK', ink)
    return (SUN_DEFS if SUN in out else '') + (FULL_DEFS if FULL in out else '') + out


def _pad(vb, p=60):
    x, y, w, h = vb
    return (x - p, y - p, w + 2 * p, h + 2 * p)


# name: (file prefix, body with @@SUN/@@INK, viewBox before cropping, png widths)
# The kit carries the two names in use, eki.labs and eki.; any other ending comes from the logo builder.
MARKS = {}
for key, prefix, second in (('logo', 'eki-labs-logo', 'labs'), ('eki', 'eki-logo', '')):
    b, vb = logo(second)
    MARKS[key] = (prefix, b, _pad(vb), (1200, 4000))
MARKS['symbol'] = ('eki-labs-symbol', symbol(), (0, 0, 100, 100), (512, 2048))
MARKS['symbol-small'] = ('eki-labs-symbol-small', symbol(ROWS_SMALL), (0, 0, 100, 100), (16, 24))  # only below 32 px
for key, prefix, second in (('signature', 'eki-labs-signature', 'labs'),):
    b, vb = signature(second)
    MARKS[key] = (prefix, b, _pad(vb, 200), (1600, 4000))
for key, prefix, second in (('signature-vertical', 'eki-labs-signature-vertical', 'labs'),):
    b, vb = signature_vertical(second)
    MARKS[key] = (prefix, b, _pad(vb, 200), (1200, 3000))


def builder_data():
    """What the logo builder needs to draw any ending in curves, in the browser."""
    from fontTools.pens.boundsPen import BoundsPen
    f = wordmark._font(wordmark.NAME_WEIGHT)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f['hmtx']
    glyphs = {}
    for ch in 'abcdefghijklmnopqrstuvwxyz0123456789-':
        ds, x1 = wordmark.paths([(ch, wordmark.NAME_WEIGHT)])
        glyphs[ch] = {'d': ds[0], 'adv': hmtx[cmap[ord(ch)]][0], 'x1': round(x1, 1)}
    base, base_x1 = wordmark.paths([(wordmark.BASE, wordmark.BASE_WEIGHT)])
    f6 = wordmark._font(wordmark.BASE_WEIGHT)
    base_adv = sum(f6['hmtx'][f6.getBestCmap()[ord(c)]][0] for c in wordmark.BASE)
    return {
        'symbol': symbol().replace('@@SUN', '{sym}').replace('@@ROWS', '{rows}'),
        'symbolSmall': symbol(ROWS_SMALL).replace('@@SUN', '{sym}').replace('@@ROWS', '{rows}'),
        'base': base, 'baseAdv': base_adv, 'baseX1': round(base_x1, 1), 'glyphs': glyphs,
        'symScale': SYM_SCALE, 'symY': SYM_Y, 'wordX': WORD_X, 'vSymScale': V_SYM_SCALE, 'vWordY': V_WORD_Y,
        'tagH': {'d': TAG_H, 'box': TAG_H_BOX, 'k': TAG_H_K}, 'tagV': {'d': TAG_V, 'box': TAG_V_BOX, 'k': TAG_V_K},
        'sunDefs': SUN_DEFS, 'fullDefs': FULL_DEFS,
    }


def svg_file(body, vb, width_px=None, title='eki.labs'):
    x, y, w, h = vb
    wpx = width_px or 480
    hpx = round(wpx * h / w, 2)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{wpx}" height="{hpx}">'
            f'<title>{title}</title>{body}</svg>\n')


TITLES = {'eki': 'eki.'}
_tight = {}


def tight(mark):
    if mark not in _tight:
        _, body, vb, _ = MARKS[mark]
        _tight[mark] = vb if mark.startswith('symbol') else tight_viewbox(re.sub('@@(SUN|ROWS|INK)', '#000', body), vb)
    return _tight[mark]


def build(out_dir):
    made = []
    for mark, (prefix, body, _, widths) in MARKS.items():
        d = os.path.join(out_dir, mark); os.makedirs(d, exist_ok=True)
        for way, (sun, rows, ink) in WAYS.items():
            b = recolour(body, sun, ink, rows)
            svg = svg_file(b, tight(mark), 120 if mark.startswith('symbol') else 480, TITLES.get(mark, 'eki.labs'))
            base = os.path.join(d, f'{prefix}-{way}')
            open(base + '.svg', 'w', encoding='utf-8').write(svg)
            cairosvg.svg2pdf(bytestring=svg.encode(), write_to=base + '.pdf')
            for wpx in widths:
                cairosvg.svg2png(bytestring=svg.encode(), write_to=f'{base}-{wpx}px.png', output_width=wpx)
            made.append(base)
    return made, {m: tight(m) for m in MARKS}


def body_for(mark, way):
    """Recoloured body + tight viewBox, for the social templates and the guide."""
    sun, rows, ink = WAYS[way]
    return recolour(MARKS[mark][1], sun, ink, rows), tight(mark)


if __name__ == '__main__':
    import sys
    made, t = build(sys.argv[1])
    print(len(made), 'files;', t)
