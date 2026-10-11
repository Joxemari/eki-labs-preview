# eki.labs brand kit · social formats (LinkedIn, Instagram, YouTube, web).
# Each piece is an editable SVG (live text in Zilla Slab, Work Sans and Geist Mono, logos as outlines)
# plus a PNG at the size each network asks for. Copy comes from the content hub; nothing invented.
import os
from PIL import ImageFont
import logos

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, 'fonts_dl')
NOCHE, ARENA, SOL, NIEBLA, ACERO, PIZARRA, GRAFITO = '#0A100C', '#F4F2EC', '#FFD54A', '#A1A69F', '#2B332D', '#555A52', '#141B16'
PIEDRA, LINEA, YHONDA = '#EBE6D8', '#D6D1C3', '#056C4A'
ZS, WS, GM = "'Zilla Slab', Georgia, serif", "'Work Sans', Arial, sans-serif", "'Geist Mono', Menlo, monospace"

_f = {}


def font(kind, size, wght=400):
    key = (kind, size, wght)
    if key not in _f:
        p = {'zs': 'zillaslab_ZillaSlab-Regular.ttf', 'ws': 'worksans_WorkSans[wght].ttf', 'gm': 'geistmono_GeistMono[wght].ttf'}[kind]
        f = ImageFont.truetype(os.path.join(FD, p), size)
        if kind != 'zs':
            try: f.set_variation_by_axes([wght])
            except Exception: pass
        _f[key] = f
    return _f[key]


def width(text, kind, size, wght=400, track=0.0):
    return font(kind, size, wght).getlength(text) + track * size * max(0, len(text) - 1)


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, t, kind, size, fill, wght=400, track=0.0, anchor='start', upper=False):
    fam = {'zs': ZS, 'ws': WS, 'gm': GM}[kind]
    ls = f' letter-spacing="{track * size:.2f}"' if track else ''
    t = t.upper() if upper else t
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{wght}" fill="{fill}"'
            f' text-anchor="{anchor}"{ls}>{esc(t)}</text>')


def eyebrow(x, y, label, size, colour, marker):
    """The system's eyebrow: a small square, then the label in mono capitals."""
    s = round(size * 0.5)
    return (f'<rect x="{x}" y="{y - size * 0.62:.1f}" width="{s}" height="{s}" fill="{marker}"/>'
            + text(x + s + round(size * 0.8), y, label, 'gm', size, colour, 500, 0.08, upper=True))


def mark(name, way, x, y, w):
    body, (vx, vy, vw, vh) = logos.body_for(name, way)
    k = w / vw
    return f'<g transform="translate({x - vx * k:.2f} {y - vy * k:.2f}) scale({k:.5f})">{body}</g>', vh * k


def horizon(y, x0, x1, colour, sw=2):
    return f'<rect x="{x0}" y="{y - sw / 2}" width="{x1 - x0}" height="{sw}" fill="{colour}"/>'


def sun(cx, y, r, colour):
    return f'<path d="M{cx - r} {y}A{r} {r} 0 0 1 {cx + r} {y}Z" fill="{colour}"/>'


def rows(x0, x1, y0, y1, colour, step=40, sw=2):
    """Panels in elevation below the horizon: the 5 % rule (2 px every 40 px)."""
    out = []
    x = x0 + step / 2
    while x < x1:
        out.append(f'<rect x="{x - sw / 2:.1f}" y="{y0}" width="{sw}" height="{y1 - y0}" fill="{colour}"/>')
        x += step
    return ''.join(out)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<title>{esc(title)}</title>{body}</svg>\n')


def landscape(w, h, y_h, sun_x, sun_r, ground=NOCHE, line=PIZARRA, row=ACERO, step=40, sw=2, sun_c=SOL):
    return (f'<rect width="{w}" height="{h}" fill="{ground}"/>' + rows(0, w, y_h + sw, h, row, step, sw)
            + horizon(y_h, 0, w, line, sw) + sun(sun_x, y_h - sw / 2, sun_r, sun_c))


# ------------------------------------------------------------------ pieces
def avatar(day=False):
    w = h = 1080
    ground, way = (ARENA, 'day') if day else (NOCHE, 'night')
    m, mh = mark('symbol', way, (w - 580) / 2, (h - 580) / 2, 580)
    return svg(w, h, f'<rect width="{w}" height="{h}" fill="{ground}"/>' + m, 'eki.labs · avatar')


def linkedin_cover():
    w, h = 1512, 256
    line = 'Farming soil and sun, together.'
    fs = 50; tw = width(line, 'zs', fs)
    gap, r = 64, 48
    x0 = round(w / 2 - (tw + gap + 2 * r) / 2)
    b = landscape(w, h, 198, x0 + tw + gap + r, r)
    b += text(x0, 150, line, 'zs', fs, ARENA)
    return svg(w, h, b, 'eki.labs · LinkedIn page cover')


def linkedin_personal():
    w, h = 1584, 396
    b = landscape(w, h, 316, 1250, 50)
    m, mh = mark('signature', 'night', 900, 64, 540)
    return svg(w, h, b + m, 'eki.labs · LinkedIn profile banner')


def youtube_banner():
    w, h = 2560, 1440
    b = landscape(w, h, 930, 1880, 64)
    m, mh = mark('signature', 'night', 700, 0, 900)
    m, mh = mark('signature', 'night', 700, round(735 - mh / 2), 900)
    # the area every device shows (1546 × 423, centred) is left as a note for whoever edits the file
    note = '<!-- Safe area on every device: x 507–2053, y 508–932. Keep logo and text inside it. -->'
    return svg(w, h, note + b + m, 'eki.labs · YouTube channel banner')


def youtube_thumb():
    w, h = 1280, 720
    b = landscape(w, h, 600, 1064, 64)
    m, mh = mark('logo', 'night', 80, 72, 210)
    b += m + eyebrow(80, 214, 'Film · 79 s', 22, NIEBLA, SOL)
    b += text(76, 336, 'One acre.', 'zs', 112, ARENA) + text(76, 456, 'Two harvests.', 'zs', 112, ARENA)
    return svg(w, h, b, 'eki.labs · YouTube thumbnail')


def statement(h=1350):
    w = 1080
    y_h = h - 210
    b = landscape(w, h, y_h, 880, 62)
    m, mh = mark('logo', 'night', 80, 80, 230)
    lines = ["Now, you don’t", 'have to choose.']
    fs = 108 if h > 1080 else 94
    top = (h - 210) / 2 - (len(lines) * fs * 1.04) / 2 + fs * 0.62
    b += m + eyebrow(80, round(top - fs * 1.05), '02 · The breakthrough', 24, NIEBLA, SOL)
    for i, t in enumerate(lines):
        b += text(74, round(top + i * fs * 1.04), t, 'zs', fs, ARENA)
    b += text(80, y_h - 44, 'ekilabs.com', 'gm', 24, NIEBLA, 400, 0.02)
    return svg(w, h, b, 'eki.labs · post · statement')


def figures(h=1350):
    w = 1080
    b = f'<rect width="{w}" height="{h}" fill="{ARENA}"/>'
    m, mh = mark('logo', 'day', 80, 80, 230)
    b += m
    big = 300 if h > 1080 else 250
    y0 = 300 if h > 1080 else 250
    b += eyebrow(80, y0, 'Field tests · Zamora', 24, PIZARRA, YHONDA)
    b += text(64, y0 + big * 0.95, '−95%', 'gm', big, NOCHE, 400, -0.05)
    b += text(80, y0 + big * 0.95 + 64, 'Land', 'ws', 36, PIZARRA)
    yb = y0 + big * 0.95 + 150
    b += horizon(yb, 80, w - 80, LINEA, 2)
    mid = 120 if h > 1080 else 104
    for i, (fig, lab) in enumerate((('+10%', 'Energy'), ('+13%', 'Revenue'))):
        x = 80 + i * 470
        b += text(x - 6, yb + 40 + mid * 0.9, fig, 'gm', mid, NOCHE, 400, -0.05)
        b += text(x, yb + 40 + mid * 0.9 + 52, lab, 'ws', 32, PIZARRA)
    b += text(80, h - 120, 'Versus conventional solar.', 'ws', 26, PIZARRA)
    b += text(80, h - 80, 'Measured over one year in our field test in Zamora.', 'ws', 26, PIZARRA)
    return svg(w, h, b, 'eki.labs · post · figures')


def carousel_cover():
    w, h = 1080, 1350
    b = landscape(w, h, 1140, 880, 62)
    m, mh = mark('logo', 'night', 80, 80, 230)
    b += m + eyebrow(80, 520, '03 · How it works', 24, NIEBLA, SOL)
    b += text(74, 640, 'One acre,', 'zs', 100, ARENA) + text(74, 744, 'four layers.', 'zs', 100, ARENA)
    b += text(80, 1096, 'Swipe →', 'gm', 24, NIEBLA, 400, 0.02)
    return svg(w, h, b, 'eki.labs · carousel · cover')


def carousel_page():
    w, h = 1080, 1350
    b = f'<rect width="{w}" height="{h}" fill="{ARENA}"/>'
    m, mh = mark('symbol', 'day', 80, 80, 64)
    b += m + text(w - 80, 124, '1 / 4', 'gm', 24, PIZARRA, 400, 0.02, 'end')
    b += text(64, 560, '01', 'gm', 220, NOCHE, 400, -0.05)
    b += text(74, 720, 'Sunlight', 'zs', 96, NOCHE)
    b += text(80, 800, 'The same light reaches the panels', 'ws', 36, PIZARRA)
    b += text(80, 852, 'and the crops.', 'ws', 36, PIZARRA)
    b += horizon(h - 160, 80, w - 80, LINEA, 2) + text(80, h - 100, 'ekilabs.com', 'gm', 24, PIZARRA, 400, 0.02)
    return svg(w, h, b, 'eki.labs · carousel · page')


def story():
    w, h = 1080, 1920
    b = landscape(w, h, 1440, 860, 72)
    m, mh = mark('logo', 'night', 80, 250, 260)
    b += m + eyebrow(80, 820, 'Film · 79 s', 28, NIEBLA, SOL)
    b += text(72, 990, 'One acre.', 'zs', 140, ARENA) + text(72, 1135, 'Two harvests.', 'zs', 140, ARENA)
    b += text(80, 1380, 'ekilabs.com', 'gm', 28, NIEBLA, 400, 0.02)
    return svg(w, h, b, 'eki.labs · Instagram story')


def og_image():
    w, h = 1200, 630
    b = landscape(w, h, 520, 1000, 54)
    m, mh = mark('signature', 'night', 0, 0, 620)
    m, mh = mark('signature', 'night', 90, round(270 - mh / 2), 620)
    return svg(w, h, b + m, 'eki.labs · social preview')


PIECES = [
    # folder, file stem, builder, png sizes (None = native)
    ('avatars', 'eki-labs-avatar-night', avatar, (400, 800, 1080)),
    ('avatars', 'eki-labs-avatar-day', lambda: avatar(True), (400, 800, 1080)),
    ('linkedin', 'eki-labs-linkedin-page-cover-1512x256', linkedin_cover, None),
    ('linkedin', 'eki-labs-linkedin-profile-banner-1584x396', linkedin_personal, None),
    ('youtube', 'eki-labs-youtube-banner-2560x1440', youtube_banner, None),
    ('youtube', 'eki-labs-youtube-thumbnail-1280x720', youtube_thumb, None),
    ('instagram', 'eki-labs-instagram-story-1080x1920', story, None),
    ('posts', 'eki-labs-post-statement-1080x1350', statement, None),
    ('posts', 'eki-labs-post-statement-1080x1080', lambda: statement(1080), None),
    ('posts', 'eki-labs-post-figures-1080x1350', figures, None),
    ('posts', 'eki-labs-post-figures-1080x1080', lambda: figures(1080), None),
    ('posts', 'eki-labs-carousel-cover-1080x1350', carousel_cover, None),
    ('posts', 'eki-labs-carousel-page-1080x1350', carousel_page, None),
    ('web', 'eki-labs-social-preview-1200x630', og_image, None),
]


def build(out_dir):
    files = []
    for folder, stem, fn, sizes in PIECES:
        d = os.path.join(out_dir, folder); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, stem + '.svg')
        open(p, 'w', encoding='utf-8').write(fn())
        files.append((p, sizes))
    return files


if __name__ == '__main__':
    import sys
    for p, s in build(sys.argv[1]): print(p, s)
