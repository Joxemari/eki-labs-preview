# eki.labs · the logo files the web uses outside the kit: header and footer logos in site/assets,
# favicons and app icons. Same artwork as logos.py; each asset keeps its viewBox so the pages
# that size it with a fixed box (width × height in the style) keep their layout.
# Run from the repo root after build_kit.py:  python3 source/brand-kit/site_logos.py
import io, os, re, sys
import cairosvg
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import logos

SITE = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'site')
NOCHE, ARENA = '#0A100C', '#F4F2EC'

# asset: (mark, ink, viewBox kept from the page layout, width, height)
ASSETS = {
    'cd5507e4423d.svg': ('logo', ARENA, (0, -816.5, 5042, 923), 349.61, 64),          # header on dark
    '935050cd151d.svg': ('logo', NOCHE, (0, -816.5, 5042, 923), 349.61, 64),          # header on light
    '759d73f045c4.svg': ('signature', ARENA, (0, -816.5, 5042, 1495.7), 504.2, 149.6),  # footer signature on dark
    '1d46fd23e616.svg': ('signature', NOCHE, (0, -816.5, 5042, 1495.7), 504.2, 149.6),
    'dc5cee91e523.svg': ('signature-vertical', ARENA, (0, 0, 3764, 3039.2), 376.4, 303.9),
    '71544ddc841a.svg': ('signature-vertical', NOCHE, (0, 0, 3764, 3039.2), 376.4, 303.9),
}


WHITE = '#FFFFFF'


def asset(mark, ink, vb, w, h):
    sym = ink if ink == WHITE else logos.FULL  # one-ink white over photos, the full gradient everywhere else
    body = logos.recolour(logos.MARKS[mark][1], sym, ink, sym)
    tx, ty, tw, th = logos.tight(mark)
    x, y, vw, vh = vb
    dx = (x + (vw - tw) / 2 - tx) if mark == 'signature-vertical' else 0  # vertical: centred in its box
    if dx:
        body = f'<g transform="translate({dx:.2f} 0)">{body}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {vw} {vh}" width="{w}" height="{h}">'
            f'<title>eki.labs</title>{body}</svg>\n')


def favicon_svg():
    """The small symbol (two rows) in the alternative for small sizes: the sun in its gradient, the rows in noche,
    arena when the browser is dark."""
    body = logos.recolour(logos.MARKS['symbol-small'][1], logos.SUN, '@@R').replace('fill="@@R"', 'class="r"')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><style>.r{fill:#0A100C}'
            '@media (prefers-color-scheme: dark){.r{fill:#F4F2EC}}</style>' + body + '</svg>\n')


def app_icon_svg(size):
    """The app icon: the symbol in the full gradient on noche, 60 % of the side."""
    body = logos.recolour(logos.MARKS['symbol'][1], logos.FULL, ARENA, logos.FULL)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{size}" height="{size}">'
            f'<rect width="100" height="100" fill="{NOCHE}"/><g transform="translate(20 20) scale(0.6)">{body}</g></svg>')


def png(svg, size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size))).convert('RGBA')


# Pages: the logo drawn inline (headers, the home intro, the guide, the logo animations). The whole symbol takes the
# full gradient and the second name of the wordmark goes in Geist 400. The two-row symbol for small sizes keeps the
# alternative (sun in gradient, rows in ink).
PAGES = ['index.html', '404.html', 'legal/index.html', 'privacy/index.html', 'decks/index.html', 'brand/index.html']
SUN_PATH = re.compile(r'(<path(?: class="[^"]*")? d="M0 50A50 50 0 [01] 1 100 50Z" fill=")#ffd54a(")', re.I)
ROW_PATH = re.compile(r'<path\b([^>]*?)\sd="(M0\.38 56\.14|M5\.51? 72\.81|M19\.31 89\.47)([^"]*)"([^>]*?)(/?)>')
LOW_HALF = re.compile(r'(<path\b[^>]*?d="M0 50A50 50 0 0 0 100 50Z"[^>]*?fill=")#ffd54a(")', re.I)
SMALL_ROWS = ('M0.86 59.21', 'M13.54 84.21')


def _full_rows(m):
    pre = re.sub(r'\sfill="[^"]*"', '', m.group(1))
    post = re.sub(r'\sfill="[^"]*"', '', m.group(4))
    return f'<path{pre} d="{m.group(2)}{m.group(3)}"{post} fill="url(#eki-sun-full)"{m.group(5)}>'


def to_full(t):
    """One inline logo svg to the full gradient. The two-row symbol (small sizes) stays in the alternative."""
    if any(r in t for r in SMALL_ROWS):
        return t
    t = SUN_PATH.sub(r'\1url(#eki-sun)\2', t)
    t = t.replace('url(#eki-sun)', 'url(#eki-sun-full)')
    t = LOW_HALF.sub(r'\1url(#eki-sun-full)\2', t)
    t = ROW_PATH.sub(_full_rows, t)
    t = re.sub(r'<defs><linearGradient id="eki-sun(?:-full)?".*?</linearGradient></defs>', '', t, flags=re.S)
    i = t.index('>') + 1
    return t[:i] + logos.FULL_DEFS + t[i:]


def _wordmark_swap():
    import wordmark
    old, _ = wordmark.paths([('eki.labs', 600)])
    new, _ = wordmark.name('labs')
    assert old[:4] == new[:4]  # «eki.» keeps its curves
    return list(zip(old[4:], new[4:]))


CANVAS = os.path.join(os.path.dirname(HERE), 'canvas')


def update_pages():
    swap = _wordmark_swap()
    files = [os.path.join(SITE, r) for r in PAGES] + sorted(
        os.path.join(CANVAS, f) for f in os.listdir(CANVAS) if f.endswith('.dc.html'))
    for path in files:
        rel = os.path.relpath(path, os.path.dirname(SITE))
        s = open(path, encoding='utf-8').read()
        n0 = s
        for a, b in swap:
            s = s.replace(a, b)

        def svg_fix(m):
            t = m.group(0)
            if 'data-lb' in t:
                return t
            t = re.sub(r'translate\((?:1278|1278\.00|1115)( 0(?:\.00)?)\)', f'translate({logos.WORD_X}\\1)', t)
            if re.search(r'url\(#eki-sun(?:-full)?\)', t) or SUN_PATH.search(t):  # a logo; a sun in another colour is a «no» example
                t = to_full(t)
            return t
        s = re.sub(r'<svg\b[^>]*>(?:(?!</svg>).)*?</svg>', svg_fix, s, flags=re.S)
        if s != n0:
            open(path, 'w', encoding='utf-8').write(s)
            print('updated', rel)


def main():
    for name, args in ASSETS.items():
        open(os.path.join(SITE, 'assets', name), 'w', encoding='utf-8').write(asset(*args))
    fav = favicon_svg()
    open(os.path.join(SITE, 'favicon.svg'), 'w', encoding='utf-8').write(fav)
    full = favicon_svg().replace(logos.recolour(logos.MARKS['symbol-small'][1], logos.SUN, '@@R').replace('fill="@@R"', 'class="r"'),
                                 logos.recolour(logos.MARKS['symbol'][1], logos.SUN, '@@R').replace('fill="@@R"', 'class="r"'))
    ico = [png(fav, 16), png(full, 32), png(full, 48)]  # two rows only below 32 px
    ico[2].save(os.path.join(SITE, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:2])
    for name, s in (('icon-192.png', 192), ('icon-512.png', 512), ('apple-touch-icon.png', 180)):
        png(app_icon_svg(s), s).convert('RGB').save(os.path.join(SITE, name), optimize=True)
    # the link preview image of every page is the kit's web preview
    import shutil
    shutil.copy(os.path.join(SITE, 'brand', 'kit', 'files', '04-social', 'web', 'eki-labs-social-preview-1200x630.png'),
                os.path.join(SITE, 'social-preview.png'))
    # email signature images (white ground, sized as the generator asks for them)
    for name, mark, (W, H) in (('eki-labs-logo.png', 'logo', (360, 66)), ('eki-labs-firma.png', 'signature', (504, 150))):
        tx, ty, tw, th = logos.tight(mark)
        svg = logos.svg_file(logos.recolour(logos.MARKS[mark][1], logos.FULL, NOCHE, logos.FULL), (tx, ty, tw, th))
        k = min(W / tw, H / th)
        im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=round(tw * k)))).convert('RGBA')
        out = Image.new('RGBA', (W, H), '#FFFFFF'); out.alpha_composite(im, (0, (H - im.height) // 2))
        out.convert('RGB').save(os.path.join(SITE, 'signature', name), optimize=True)
    update_pages()
    print('site logos, favicons and icons written')


if __name__ == '__main__':
    main()
