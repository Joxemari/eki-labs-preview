# Responsive layer for the GitHub preview (phase 1: Home).
# The design canvas stays a 1280 px desktop design; only the preview adapts to tablet and phone.
# Method: tag the snapshot's elements with r-* classes from their inline styles, then override those
# inline styles inside media queries (!important). At 1280 px and above nothing changes.
import re
from bs4 import BeautifulSoup

PHONE = 639     # phones: 360–440 px
TABLET = 1023   # iPad mini / iPad / iPad Air 11 / iPad Pro 11 portrait: 744–834 px
WIDE = 1279     # iPad 13 portrait, iPads in landscape, small laptops: 1024–1279 px


def _style(el):
    d = {}
    for part in (el.get('style') or '').split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            d[k.strip()] = v.strip()
    return d


def _box(v):
    """CSS shorthand (padding/margin) -> [top, right, bottom, left] as strings."""
    p = v.split()
    if len(p) == 1: p = p * 4
    elif len(p) == 2: p = [p[0], p[1], p[0], p[1]]
    elif len(p) == 3: p = [p[0], p[1], p[2], p[1]]
    return p[:4]


def _px(v):
    m = re.match(r'^(?:calc\()?(-?[\d.]+)px\)?$', v or '')
    return float(m.group(1)) if m else None


def _add(el, *cls):
    c = el.get('class') or []
    for k in cls:
        if k not in c: c.append(k)
    el['class'] = c


GRIDS = {
    'repeat(12, minmax(0px, 1fr))': 'r-g12', 'repeat(3, minmax(0px, 1fr))': 'r-g3', 'repeat(5, minmax(0px, 1fr))': 'r-g5',
    'repeat(2, minmax(0px, 1fr))': 'r-g2', '1fr 1fr': 'r-g2', 'minmax(0px, 2fr) minmax(0px, 1fr)': 'r-g21', '1fr 2fr': 'r-gfoot',
    '120px minmax(0px, 1fr)': 'r-gmem', '1.15fr 1fr': 'r-ghero', '1.3fr 1fr': 'r-ghero',
    'repeat(4, minmax(0px, 1fr))': 'r-g4', '150px 1fr': 'r-gkv', '170px minmax(0px, 1fr)': 'r-gkv2', '170px 1fr': 'r-gchart',
}
FS = {114.68: 'h1', 94: 'h1', 88: '88', 70: '70', 64: '64', 48: '48', 40: '40', 34: '34', 30: '30', 28: '28', 26: '26', 24: '24', 22: '22', 20: '20', 19: '19', 11: '11'}


def tag(html):
    soup = BeautifulSoup(html, 'lxml')
    for el in soup.find_all(True):
        if el.name in ('svg', 'path', 'g', 'rect', 'circle', 'line', 'text', 'mask', 'clippath'):
            continue
        s = _style(el)
        if not s: continue
        if s.get('width') == '1280px': _add(el, 'r-root')
        g = s.get('grid-template-columns')
        if g in GRIDS: _add(el, GRIDS[g])
        gc = s.get('grid-column')
        if gc: _add(el, 'r-gc')
        fs = _px(s.get('font-size'))
        if fs is not None:
            k = min(FS, key=lambda x: abs(x - fs))
            if abs(k - fs) < 0.6: _add(el, 'r-fs' + FS[k])
        for prop in ('padding', 'margin'):
            if prop in s:
                t, r, b, l = _box(s[prop])
                if r == '52px' or l == '52px': _add(el, 'r-' + prop[0] + 'x52')
                if r == '64px' or l == '64px': _add(el, 'r-' + prop[0] + 'x64')
                if r == '12px' and l == '12px': _add(el, 'r-' + prop[0] + 'x12')
                if t in ('144px', '148px'): _add(el, 'r-' + prop[0] + 't144')
                if t == '96px' and prop == 'padding': _add(el, 'r-pt96')
                if b == '96px' and prop == 'padding': _add(el, 'r-pb96')
                if t in ('72px', '56px') and prop == 'padding': _add(el, 'r-pt72')
        h = _px(s.get('height'))
        if h is not None and h >= 200: _add(el, 'r-h%d' % h)
        mh = _px(s.get('min-height'))
        if mh is not None and mh >= 150: _add(el, 'r-mh%d' % mh)
        if s.get('max-width', '').endswith('ch') or s.get('max-width', '').endswith('px'): _add(el, 'r-mw')
    return soup


# ---------------------------------------------------------------- Home
NAV_EXTRA = ('<span class="nav-h r-mob">On this page</span>'
             '<a class="r-mob" href="#how">How it works</a><a class="r-mob" href="#impact">Impact</a>'
             '<a class="r-mob" href="#team">Team</a><a class="r-mob" href="#story">Origins</a>'
             '<a class="r-mob" href="#contact">Contact</a><span class="nav-h r-mob">eki.labs sites</span>')


def home(html, clips):
    soup = tag(html)
    hdr = soup.select_one('[data-hdr] header')
    if hdr:
        _add(hdr, 'r-hdr')
        nav = hdr.find('nav', recursive=False)
        if nav: _add(nav, 'r-nav')
        right = hdr.find('div', recursive=False)
        if right:
            _add(right, 'r-hdr-r')
            links = right.find_all('a', recursive=False)
            if links: _add(links[0], 'r-hide-t')           # «Contact»: in the menu on tablet and phone
            if len(links) > 1: _add(links[1], 'r-cta')      # «Explore our science»
        panel = hdr.select_one('.nav-panel')
        if panel:
            first = panel.find('span', class_='nav-h')
            if first:
                first.insert_before(BeautifulSoup(NAV_EXTRA, 'html.parser'))
                first.decompose()
    # hero
    hero = soup.select_one('#mission > div')
    if hero: _add(hero, 'r-hero')
    ref = soup.find('span', string=re.compile('Foto de referencia'))
    if ref: _add(ref, 'r-ref')
    for sp in soup.find_all('span', string=re.compile('Foto provisional')): _add(sp, 'r-ref2')
    # partners carousel
    part = soup.select_one('#partners')
    if part: _add(part, 'r-partners')
    # How it works: one clip per format, chosen by the runtime (phone / tablet / desktop)
    how = soup.select_one('#how video')
    if how:
        d, t, m = clips
        for k in ('src', 'poster'): del how[k]
        how['data-src-d'], how['data-poster-d'] = d
        how['data-src-t'], how['data-poster-t'] = t
        how['data-src-m'], how['data-poster-m'] = m
        how['style'] = 'display:block; width:100%; height:auto; aspect-ratio:1280/900; object-fit:cover;'
        _add(how, 'r-how')
    for el in soup.select('.r-gmem'): _add(el.parent, 'r-gteam')
    for el in soup.select('#problem .r-g2 > div > div'): _add(el, 'r-card-in')
    for el in soup.select('#team .r-g21 > div'): _add(el, 'r-teamcard')
    for el in soup.select('#story .r-g5 .r-fs48'): _add(el, 'r-stat')
    for el in soup.select('#story .r-g12 > div:last-child > div'): _add(el, 'r-backed')
    # team members, supporters, careers, origins stats, brand band, contact decoration, funding logos
    sup = soup.find('span', string=re.compile('Experience and support'))
    if sup: _add(sup.parent, 'r-support')
    marca = soup.select_one('#marca')
    if marca:
        _add(marca, 'r-marca')
        svg = marca.find('svg')
        if svg: _add(svg, 'r-marca-logo')
        row = marca.find_all('div', recursive=False)
        if row: _add(row[-1], 'r-marca-row')
    contact = soup.select_one('#contact')
    if contact:
        deco = contact.find_all('div', recursive=False)
        if deco: _add(deco[-1], 'r-deco')
    fl = soup.select_one('#funding-logos')
    if fl: _add(fl, 'r-flogos')
    legal = soup.select_one('#funding')
    if legal and legal.find_next_sibling('div'): _add(legal.find_next_sibling('div'), 'r-legal')
    body = soup.body.decode_contents() if soup.body else str(soup)
    return body


CSS_HOME = r'''
/* ---------- responsive layer (preview only) ---------- */
.r-mob{display:none !important}
.r-root{box-sizing:border-box}
.r-how{border-radius:0}
@media (max-width: %(WIDE)dpx){
  .wrap{width:100% !important}
  .r-root{width:100% !important}
  .r-px52{padding-left:40px !important; padding-right:40px !important}
  .r-mx52{margin-left:40px !important; margin-right:40px !important}
  .r-px64{padding-left:52px !important; padding-right:52px !important}
  .r-fsh1{font-size:96px !important}
  .r-fs70{font-size:60px !important}
  .r-g12{column-gap:20px !important}
  .r-nav{gap:18px !important}
  .r-hdr{gap:28px !important}
  .r-deco{margin-left:-40px !important; margin-right:-40px !important}
  form input, form select, form textarea{box-sizing:border-box !important; max-width:100%}
  .r-stat{font-size:36px !important}
  .r-backed{flex-wrap:wrap; gap:20px 32px !important}
  .r-gmem{grid-template-columns:96px minmax(0,1fr) !important; gap:16px !important}
  .r-gmem > img{width:96px !important; height:96px !important}
}
@media (max-width: 1100px){
  .r-gteam{grid-template-columns:repeat(2, minmax(0,1fr)) !important}
}
@media (max-width: %(TABLET)dpx){
  html,body{overflow-x:hidden}
  .r-nav,.r-hide-t{display:none !important}
  .nav-panel .r-mob{display:flex !important}
  .nav-panel .nav-h.r-mob{display:block !important}
  .r-hdr{top:16px !important; left:16px !important; right:16px !important; gap:16px !important; justify-content:space-between}
  .r-hdr-r{margin-left:auto}
  .nav-panel{max-height:calc(100vh - 120px); overflow-y:auto}
  .r-g12{display:flex !important; flex-direction:column; align-items:flex-start !important; gap:20px}
  .r-g12 > .r-gc{width:100%; max-width:640px}
  #funding .r-gc{max-width:540px}
  section.r-pt144{padding-top:112px !important}
  .r-mt144{margin-top:112px !important}
  .r-pt96{padding-top:72px !important}
  .r-pb96{padding-bottom:72px !important}
  .r-pt72{padding-top:56px !important}
  .r-px52{padding-left:28px !important; padding-right:28px !important}
  .r-mx52{margin-left:28px !important; margin-right:28px !important}
  .r-px64{padding-left:40px !important; padding-right:40px !important}
  .r-fsh1{font-size:76px !important}
  .r-fs70{font-size:52px !important}
  .r-fs48{font-size:40px !important}
  .r-fs40{font-size:32px !important; line-height:1.2 !important}
  .r-fs34{font-size:28px !important}
  .r-fs30{font-size:25px !important}
  #mission > div.r-hero{height:clamp(640px, 82vh, 920px) !important}
  .r-ghero{display:flex !important; flex-direction:column; align-items:stretch !important; gap:24px !important; padding:120px 28px 40px !important}
  .r-ghero h1{max-width:12ch !important}
  .r-ref{top:88px !important}
  .r-partners{padding:48px 40px 0 !important}
  .r-partners .r-g12{gap:16px}
  .r-partners .lg-marquee{width:100%}
  .r-h300{height:240px !important}
  .r-h480{height:380px !important}
  .r-h580{height:440px !important}
  .r-h500{height:460px !important}
  .r-h560{height:480px !important}
  .r-g21{grid-template-columns:1fr 1fr !important}
  .r-gteam{grid-template-columns:repeat(2, minmax(0,1fr)) !important}
  .r-gmem{grid-template-columns:96px minmax(0,1fr) !important}
  .r-gmem > img{width:96px !important; height:96px !important}
  .r-partners .lg-marquee{max-width:none !important}
  .r-card-in{padding:28px 28px 36px !important; gap:28px !important}
  .r-teamcard{padding:36px 32px !important}
  .r-g5{grid-template-columns:repeat(3, minmax(0,1fr)) !important}
  .r-stat{font-size:40px !important}
  .r-support{flex-wrap:wrap}
  .r-marca-logo{width:min(520px, 70vw) !important; height:auto !important}
  .r-marca-row{flex-wrap:wrap; justify-content:center; gap:10px 28px !important; padding:0 20px; text-align:center}
  .r-how{aspect-ratio:800/620 !important}
  .r-gfoot{grid-template-columns:1fr !important; gap:36px !important}
  .r-deco{margin-left:-28px !important; margin-right:-28px !important}
  .r-flogos{flex-wrap:wrap; gap:24px 40px !important}
}
@media (max-width: %(PHONE)dpx){
  .r-hdr{top:8px !important; left:8px !important; right:8px !important; height:56px !important; padding:0 8px 0 16px !important; gap:10px !important}
  .r-cta{display:none !important}
  .r-fs11{font-size:12px !important}
  .r-hdr > a{padding:11px 0}
  footer .r-g3 a{padding:6px 0}
  footer .r-g3 > div{gap:2px !important}
  .nav-panel{position:fixed !important; top:72px !important; left:8px !important; right:8px !important; width:auto !important; background:#0a100c !important}
  .nav-panel a,.nav-panel .nav-soon{min-height:44px; box-sizing:border-box; align-items:center !important}
  .r-mx12{margin-left:8px !important; margin-right:8px !important}
  .r-px12{padding-left:8px !important; padding-right:8px !important}
  section.r-pt144{padding-top:88px !important}
  .r-mt144{margin-top:88px !important}
  .r-pt96{padding-top:56px !important}
  .r-pb96{padding-bottom:56px !important}
  .r-pt72{padding-top:44px !important}
  .r-px52{padding-left:12px !important; padding-right:12px !important}
  .r-mx52{margin-left:12px !important; margin-right:12px !important}
  .r-px64{padding-left:20px !important; padding-right:20px !important}
  #story.r-px52,#contact.r-px52{padding-left:20px !important; padding-right:20px !important}
  footer .r-px52{padding-left:20px !important; padding-right:20px !important}
  footer .r-mx52{margin-left:20px !important; margin-right:20px !important}
  #careers.r-px52{padding-left:20px !important; padding-right:20px !important}
  .r-fsh1{font-size:clamp(46px, 13vw, 58px) !important; line-height:1 !important}
  .r-fs70{font-size:40px !important; line-height:1.05 !important}
  .r-fs48{font-size:32px !important; line-height:1.12 !important}
  .r-fs40{font-size:27px !important; line-height:1.22 !important}
  .r-fs34{font-size:25px !important; line-height:1.2 !important}
  .r-fs30{font-size:21px !important; line-height:1.4 !important}
  .r-fs28{font-size:22px !important}
  .r-fs24{font-size:21px !important}
  .r-fs22{font-size:20px !important}
  .r-fs20,.r-fs19{font-size:17px !important; line-height:1.5 !important}
  #mission > div.r-hero{height:min(100vh, 760px) !important; height:min(100svh, 760px) !important}
  .r-ghero{padding:0 20px 28px !important; gap:18px !important; margin-top:auto}
  .r-ref{top:76px !important; right:12px !important}
  .r-ref2{top:12px !important; left:12px !important}
  .r-partners{padding:40px 20px 0 !important}
  .lg-cell{padding:0 22px !important}
  .r-g2{grid-template-columns:1fr !important; gap:8px !important}
  .r-g3{grid-template-columns:1fr !important; gap:8px !important}
  .r-g21{grid-template-columns:1fr !important; gap:8px !important}
  .r-g5{grid-template-columns:repeat(2, minmax(0,1fr)) !important; gap:8px !important}
  .r-g5 > :last-child{grid-column:1 / -1}
  .r-stat{font-size:32px !important}
  .r-gmem{grid-template-columns:88px minmax(0,1fr) !important; gap:16px !important; padding:12px !important}
  .r-gmem > img{width:88px !important; height:88px !important}
  .r-h300{height:210px !important}
  .r-h480{height:280px !important}
  .r-h580{height:420px !important}
  .r-h500{height:auto !important; min-height:340px}
  figure.r-h500{height:440px !important}
  .r-h560{height:400px !important}
  .r-mh196{min-height:150px !important}
  .r-gteam{grid-template-columns:1fr !important}
  .r-card-in{padding:24px 20px 28px !important; gap:24px !important}
  .r-teamcard{padding:28px 24px !important; gap:24px}
  .r-how{aspect-ratio:390/760 !important}
  .r-support{flex-direction:column; align-items:flex-start !important; gap:16px !important}
  .r-marca-logo{width:78vw !important}
  .r-marca-row{flex-direction:column; align-items:center; gap:6px !important; bottom:22px !important; font-size:12px !important; letter-spacing:0.04em !important}
  .nav-panel small,.nav-panel .nav-h{font-size:12px !important}
  .r-gfoot{gap:28px !important}
  .r-gfoot .r-g3{grid-template-columns:repeat(2, minmax(0,1fr)) !important; gap:24px 16px !important}
  .r-deco{margin:40px -20px -56px !important; height:180px !important}
  .r-legal{flex-direction:column; gap:8px}
  .r-flogos{padding:24px 20px 32px !important; gap:20px 28px !important}
  .r-flogos img{height:34px !important; width:auto !important}
}
'''.replace('%(WIDE)dpx', f'{WIDE}px').replace('%(TABLET)dpx', f'{TABLET}px').replace('%(PHONE)dpx', f'{PHONE}px')

RUNTIME_HOME = r'''
<script>
(function () {
  // one clip per format: phone < 640 px, tablet < 1024 px, desktop
  var vs = [].slice.call(document.querySelectorAll('video[data-src-d]'));
  function pick() {
    var w = window.innerWidth;
    vs.forEach(function (v) {
      var k = w < 640 ? 'm' : (w < 1024 ? 't' : 'd');
      if (v.getAttribute('data-cur') === k) return;
      v.setAttribute('data-cur', k);
      v.poster = v.getAttribute('data-poster-' + k); v.src = v.getAttribute('data-src-' + k);
      var ar = v.getAttribute('data-ar-' + k); if (ar) v.style.aspectRatio = ar;
      if (v.hasAttribute('data-noplay')) return;
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    });
  }
  pick(); var tm; window.addEventListener('resize', function () { clearTimeout(tm); tm = setTimeout(pick, 200); });
  // the menu closes after choosing a section
  document.querySelectorAll('.nav-panel a[href^="#"]').forEach(function (a) { a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.removeAttribute('open'); }); });
})();
</script>'''


# ---------------------------------------------------------------- microsites (phase 2: Technology, Model, Film)
def _header(soup):
    """Header for tablet and phone: the section links and Contact move into the menu."""
    hdr = soup.select_one('[data-hdr] header')
    if not hdr: return
    _add(hdr, 'r-hdr')
    nav = hdr.find('nav', recursive=False)
    right = hdr.find('div', recursive=False)
    items = []
    if nav:
        _add(nav, 'r-nav')
        items = [(a.get('href'), a.get_text(strip=True)) for a in nav.find_all('a')]
    if right:
        _add(right, 'r-hdr-r')
        links = right.find_all('a', recursive=False)
        if links:
            _add(links[0], 'r-hide-t')
            items.append((links[0].get('href'), 'Contact'))
        if len(links) > 1: _add(links[1], 'r-cta')
    panel = hdr.select_one('.nav-panel')
    first = panel.find('span', class_='nav-h') if panel else None
    if first and items:
        extra = '<span class="nav-h r-mob">On this page</span>' + ''.join(f'<a class="r-mob" href="{h}">{t}</a>' for h, t in items) + \
                '<span class="nav-h r-mob">eki.labs sites</span>'
        first.insert_before(BeautifulSoup(extra, 'html.parser'))
        first.decompose()


def _footer(soup):
    fl = soup.select_one('#funding-logos')
    if fl: _add(fl, 'r-flogos')
    legal = soup.select_one('#funding')
    if legal and legal.find_next_sibling('div'): _add(legal.find_next_sibling('div'), 'r-legal')


def _clip(v, variants):
    """variants: {'d'|'t'|'m': (src, poster, aspect)} — the runtime picks one by width."""
    for k in ('src', 'poster'):
        if v.has_attr(k): del v[k]
    for k, (src, poster, ar) in variants.items():
        v['data-src-' + k], v['data-poster-' + k], v['data-ar-' + k] = src, poster, ar
    v['style'] = 'display:block; width:100%; height:auto; aspect-ratio:' + variants['d'][2] + '; object-fit:cover;'
    _add(v, 'r-vid')
    wrap = v.find_parent('div', style=re.compile(r'border-radius: 20px'))
    if wrap: _add(wrap, 'r-vwrap')


def micro(html, page, clips=None):
    soup = tag(html)
    _header(soup)
    _footer(soup)
    hero = soup.select_one('#top > div')
    if hero: _add(hero, 'r-hero')
    ref = soup.find('span', string=re.compile('Foto de referencia'))
    if ref: _add(ref, 'r-ref')
    for sp in soup.find_all('span', string=re.compile('Foto provisional')): _add(sp, 'r-ref2')
    # closing call to action: the button drops under the text on phones
    for a in [x for x in soup.find_all('a') if 'Get in touch' in x.get_text()]:
        par = a.parent
        if par and 'display: flex' in (par.get('style') or '') and page != 'video': _add(par, 'r-ctarow')
    if page == 'tech':
        for v in soup.find_all('video'):
            src = v.get('src', '')
            for key in clips or {}:
                if key in src: _clip(v, clips[key])
        for el in soup.select('#compare .r-g2 > div'): _add(el, 'r-cardp')
        fig = soup.select_one('#science figure')
        if fig:
            _add(fig, 'r-fig')
            head = fig.find('div', recursive=False)
            if head: _add(head, 'r-fighead')
            if fig.find('video'): _add(fig.find('video'), 'r-vid')
        for el in soup.select('#field .r-g4 > div > span:first-child'): _add(el, 'r-stat88')
    if page == 'model':
        for el in soup.find_all('div', style=re.compile(r'padding: 36px 36px 32px')): _add(el, 'r-chartbox')
        box = soup.select_one('.r-chartbox')
        if box:
            head = box.find('div', recursive=False)
            if head:
                _add(head, 'r-wrap')
                for sp in head.find_all('span', recursive=False): _add(sp, 'r-wrap')
        for el in soup.select('#next .r-g4 > div'):
            if 'position: absolute' in (el.get('style') or ''): _add(el, 'r-tline')
    if page == 'video':
        v = soup.select_one('#film video')
        if v and clips:
            srcd = v.find('source')['src'] if v.find('source') else v.get('src')
            pd = v.get('poster')
            _clip(v, {'d': (srcd, pd, '16/9'), 't': (srcd, pd, '16/9'), 'm': clips['film_m']})
            v['style'] += ' background:#0a100c;'
            v['data-noplay'] = ''
            v['preload'] = 'metadata'
        for a in [x for x in soup.find_all('a') if '9:16' in x.get_text()]:
            _add(a, 'r-hide-m')
            if a.parent: _add(a.parent, 'r-linkrow')
    return soup.body.decode_contents() if soup.body else str(soup)


CSS_MICRO = r"""
/* ---------- responsive layer, microsites ---------- */
.r-vwrap{height:auto !important}
.r-vwrap > div{margin-left:0 !important}
.r-vid{display:block; width:100% !important; height:auto !important}
@media (max-width: %(WIDE)dpx){
  .r-fs88{font-size:76px !important}
  .r-mx64{margin-left:52px !important; margin-right:52px !important}
  #top .r-fsh1{font-size:76px !important}
}
@media (max-width: 1180px){
  /* the section links no longer fit next to the logo: they move into the menu */
  .r-nav,.r-hide-t{display:none !important}
  .nav-panel .r-mob{display:flex !important}
  .nav-panel .nav-h.r-mob{display:block !important}
  .r-hdr-r{margin-left:auto}
}
@media (max-width: %(TABLET)dpx){
  #top > div.r-hero{height:clamp(640px, 82vh, 920px) !important}
  .r-g4{grid-template-columns:repeat(2, minmax(0,1fr)) !important; row-gap:32px !important}
  .r-fs88{font-size:64px !important}
  .r-fs64{font-size:52px !important}
  .r-fs26{font-size:24px !important}
  .r-gkv2{grid-template-columns:120px minmax(0,1fr) !important}
  img.r-h380{height:320px !important}
  div.r-h380{height:auto !important; min-height:320px}
  .r-gchart{grid-template-columns:132px minmax(0,1fr) !important}
  .r-wrap{flex-wrap:wrap; row-gap:10px !important}
  .r-tline{display:none !important}
  #next .r-g4 > #ai-infrastructure{grid-column:1 / -1 !important}
  .r-mx64{margin-left:40px !important; margin-right:40px !important}
  .r-fig{margin-top:48px !important}
  .r-ctarow{flex-wrap:wrap; gap:24px 40px !important}
  #field .r-g4 > div{justify-content:space-between}
  #field .r-g4 > div > .r-fs30{min-height:0 !important}
}
@media (max-width: %(PHONE)dpx){
  #top > div.r-hero{height:min(100vh, 760px) !important; height:min(100svh, 760px) !important}
  .r-g4{gap:28px 12px !important}
  #next .r-g4{grid-template-columns:1fr !important; gap:36px !important}
  .r-fs88{font-size:52px !important}
  .r-fs64{font-size:44px !important}
  .r-fs26{font-size:23px !important}
  .r-gkv{grid-template-columns:100px minmax(0,1fr) !important; gap:12px !important}
  .r-gkv2{grid-template-columns:1fr !important; gap:4px !important}
  img.r-h380{height:240px !important}
  div.r-h380{min-height:0}
  .r-cardp{padding:24px 20px 28px !important}
  .r-chartbox{padding:24px 16px 20px !important}
  .r-gchart{grid-template-columns:1fr !important; gap:8px !important}
  .r-mh240,.r-mh300{min-height:0 !important}
  .r-ctarow{flex-direction:column; align-items:flex-start !important; gap:24px !important}
  .r-mx64{margin-left:20px !important; margin-right:20px !important}
  .r-linkrow{flex-direction:column; align-items:flex-start !important; gap:16px !important}
  .r-linkrow > div{flex-wrap:wrap; gap:20px 28px !important}
  .r-linkrow a{white-space:nowrap}
  .r-hide-m{display:none !important}
  .r-fighead{flex-direction:column; align-items:flex-start !important; gap:6px}
  .r-fig{margin-top:36px !important; gap:16px !important}
}
""".replace('%(WIDE)dpx', f'{WIDE}px').replace('%(TABLET)dpx', f'{TABLET}px').replace('%(PHONE)dpx', f'{PHONE}px')
