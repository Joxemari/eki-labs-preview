# eki.labs · production build for ekilabs.com (Cloudflare Pages).
# Input: the preview build (preview/site). Output: repo/site (static site), repo/functions (Pages Functions).
# What changes against the preview:
#   indexable pages (canonical, description, Open Graph), favicons and manifest, fonts served from the site,
#   no Feedbucket, no internal photo labels, legal and privacy pages (drafts pending a lawyer), a working
#   contact form (/api/contact), videos that load and play only near the viewport, 404, robots, sitemap,
#   headers and redirects. Decks stay encrypted and unindexed.
import io, json, os, re, shutil, subprocess, sys, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(HERE)
PREV = os.path.join(SP, 'preview', 'site')
KIT = os.path.join(SP, 'kit', 'out', 'eki-labs-brand-kit')
REPO = os.path.join(HERE, 'repo')
SITE = os.path.join(REPO, 'site')
ORIGIN = 'https://ekilabs.com'

PAGES = {  # path: (title, description)
    'index.html': ('eki.labs · Farming soil and sun, together.',
                   'AI and electrification need clean power now, and farmland has to keep feeding us. We build solar farms that do both: −95% land, +10% energy and +13% revenue compared with standard solar, measured over one year in our field test in Zamora.'),
    'technology/index.html': ('Technology · eki.labs', 'Solar power that is compatible with farming, at scale. Bifacial rows facing east and west, 10–18 m apart. Machinery keeps working; the crops keep growing.'),
    'model/index.html': ('Model · eki.labs', 'We generate more value, and we share it. Farmers keep their land, their crops and their CAP payments, and add a stable income from eki.labs.'),
    'video/index.html': ('Film · eki.labs', 'One acre. Two harvests. From a family of farmers to dual land use at scale: food and energy from the same field. 79 seconds.'),
    'brand/index.html': ('Brand guidelines · eki.labs', 'How eki.labs looks and speaks: logo, signature, motion, colour, type, voice and photography, with the brand kit to download.'),
    'signature/index.html': ('Email signature · eki.labs', 'One email signature for the whole eki.labs team.'),
}
NOINDEX = {'signature/index.html'}


def rel(path):
    if path == '404.html': return '/'  # served at any depth: absolute paths
    depth = path.count('/')
    return '../' * depth


def url_of(path):
    return ORIGIN + '/' + (path[:-len('index.html')] if path.endswith('index.html') else path)


# ------------------------------------------------------------------ fonts, from Google Fonts into the site
FONT_CSS = 'https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@400;500&family=Work+Sans:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'


def fetch(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=60).read()


def build_fonts(d):
    os.makedirs(d, exist_ok=True)
    css = fetch(FONT_CSS).decode()
    blocks = re.findall(r'/\* ([a-z-]+) \*/\s*(@font-face\s*\{[^}]+\})', css)
    out = ['/* Zilla Slab, Work Sans and Geist Mono · SIL Open Font License 1.1 · served from ekilabs.com */']
    n, seen = 0, {}
    for subset, block in blocks:
        if subset not in ('latin', 'latin-ext'): continue
        fam = re.search(r"font-family: '([^']+)'", block).group(1)
        wt = re.search(r'font-weight: (\d+)', block).group(1)
        m = re.search(r'url\((https://[^)]+\.woff2)\)', block)
        assert m, 'font block without woff2: ' + block[:300]
        src = m.group(1)
        if src in seen:  # variable fonts: one file serves several weights
            name = seen[src]
        else:
            name = seen[src] = f"{fam.lower().replace(' ', '-')}-{wt}-{subset}.woff2"
            open(os.path.join(d, name), 'wb').write(fetch(src)); n += 1
        out.append(block.replace(src, name))
    open(os.path.join(d, 'fonts.css'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    return n


# ------------------------------------------------------------------ icons and the link preview image
def build_icons(d):
    import cairosvg
    sys.path.insert(0, os.path.join(SP, 'kit'))
    import logos
    small, _ = logos.MARKS['symbol-small'][0], None
    full = logos.MARKS['symbol'][0]
    day = logos.recolour(small, '#FFD54A', '#0A100C')
    svg_fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><style>.r{fill:#0A100C}@media (prefers-color-scheme: dark){.r{fill:#F4F2EC}}</style>'
               + day.replace('fill="#0A100C"', 'class="r"') + '</svg>\n')
    open(os.path.join(d, 'favicon.svg'), 'w').write(svg_fav)
    ims = []
    for px in (16, 32, 48):
        png = cairosvg.svg2png(bytestring=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">' + day + '</svg>').encode(), output_width=px, output_height=px)
        ims.append(Image.open(io.BytesIO(png)).convert('RGBA'))
    ims[-1].save(os.path.join(d, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)], append_images=ims[:-1])
    night = logos.recolour(full, '#FFD54A', '#F4F2EC')
    for px, name in ((180, 'apple-touch-icon.png'), (192, 'icon-192.png'), (512, 'icon-512.png')):
        pad = round(px * 0.2)
        inner = px - 2 * pad
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 {px} {px}"><rect width="{px}" height="{px}" fill="#0A100C"/>'
               f'<g transform="translate({pad} {pad}) scale({inner / 100})">{night}</g></svg>')
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(d, name))
    json.dump({'name': 'eki.labs', 'short_name': 'eki.labs', 'start_url': '/', 'display': 'browser', 'background_color': '#0A100C', 'theme_color': '#0A100C',
               'icons': [{'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}]},
              open(os.path.join(d, 'site.webmanifest'), 'w'), indent=2)
    shutil.copy(os.path.join(KIT, '04-social', 'web', 'eki-labs-social-preview-1200x630.png'), os.path.join(d, 'social-preview.png'))


# ------------------------------------------------------------------ the runtime that replaces the preview one
RUNTIME = r'''<script>
(function () {
  // videos: posters at once, files and playback only near the viewport (phone, tablet or desktop clip)
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var picks = [].slice.call(document.querySelectorAll('video[data-src-d]'));
  var loops = [].slice.call(document.querySelectorAll('video[autoplay]'));
  function fmt() { var w = window.innerWidth; return w < 640 ? 'm' : (w < 1024 ? 't' : 'd'); }
  function setPoster(v) { var k = fmt(), p = v.getAttribute('data-poster-' + k), ar = v.getAttribute('data-ar-' + k); if (p) v.poster = p; if (ar) v.style.aspectRatio = ar; }
  function load(v) { var k = fmt(); if (v.getAttribute('data-cur') === k) return false; v.setAttribute('data-cur', k); setPoster(v); v.src = v.getAttribute('data-src-' + k); return true; }
  function play(v) { if (still || v.hasAttribute('data-noplay')) return; var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  function lazy(v) { var s = v.getAttribute('data-lazy'); if (s && !v.getAttribute('src')) { v.src = s; v.preload = 'auto'; } }
  picks.forEach(setPoster);
  loops.forEach(function (v) { v.removeAttribute('autoplay'); if (!v.hasAttribute('data-src-d')) v.setAttribute('preload', 'none'); });
  var all = loops.concat(picks.filter(function (v) { return loops.indexOf(v) < 0; }));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) { if (v.hasAttribute('data-src-d')) load(v); lazy(v); if (v.loop) play(v); }
        else if (!v.paused && v.loop) v.pause();
      });
    }, { rootMargin: '300px 0px' });
    all.forEach(function (v) { io.observe(v); });
  } else { picks.forEach(load); loops.forEach(function (v) { lazy(v); play(v); }); }
  var tm;
  window.addEventListener('resize', function () {
    clearTimeout(tm);
    tm = setTimeout(function () { picks.forEach(function (v) { var r = v.getBoundingClientRect(); if (r.bottom > -300 && r.top < innerHeight + 300) { if (load(v) && v.loop) play(v); } else setPoster(v); }); }, 200);
  });
  // the menu closes after choosing a section
  document.querySelectorAll('.nav-panel a[href^="#"]').forEach(function (a) { a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.removeAttribute('open'); }); });
})();
</script>'''

FORM_JS = r'''<script>
(function () {
  var f = document.querySelector('form[data-contact]'); if (!f) return;
  var st = f.querySelector('[data-status]'), btn = f.querySelector('button[type="submit"]');
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    if (f.reportValidity && !f.reportValidity()) return;
    var data = {}; new FormData(f).forEach(function (v, k) { data[k] = v; });
    btn.disabled = true; st.textContent = 'Sending…';
    fetch(f.getAttribute('action'), { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || String(r.status)); }); })
      .then(function () { f.reset(); st.textContent = 'Thank you. We will get back to you soon.'; })
      .catch(function () { st.innerHTML = 'It did not go through. Write to us at <a href="mailto:hola@ekilabs.com" style="color: inherit;">hola@ekilabs.com</a>.'; })
      .then(function () { btn.disabled = false; });
  });
})();
</script>'''


def head_extra(path, title, desc):
    r = rel(path)
    tags = [f'<meta name="description" content="{desc}">', f'<link rel="canonical" href="{url_of(path)}">',
            f'<meta property="og:type" content="website">', f'<meta property="og:site_name" content="eki.labs">',
            f'<meta property="og:title" content="{title}">', f'<meta property="og:description" content="{desc}">',
            f'<meta property="og:url" content="{url_of(path)}">', f'<meta property="og:image" content="{ORIGIN}/social-preview.png">',
            '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            '<meta property="og:image:alt" content="eki.labs · Farming soil and sun, together.">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="theme-color" content="#0A100C">',
            f'<link rel="icon" href="{r}favicon.ico" sizes="32x32">', f'<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">',
            f'<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">', f'<link rel="manifest" href="{r}site.webmanifest">',
            f'<link rel="preload" href="{r}fonts/zilla-slab-400-latin.woff2" as="font" type="font/woff2" crossorigin>',
            f'<link rel="preload" href="{r}fonts/work-sans-400-latin.woff2" as="font" type="font/woff2" crossorigin>',
            f'<link rel="stylesheet" href="{r}fonts/fonts.css">']
    if path == '404.html':  # no canonical address for the error page
        tags = [t for t in tags if 'canonical' not in t and 'og:url' not in t]
    return '\n'.join(tags)


def esc_attr(t): return t.replace('&', '&amp;').replace('"', '&quot;')


def transform(path, html):
    title, desc = PAGES[path]
    r = rel(path)
    n0 = len(html)
    # head: robots, title, fonts, Feedbucket, meta
    if path in NOINDEX:
        html = html.replace('<meta name="robots" content="noindex, nofollow">', '<meta name="robots" content="noindex">')
    else:
        html = html.replace('<meta name="robots" content="noindex, nofollow">\n', '')
    html = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', html, count=1)
    html = re.sub(r'<link rel="(?:stylesheet|preconnect)" href="https://fonts\.(?:googleapis|gstatic)\.com[^"]*"[^>]*>\n?', '', html)
    html = re.sub(r'<script type="text/javascript">\s*\(function\(k\) \{.*?feedbucket.*?</script>\n?', '', html, flags=re.S)
    assert 'feedbucket' not in html and 'fonts.googleapis' not in html, path
    html = html.replace('</title>', '</title>\n' + head_extra(path, esc_attr(title), esc_attr(desc)), 1)
    # internal photo labels of the preview
    html = re.sub(r'<span[^>]*>Foto (?:de referencia|provisional)</span>', '', html)
    # footer: legal and privacy pages
    html = html.replace('[Legal notice] · [Privacy]', f'<a href="{r}legal/" style="color: inherit;">Legal notice</a> · <a href="{r}privacy/" style="color: inherit;">Privacy</a>')
    # the preview runtime for videos and menu → the production one (all pages)
    html = re.sub(r'<script>\s*\(function \(\) \{\s*// one clip per format.*?</script>', '', html, flags=re.S)
    html = html.replace('</body>', RUNTIME + '\n</body>', 1)
    # loops with a plain src (brand page): the file loads only when the tile comes near the viewport
    def lazy(m):
        tag = m.group(0)
        if 'data-src-d' in tag or ' src="' not in tag: return tag
        return tag.replace(' src="', ' data-lazy="', 1).replace('preload="auto"', 'preload="none"')
    html = re.sub(r'<video[^>]*>', lazy, html)
    html = re.sub(r'(<video[^>]*?data-src-d[^>]*?)preload="auto"', r'\1preload="none"', html)
    if path == 'index.html':
        html = contact_form(html, r)
    return html


def contact_form(html, r):
    a = html.index('<form'); b = html.index('</form>', a) + len('</form>')
    f = html[a:b]
    f = f.replace('<form ', '<form data-contact="" action="/api/contact" method="post" ', 1)
    f = f.replace('name="name" ', 'name="name" required="" maxlength="200" ', 1).replace('name="email" ', 'name="email" required="" maxlength="200" ', 1)
    f = f.replace('name="message" ', 'name="message" maxlength="5000" ', 1)
    m = re.search(r'<input([^>]*?)name="privacy"([^>]*)>', f) or re.search(r'<input([^>]*?type="checkbox"[^>]*)>', f)
    assert m, 'privacy checkbox'
    f = f.replace(m.group(0), m.group(0).replace('<input', '<input required=""', 1), 1)
    f = f.replace('I accept the privacy policy', f'<span>I accept the <a href="{r}privacy/" style="color: inherit; text-decoration: underline; text-underline-offset: 3px;">privacy policy</a></span>', 1)
    # honeypot (hidden from people and assistive tech) and a live status line after the button
    trap = ('<div aria-hidden="true" style="position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden;">'
            '<label>Leave this empty <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>')
    f = f.replace('</form>', trap + '<p data-status="" role="status" aria-live="polite" style="margin: 0; min-height: 24px; font-size: 15px; line-height: 24px; color: rgb(161, 166, 159);"></p></form>')
    assert 'I accept the <a' in f and 'data-contact' in f
    html = html[:a] + f + html[b:]
    return html.replace('</body>', FORM_JS + '\n</body>', 1)


# ------------------------------------------------------------------ simple pages: legal, privacy, 404
def simple_page(path, title, desc, body, noindex=False):
    r = rel(path)
    robots = '<meta name="robots" content="noindex">\n' if noindex else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{robots}<title>{title}</title>
{head_extra(path, esc_attr(title), esc_attr(desc))}
<style>
:root{{--noche:#0A100C;--arena:#F4F2EC;--piedra:#EBE6D8;--linea:#D6D1C3;--pizarra:#555A52;--niebla:#A1A69F;--yhonda:#056C4A;--sol:#FFD54A}}
*{{box-sizing:border-box}}html,body{{margin:0;background:var(--noche);color:var(--noche);font-family:'Work Sans',Arial,sans-serif}}
a{{color:var(--yhonda)}}
.top{{display:flex;align-items:center;justify-content:space-between;gap:24px;max-width:1280px;margin:0 auto;padding:28px 40px;color:var(--arena)}}
.top a{{color:var(--arena);text-decoration:none;font-family:'Geist Mono',Menlo,monospace;font-size:14px}}
.card{{max-width:1256px;margin:0 auto;border-radius:20px;background:var(--arena);padding:88px 52px 96px}}
.inner{{max-width:760px}}
.eyebrow{{font-family:'Geist Mono',Menlo,monospace;font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--pizarra);margin:0 0 24px}}
.eyebrow span{{display:inline-block;width:6px;height:6px;margin-right:10px;vertical-align:1px;background:var(--yhonda)}}
h1{{font-family:'Zilla Slab',Georgia,serif;font-weight:400;font-size:56px;line-height:1.05;letter-spacing:-.015em;margin:0 0 28px}}
h2{{font-family:'Zilla Slab',Georgia,serif;font-weight:400;font-size:28px;line-height:1.2;margin:48px 0 12px}}
h3{{font-size:17px;font-weight:500;margin:28px 0 8px}}
p,li,dd{{font-size:17px;line-height:27px}}p{{margin:0 0 14px}}ul{{padding-left:20px;margin:0 0 14px}}
dl{{display:grid;grid-template-columns:200px minmax(0,1fr);gap:10px 24px;margin:0 0 14px;padding:16px 0;border-top:1px solid var(--linea);border-bottom:1px solid var(--linea)}}
dt{{font-family:'Geist Mono',Menlo,monospace;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--pizarra);padding-top:5px}}dd{{margin:0}}
.draft{{display:flex;gap:12px;align-items:flex-start;padding:16px 18px;border-radius:12px;background:var(--piedra);margin:0 0 40px;font-size:15px;line-height:23px}}
.draft b{{font-weight:500}}
.ph{{background:rgba(255,213,74,.35);padding:0 4px;border-radius:3px}}
.muted{{color:var(--pizarra);font-size:15px;line-height:23px}}
.lang{{margin-top:72px;padding-top:40px;border-top:1px solid var(--linea)}}
.foot{{max-width:1280px;margin:0 auto;padding:40px;display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;color:var(--niebla);font-family:'Geist Mono',Menlo,monospace;font-size:12px}}
.foot a{{color:var(--niebla)}}
.fund{{max-width:1280px;margin:0 auto;padding:40px 40px 0;display:grid;grid-template-columns:200px minmax(0,1fr);gap:8px 24px;color:var(--niebla)}}
.fund span{{font-family:'Geist Mono',Menlo,monospace;font-size:11px;line-height:22px;font-weight:500;letter-spacing:.08em;text-transform:uppercase}}
.fund p{{margin:0;max-width:640px;font-size:14px;line-height:22px}}
.fund p span{{font-family:inherit;font-size:inherit;letter-spacing:0;text-transform:none;font-weight:400;color:var(--arena)}}
.logos{{max-width:1256px;margin:0 auto 12px;padding:28px 40px;border-radius:20px;background:var(--arena);display:flex;flex-wrap:wrap;align-items:center;gap:28px 48px}}
.logos img{{display:block;height:44px;width:auto}}
@media (max-width:639px){{.top{{padding:20px}}.card{{margin:0 8px;padding:56px 20px 64px;border-radius:16px}}h1{{font-size:40px}}dl{{grid-template-columns:1fr;gap:2px}}dt{{padding-top:12px}}.foot{{padding:28px 20px}}.fund{{grid-template-columns:1fr;padding:32px 20px 0}}.logos{{margin:0 8px 8px;padding:24px 20px;gap:20px 28px;border-radius:16px}}.logos img{{height:34px}}}}
</style>
</head>
<body>
<header class="top"><a href="{r}" aria-label="eki.labs, home">{LOGO_NIGHT}</a><a href="{r}#contact">Contact →</a></header>
<main class="card"><div class="inner">
{body}
</div></main>
<footer><div class="fund"><span>Funding</span><p>{FUND_TEXT}</p></div>
<div class="foot"><span>© Eki Agrivoltaic, S.L.U.</span><span><a href="{r}legal/">Legal notice</a> · <a href="{r}privacy/">Privacy</a> · <a href="{r}brand/">Brand</a></span></div></footer>
<div class="logos">{FUND_LOGOS.replace('src="assets/', 'src="' + r + 'assets/')}</div>
</body>
</html>
'''


def logo_night_svg():
    sys.path.insert(0, os.path.join(SP, 'kit'))
    import logos
    body, (x, y, w, h) = logos.body_for('logo', 'night')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="120" height="{120 * h / w:.1f}" role="img" aria-label="eki.labs">{body}</svg>'


LOGO_NIGHT = ''
PH = lambda t: f'<span class="ph">[{t}]</span>'


def legal_body():
    return f'''<p class="eyebrow"><span></span>Legal</p>
<h1>Legal notice</h1>
<div class="draft"><div><b>Draft pending legal review.</b> The bracketed details must be completed and the text checked by a lawyer before this page is final.</div></div>
<h2>Who runs this website</h2>
<p>In compliance with Article 10 of Spanish Law 34/2002 on information society services and electronic commerce (LSSI-CE), these are the details of the owner of ekilabs.com:</p>
<dl>
<dt>Owner</dt><dd>{PH('Legal name of the company')}</dd>
<dt>Tax ID</dt><dd>{PH('NIF / CIF')}</dd>
<dt>Registered office</dt><dd>{PH('Full address')}</dd>
<dt>Registry</dt><dd>{PH('Registro Mercantil, volume, folio, sheet and entry')}</dd>
<dt>Email</dt><dd><a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a></dd>
</dl>
<h2>Use of the website</h2>
<p>Access to this website is free and does not require registration. By using it you agree to use it lawfully, in good faith and without harming the website, its owner or third parties.</p>
<h2>Intellectual and industrial property</h2>
<p>The content of this website, including text, images, video, graphics, the eki.labs name, logos and design, belongs to its owner or is used with permission. Copying, distributing or transforming it without permission is not allowed, except for the materials published for download on the brand page, which may be used as described there to refer to eki.labs.</p>
<h2>Liability</h2>
<p>We work to keep the information on this website accurate and up to date. Figures are indicative unless stated otherwise and do not constitute an offer. The owner is not liable for the content of third-party websites linked from this site.</p>
<h2>Applicable law</h2>
<p>This notice is governed by Spanish law. {PH('Courts with jurisdiction, if a specific venue is wanted')}</p>
<p class="muted">Last updated: {PH('date')}</p>

<div class="lang" lang="es">
<p class="eyebrow"><span></span>Versión en español</p>
<h2 style="margin-top:0">Aviso legal</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico (LSSI-CE), el titular de ekilabs.com es {PH('razón social')}, con NIF {PH('NIF')}, domicilio en {PH('dirección completa')} e inscrita en {PH('Registro Mercantil, tomo, folio, hoja e inscripción')}. Contacto: <a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a>.</p>
<p>El acceso a la web es gratuito y no requiere registro. Los contenidos (textos, imágenes, vídeo, gráficos, el nombre eki.labs, logotipos y diseño) pertenecen a su titular o se usan con autorización; no se permite su reproducción, distribución o transformación sin permiso, salvo los materiales que se publican para su descarga en la página de marca, en las condiciones allí indicadas. Las cifras son orientativas salvo que se indique lo contrario y no constituyen una oferta. Este aviso se rige por la legislación española.</p>
</div>'''


def privacy_body():
    return f'''<p class="eyebrow"><span></span>Legal</p>
<h1>Privacy policy</h1>
<div class="draft"><div><b>Draft pending legal review.</b> The bracketed details must be completed and the text checked by a lawyer before this page is final.</div></div>
<h2>Who is responsible for your data</h2>
<dl>
<dt>Controller</dt><dd>{PH('Legal name of the company')}</dd>
<dt>Tax ID</dt><dd>{PH('NIF / CIF')}</dd>
<dt>Address</dt><dd>{PH('Full address')}</dd>
<dt>Contact</dt><dd><a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a></dd>
</dl>
<h2>What we collect and why</h2>
<p>When you write to us through the contact form or by email, we receive your name, your email address, the profile you choose (investor, farmer or other) and your message. We use them only to answer you and to follow up on your request.</p>
<ul>
<li><b>Legal basis:</b> your consent when you send the form, and the steps you ask us to take before a possible agreement.</li>
<li><b>How long we keep them:</b> while we handle your request and, afterwards, for as long as the law requires. {PH('Specific retention period')}</li>
<li><b>We do not</b> sell your data, use it for advertising or make automated decisions with it.</li>
</ul>
<h2>Who processes it for us</h2>
<p>Providers that help us run the website and email, under contract and only on our instructions:</p>
<ul>
<li>Cloudflare, Inc.: website hosting and security.</li>
<li>Resend: delivery of the messages sent through the contact form.</li>
<li>Google: our email (Google Workspace).</li>
</ul>
<p>Some of these providers may process data outside the European Economic Area. In that case the transfer relies on the safeguards the GDPR allows, such as the EU–US Data Privacy Framework or the European Commission's standard contractual clauses. {PH('Confirm providers and safeguards')}</p>
<h2>Cookies</h2>
<p>This website does not use analytics, advertising or tracking cookies. Our hosting provider may set strictly necessary cookies for security. Pages restricted to the team use a sign-in cookie.</p>
<h2>Your rights</h2>
<p>You can ask to access, correct or delete your data, to restrict or object to its processing, and to receive it in a portable format, and you can withdraw your consent at any time. Write to <a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a>. If you think we have not handled your data properly, you can complain to the Spanish Data Protection Agency (<a href="https://www.aepd.es">aepd.es</a>).</p>
<p class="muted">Last updated: {PH('date')}</p>

<div class="lang" lang="es">
<p class="eyebrow"><span></span>Versión en español</p>
<h2 style="margin-top:0">Política de privacidad</h2>
<p>Responsable: {PH('razón social')}, NIF {PH('NIF')}, {PH('dirección')}. Contacto: <a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a>.</p>
<p>Si nos escribes por el formulario o por email, tratamos tu nombre, tu email, el perfil que elijas y tu mensaje solo para responderte y atender tu solicitud, con base en tu consentimiento y en las medidas precontractuales que nos pidas. Los conservamos mientras atendemos tu solicitud y, después, durante los plazos legales. {PH('plazo concreto')} No los vendemos ni los usamos para publicidad.</p>
<p>Nos ayudan a prestar el servicio Cloudflare (alojamiento y seguridad), Resend (envío de los mensajes del formulario) y Google (correo), que pueden tratar datos fuera del Espacio Económico Europeo con las garantías que permite el RGPD. Esta web no usa cookies de analítica, publicidad ni seguimiento.</p>
<p>Puedes ejercer tus derechos de acceso, rectificación, supresión, limitación, oposición y portabilidad, y retirar tu consentimiento, escribiendo a <a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a>. También puedes reclamar ante la Agencia Española de Protección de Datos (<a href="https://www.aepd.es">aepd.es</a>).</p>
</div>'''


def notfound_body():
    return '''<p class="eyebrow"><span></span>404</p>
<h1>This page is not in the field.</h1>
<p>The link may be old or mistyped. Start again from the home page, or write to us.</p>
<p style="margin-top:28px;display:flex;flex-wrap:wrap;align-items:center;gap:16px 28px"><a href="/" style="display:inline-flex;align-items:center;gap:10px;height:48px;padding:0 20px;border-radius:4px;background:#58E9AE;color:#0A100C;font-family:'Geist Mono',Menlo,monospace;font-size:14px;font-weight:500;text-decoration:none">Go to the home page →</a>
<a href="mailto:hola@ekilabs.com">hola@ekilabs.com</a></p>'''


# ------------------------------------------------------------------ files for Cloudflare Pages
ROBOTS = f'''User-agent: *
Allow: /
Disallow: /decks/
Disallow: /signature/
Disallow: /lab/

Sitemap: {ORIGIN}/sitemap.xml
'''

HEADERS = '''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=86400, stale-while-revalidate=604800

/fonts/*
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *

/decks/*
  X-Robots-Tag: noindex, nofollow
  Cache-Control: private, no-store

/signature/*
  X-Robots-Tag: noindex

/brand/kit/*
  Content-Disposition: attachment
'''

REDIRECTS = '''/deck          /decks/       301
/deck/         /decks/       301
/slides        /decks/       301
/careers       /#careers     301
/careers/      /#careers     301
/film          /video/       301
/film/         /video/       301
'''

FUNCTION = r'''// POST /api/contact · the contact form on the home page.
// Sends the message by email through Resend (https://resend.com). Configure in Cloudflare Pages
// › Settings › Variables and secrets:
//   RESEND_API_KEY  (secret)  API key from Resend
//   CONTACT_FROM              sender on a domain verified in Resend, e.g. "eki.labs web <web@notify.ekilabs.com>"
//   CONTACT_TO                where messages go (comma-separated), default hola@ekilabs.com
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export async function onRequestPost({ request, env }) {
  let d;
  try {
    const type = request.headers.get('content-type') || '';
    d = type.includes('application/json') ? await request.json() : Object.fromEntries(await request.formData());
  } catch {
    return json({ ok: false, error: 'bad_request' }, 400);
  }
  if (d.website) return json({ ok: true }); // honeypot: bots fill it, people never see it
  const clean = (v, n) => String(v ?? '').replace(/[\r\n]+/g, ' ').trim().slice(0, n);
  const name = clean(d.name, 200);
  const email = clean(d.email, 200);
  const profile = clean(d.profile, 60);
  const message = String(d.message ?? '').trim().slice(0, 5000);
  const consent = d.privacy === 'on' || d.privacy === true || d.privacy === 'true';
  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !consent) return json({ ok: false, error: 'invalid' }, 422);
  if (!env.RESEND_API_KEY || !env.CONTACT_FROM) return json({ ok: false, error: 'not_configured' }, 503);
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: env.CONTACT_FROM,
      to: (env.CONTACT_TO || 'hola@ekilabs.com').split(',').map((s) => s.trim()).filter(Boolean),
      reply_to: email,
      subject: `ekilabs.com · ${profile || 'Contact'} · ${name}`,
      text: `Name: ${name}\nEmail: ${email}\nI am: ${profile || '—'}\n\n${message || '(no message)'}\n\n— Sent from the contact form at ekilabs.com`,
    }),
  });
  if (!r.ok) return json({ ok: false, error: 'send_failed' }, 502);
  return json({ ok: true });
}

export const onRequest = () => new Response('Method not allowed', { status: 405, headers: { Allow: 'POST' } });
'''


def unused_assets(site):
    """Assets of the preview that no page, script or stylesheet points to (the decks keep theirs)."""
    text = ''
    for dp, _, fs in os.walk(site):
        if os.path.relpath(dp, site).startswith('decks'): continue
        for f in fs:
            if f.endswith(('.html', '.css', '.js', '.json', '.webmanifest')):
                text += open(os.path.join(dp, f), encoding='utf-8', errors='ignore').read()
    out = []
    for f in os.listdir(os.path.join(site, 'assets')):
        if f not in text: out.append(f)
    return out


def main():
    global LOGO_NIGHT
    shutil.rmtree(REPO, ignore_errors=True)
    shutil.copytree(PREV, SITE)
    for junk in ('.nojekyll',):
        p = os.path.join(SITE, junk)
        if os.path.exists(p): os.remove(p)
    print('fonts', build_fonts(os.path.join(SITE, 'fonts')))
    build_icons(SITE)
    LOGO_NIGHT = logo_night_svg()
    for path in PAGES:
        p = os.path.join(SITE, path)
        src = open(p, encoding='utf-8').read()  # read before opening for writing (that truncates the file)
        out = transform(path, src)
        open(p, 'w', encoding='utf-8').write(out)
    # signature images from the folder the page is served from (ekilabs.com or the GitHub preview); elsewhere from ekilabs.com
    sig = os.path.join(SITE, 'signature', 'index.html')
    s = open(sig, encoding='utf-8').read()
    assert s.count("var BASE = 'https://joxemari.github.io/eki-labs-preview/signature/';") == 1
    open(sig, 'w', encoding='utf-8').write(s.replace("var BASE = 'https://joxemari.github.io/eki-labs-preview/signature/';", "var BASE = /^(ekilabs\\.com|joxemari\\.github\\.io)$/.test(location.hostname) ? new URL('./', location.href).href : 'https://ekilabs.com/signature/';"))
    # decks: same fonts as the site, still private
    dk = os.path.join(SITE, 'decks', 'index.html')
    s = open(dk, encoding='utf-8').read()
    s = re.sub(r'<link rel="(?:stylesheet|preconnect)" href="https://fonts\.(?:googleapis|gstatic)\.com[^"]*"[^>]*>\n?', '', s)
    s = s.replace('</title>', '</title>\n<link rel="icon" href="../favicon.ico" sizes="32x32">\n<link rel="stylesheet" href="../fonts/fonts.css">', 1)
    s = s.replace('Slides · eki.labs · Preview', 'Slides · eki.labs')
    open(dk, 'w', encoding='utf-8').write(s)
    # the funding block of the home page (text and logos), for the simple pages
    global FUND_TEXT, FUND_LOGOS
    home = open(os.path.join(SITE, 'index.html'), encoding='utf-8').read()
    m = re.search(r'id="funding"[^>]*>.*?<p[^>]*>(.*?)</p>', home, re.S); assert m, 'funding text'
    FUND_TEXT = re.sub(r'\s*style="[^"]*"', '', m.group(1))
    m = re.search(r'id="funding-logos"[^>]*>(.*?)</div>', home, re.S); assert m, 'funding logos'
    FUND_LOGOS = re.sub(r'\s*style="[^"]*"', '', m.group(1))
    assert FUND_LOGOS.count('<img') == 4
    # new pages
    for path, title, desc, body, ni in (('legal/index.html', 'Legal notice · eki.labs', 'Legal notice of ekilabs.com.', legal_body(), False),
                                        ('privacy/index.html', 'Privacy policy · eki.labs', 'How eki.labs handles personal data.', privacy_body(), False),
                                        ('404.html', 'Page not found · eki.labs', 'This page is not in the field.', notfound_body(), True)):
        os.makedirs(os.path.dirname(os.path.join(SITE, path)) or SITE, exist_ok=True)
        open(os.path.join(SITE, path), 'w', encoding='utf-8').write(simple_page(path, title, desc, body, ni))
    PAGES_SM = [p for p in PAGES if p not in NOINDEX] + ['legal/index.html', 'privacy/index.html']
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'  <url><loc>{url_of(p)}</loc></url>' for p in PAGES_SM] + ['</urlset>']
    open(os.path.join(SITE, 'sitemap.xml'), 'w').write('\n'.join(sm) + '\n')
    open(os.path.join(SITE, 'robots.txt'), 'w').write(ROBOTS)
    open(os.path.join(SITE, '_headers'), 'w').write(HEADERS)
    open(os.path.join(SITE, '_redirects'), 'w').write(REDIRECTS)
    os.makedirs(os.path.join(REPO, 'functions', 'api'), exist_ok=True)
    open(os.path.join(REPO, 'functions', 'api', 'contact.js'), 'w').write(FUNCTION)
    for f in unused_assets(SITE):
        os.remove(os.path.join(SITE, 'assets', f)); print('removed unused asset', f)
    n = sum(len(fs) for _, _, fs in os.walk(SITE))
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(SITE) for f in fs)
    big = [(os.path.getsize(os.path.join(dp, f)), os.path.join(dp, f)) for dp, _, fs in os.walk(SITE) for f in fs if os.path.getsize(os.path.join(dp, f)) > 25 * 1024 * 1024]
    print('site files', n, 'MB', round(size / 1e6, 1), 'over 25 MiB:', big)


if __name__ == '__main__':
    main()
