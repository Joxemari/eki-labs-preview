"""Builds /brand/download/: every file of the brand kit, one by one, and the logo builder.

Run from the repo root after the kit zips are in place:
    python3 source/brand-kit/build_download.py
It unpacks site/brand/kit/eki-labs-brand-kit.zip into site/brand/kit/files/ and writes
site/brand/download/index.html. The builder takes its artwork from the day SVGs of the kit,
so it always draws the same curves as the logo files.
"""
import html, json, os, re, shutil, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, 'site')
KIT_ZIP = os.path.join(SITE, 'brand', 'kit', 'eki-labs-brand-kit.zip')
FILES = os.path.join(SITE, 'brand', 'kit', 'files')
PAGE = os.path.join(SITE, 'brand', 'download', 'index.html')
BRAND = os.path.join(SITE, 'brand', 'index.html')
TOP = 'eki-labs-brand-kit/'

# The 16 colour tokens (CLAUDE.md, /brand). Order = how they appear in the pickers.
TOKENS = [
    ('sol', '#FFD54A'), ('yerba', '#58E9AE'), ('tierra', '#CF8166'), ('noche', '#0A100C'),
    ('yerba honda', '#056C4A'), ('tierra honda', '#964A2F'), ('origen', '#311D16'), ('bosque', '#0A281A'),
    ('arena', '#F4F2EC'), ('piedra', '#EBE6D8'), ('línea', '#D6D1C3'), ('pizarra', '#555A52'),
    ('grafito', '#141B16'), ('acero', '#2B332D'), ('niebla', '#A1A69F'), ('blanco', '#FFFFFF'),
]

SECTIONS = [
    ('01-logo/logo', 'eki.labs', 'Symbol and name, the everyday logo.'),
    ('01-logo/eki', 'eki.', 'The base of the name on its own: symbol and «eki.».'),
    ('01-logo/symbol', 'Symbol', 'The sun over three rows, on its own.'),
    ('01-logo/symbol-small', 'Small symbol', 'Two rows, for 16–31 px: favicons and tiny icons.'),
    ('01-logo/signature', 'eki.labs and tagline', 'One block, as it always travels.'),
    ('01-logo/signature-vertical', 'eki.labs and tagline, stacked', 'For square and tall spaces.'),
    ('02-colour', 'Colour', 'The palette for Adobe (ASE), CSS, JSON and a swatch card.'),
    ('03-type', 'Type', 'Zilla Slab, Work Sans and Geist Mono, with their licences.'),
    ('04-social', 'Social', 'Avatars, covers, posts and the link preview image.'),
    ('', 'Guide', 'What is in the kit and how to use it.'),
]


def unpack():
    if os.path.isdir(FILES):
        shutil.rmtree(FILES)
    names = []
    with zipfile.ZipFile(KIT_ZIP) as z:
        for info in z.infolist():
            if info.is_dir() or not info.filename.startswith(TOP):
                continue
            rel = info.filename[len(TOP):]
            if '..' in rel.split('/'):
                raise SystemExit('unexpected path in kit: ' + info.filename)
            dest = os.path.join(FILES, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(info) as src, open(dest, 'wb') as out:
                shutil.copyfileobj(src, out)
            names.append((rel, info.file_size))
    return sorted(names)


def size(n):
    return f'{n / 1048576:.1f} MB' if n >= 1048576 else f'{max(1, round(n / 1024))} KB'


def file_list(names):
    out = []
    for prefix, title, note in SECTIONS:
        rows = [(r, n) for r, n in names if (r.startswith(prefix + '/') if prefix else '/' not in r)]
        if not rows:
            continue
        items = ''.join(
            f'<li><a href="../kit/files/{html.escape(r)}" download>{html.escape(r.rsplit("/", 1)[-1])}</a><span>{size(n)}</span></li>'
            for r, n in rows)
        out.append(f'<section class="files"><h3>{title}</h3><p class="muted">{note}</p><ul>{items}</ul></section>')
    return ''.join(out)


def main():
    names = unpack()
    import logos
    art = logos.builder_data()
    head = open(os.path.join(SITE, 'legal', 'index.html'), encoding='utf-8').read()
    style = re.search(r'<style>(.*?)</style>', head, re.S).group(1)
    header = re.search(r'<header class="top">.*?</header>', head, re.S).group(0)
    fund = re.search(r'<footer>.*?</footer>\s*<div class="logos">.*?</div>', head, re.S).group(0)
    up = lambda x: x.replace('href="../', 'href="../../').replace('src="../', 'src="../../')  # one folder deeper than legal/
    header, fund = up(header), up(fund)
    page = TEMPLATE
    for k, v in {
        '%STYLE%': style, '%HEADER%': header, '%FUND%': fund, '%FILES%': file_list(names),
        '%COUNT%': str(len(names)),
    }.items():
        page = page.replace(k, v)
    page = page.replace('%BUILDER_HTML%', builder_html('')).replace('%BUILDER_JS%', builder_js('', art)).replace('%BUILDER_CSS%', builder_css())
    os.makedirs(os.path.dirname(PAGE), exist_ok=True)
    open(PAGE, 'w', encoding='utf-8').write(page)
    print(len(names), 'files ·', PAGE)
    brand_page(art)


def builder_css():
    import logos
    g = lambda stops: 'linear-gradient(180deg,' + ','.join(f'{c} {round(o * 100)}%' for o, c in stops) + ')'
    return BUILDER_CSS.replace('%SUNCSS%', g(logos.SUN_STOPS)).replace('%FULLCSS%', g(logos.FULL_STOPS))


def builder_html(prefix):
    return BUILDER_HTML.replace('%P%', prefix)


def builder_js(prefix, art):
    return (BUILDER_JS.replace('%P%', prefix).replace('%ART%', json.dumps(art, ensure_ascii=False, separators=(',', ':')))
            .replace('%TOKENS%', json.dumps(TOKENS, ensure_ascii=False))
            .replace('%SUNHEX%', ' · '.join(dict.fromkeys(c for _, c in __import__('logos').SUN_STOPS)))
            .replace('%FULLHEX%', ' · '.join(dict.fromkeys(c for _, c in __import__('logos').FULL_STOPS))))


def brand_page(art):
    """Put the same logo builder on the brand page, in Downloads, before the social sizes."""
    s = open(BRAND, encoding='utf-8').read()
    s = re.sub(r'<style data-lb>.*?</style>', '', s, flags=re.S)
    s = re.sub(r'<!--lb:html-->.*?<!--/lb:html-->', '', s, flags=re.S)
    s = re.sub(r'<script data-lb>.*?</script>\n?', '', s, flags=re.S)
    block = ('<!--lb:html--><div id="logo-builder" style="grid-column: 1 / -1; scroll-margin-top: 96px;">'
             '<div style="display: grid; grid-template-columns: repeat(12, minmax(0px, 1fr)); column-gap: 24px; align-items: start;">'
             '<div style="grid-column: 1 / span 3; display: flex; flex-direction: column; gap: 6px; padding-top: 2px;">'
             '<span style="font-family: &quot;Geist Mono&quot;, Menlo, monospace; font-size: 11px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: rgb(10, 16, 12);">Logo builder</span>'
             '<span style="font-size: 14px; line-height: 21px; color: rgb(85, 90, 82);">Write the name after «eki.», pick the artwork and three colours: the symbol (the full gradient, or the sun in its gradient with the rows in ink), the letters, and the background. '
             'It flags any combination the brand rules do not allow.</span></div>'
             '<div style="grid-column: 4 / span 9;">' + builder_html('lb-') +
             '<noscript><p style="font-size: 14px; color: rgb(85, 90, 82);">The logo builder needs JavaScript. The kit above works without it.</p></noscript>'
             '</div></div></div><!--/lb:html-->')
    anchor = s.index('<div style="grid-column: 1 / -1;"><div style="display: grid; grid-template-columns: repeat(12, minmax(0px, 1fr)); column-gap: 24px; align-items: start;"><div style="grid-column: 1 / span 3; display: flex; flex-direction: column; gap: 6px; padding-top: 2px;"><span style="font-family: &quot;Geist Mono&quot;, Menlo, monospace; font-size: 11px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: rgb(10, 16, 12);">Sizes in the kit</span>')
    s = s[:anchor] + block + s[anchor:]
    s = s.replace('</head>', '<style data-lb>' + builder_css() + '</style></head>', 1)
    s = s.replace('</body>', builder_js('lb-', art).replace('<script>', '<script data-lb>', 1) + '\n</body>', 1)
    s = s.replace('>Every file one by one, and the logo builder →</a>', '>Every file one by one →</a>')
    open(BRAND, 'w', encoding='utf-8').write(s)
    print('logo builder ·', BRAND)


BUILDER_CSS = r'''.lb{--linea:#D6D1C3;--noche:#0A100C;--arena:#F4F2EC;--pizarra:#555A52;--piedra:#EBE6D8;--yhonda:#056C4A}
.lb .builder{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:32px;margin:24px 0 8px;align-items:start}
.lb .stage{border:1px solid var(--linea);border-radius:16px;min-height:360px;display:flex;align-items:center;justify-content:center;padding:32px;background-image:linear-gradient(45deg,#e7e3d6 25%,transparent 25%,transparent 75%,#e7e3d6 75%),linear-gradient(45deg,#e7e3d6 25%,transparent 25%,transparent 75%,#e7e3d6 75%);background-size:20px 20px;background-position:0 0,10px 10px}
.lb .stage svg{display:block;max-width:100%;max-height:420px;height:auto}
.lb .panel{display:flex;flex-direction:column;gap:20px}
.lb .label{display:block;font-family:'Geist Mono',Menlo,monospace;font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--pizarra);margin:0 0 8px}
.lb .seg{display:flex;flex-wrap:wrap;gap:6px}
.lb .seg button,.lb .btn{font:inherit;font-size:14px;line-height:20px;padding:8px 12px;border-radius:4px;border:1px solid var(--linea);background:#fff0;color:var(--noche);cursor:pointer}
.lb .seg button[aria-pressed="true"]{background:var(--noche);border-color:var(--noche);color:var(--arena)}
.lb .sw{display:grid;grid-template-columns:repeat(8,1fr);gap:6px}
.lb .sw button{aspect-ratio:1;border-radius:6px;border:1px solid var(--linea);cursor:pointer;padding:0;position:relative}
.lb .sw button[aria-pressed="true"]{outline:2px solid var(--noche);outline-offset:2px}
.lb .sw button.none{background:repeating-linear-gradient(45deg,#fff 0 4px,#e7e3d6 4px 8px)}
.lb .sw button.sun{background:%SUNCSS%}
.lb .sw button.full{background:%FULLCSS%}
.lb .end{font:inherit;font-family:'Geist Mono',Menlo,monospace;font-size:15px;line-height:22px;width:100%;box-sizing:border-box;padding:9px 12px;border:1px solid #797C72;border-radius:4px;background:#fff0;color:var(--noche)}
.lb .end:focus-visible{outline:2px solid var(--noche);outline-offset:2px}
.lb .picked{font-family:'Geist Mono',Menlo,monospace;font-size:12px;color:var(--pizarra);margin-top:6px}
.lb .checks{margin:0;padding:12px 14px;border-radius:12px;background:var(--piedra);font-size:14px;line-height:21px;list-style:none}
.lb .checks li{margin:0}.checks li+li{margin-top:6px}
.lb .checks .ok{color:var(--yhonda)}.checks .warn{color:#964A2F}
.lb .dl{display:flex;flex-wrap:wrap;gap:8px}
.lb .btn.primary{background:var(--noche);border-color:var(--noche);color:var(--arena)}
@media (max-width:1023px){.lb .builder{grid-template-columns:1fr}}
'''

BUILDER_HTML = r'''<div class="lb">
<div class="builder">
    <div class="stage" id="%P%stage" aria-live="polite"></div>
    <div class="panel">
      <div><label class="label" for="%P%end">Name after eki.</label><input class="end" id="%P%end" type="text" value="labs" maxlength="16" autocomplete="off" spellcheck="false" aria-describedby="%P%end-hint"><div class="picked" id="%P%end-hint">Lowercase letters, figures and hyphens. Empty for «eki.» alone.</div></div>
      <div><span class="label">Artwork</span><div class="seg" id="%P%lockup"></div></div>
      <div><span class="label">Ready-made</span><div class="seg" id="%P%presets"></div></div>
      <div><span class="label">Sun</span><div class="sw" id="%P%sw-sym"></div><div class="picked" id="%P%pk-sym"></div></div>
      <div><span class="label">Letters and rows</span><div class="sw" id="%P%sw-ink"></div><div class="picked" id="%P%pk-ink"></div></div>
      <div><span class="label">Background</span><div class="sw" id="%P%sw-bg"></div><div class="picked" id="%P%pk-bg"></div></div>
      <ul class="checks" id="%P%checks"></ul>
      <div><span class="label">Download</span><div class="dl">
        <button class="btn primary" id="%P%dl-svg" type="button">SVG</button>
        <button class="btn" id="%P%dl-png1" type="button">PNG 1200 px</button>
        <button class="btn" id="%P%dl-png4" type="button">PNG 4000 px</button>
      </div></div>
    </div>
  </div>
</div>
'''

BUILDER_JS = r'''<script>
(function () {
  var ART = %ART%, TOKENS = %TOKENS%, SUN = 'original', FULL = 'full';
  var HEX = {}; TOKENS.forEach(function (t) { HEX[t[0]] = t[1]; });
  var PRESETS = [['Day', 'noche', FULL, 'arena'], ['Night', 'arena', FULL, 'noche'], ['Day · sun gradient', 'noche', SUN, 'arena'], ['Night · sun gradient', 'arena', SUN, 'noche'], ['Black', 'noche', 'noche', 'none'], ['White', 'blanco', 'blanco', 'none']];
  var LOCKUPS = [['logo', 'Logo'], ['signature', 'Logo and tagline'], ['stacked', 'Stacked with tagline'], ['symbol', 'Symbol']];
  var S = { lockup: 'logo', end: 'labs', ink: 'noche', sym: FULL, bg: 'arena' };
  var $ = function (id) { return document.getElementById('%P%' + id); };
  function lum(h) { var c = [1, 3, 5].map(function (i) { var v = parseInt(h.substr(i, 2), 16) / 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  function f(n) { return Math.round(n * 100) / 100; }
  // the name in curves: «eki.» in Geist 600, the ending in Geist 400 (no kerning, as in the kit files)
  function word() {
    var out = ART.base.map(function (d) { return '<path d="' + d + '" fill="{ink}"/>'; }).join(''), x = ART.baseAdv, x1 = ART.baseX1;
    S.end.split('').forEach(function (ch) { var g = ART.glyphs[ch]; if (!g) return; out += '<path transform="translate(' + x + ' 0)" d="' + g.d + '" fill="{ink}"/>'; x1 = x + g.x1; x += g.adv; });
    return { body: out, w: x1 };
  }
  function tag(t, dx) { var b = t.box; return '<g transform="translate(' + f(b[0] + dx) + ' ' + f(b[1]) + ') scale(' + t.k + ') translate(' + f(-b[0]) + ' ' + f(-b[1]) + ')"><path d="' + t.d + '" fill="{ink}"/></g>'; }
  function art() {
    var A = ART, sym = A.symbol, w, b, tw, block;
    if (S.lockup === 'symbol') return { vb: [0, 0, 100, 100], body: sym, clear: 25 };
    w = word();
    var logo = '<g transform="translate(0 ' + A.symY + ') scale(' + A.symScale + ')">' + sym + '</g><g transform="translate(' + A.wordX + ' 0)">' + w.body + '</g>';
    if (S.lockup === 'logo') return { vb: [0, A.symY, A.wordX + w.w, 100 * A.symScale], body: logo, clear: 100 * A.symScale / 4 };
    if (S.lockup === 'signature') {
      b = A.tagH.box; tw = b[2] * A.tagH.k;
      return { vb: [0, A.symY, Math.max(A.wordX + w.w, b[0] + tw), b[1] + b[3] * A.tagH.k - A.symY], body: logo + tag(A.tagH, 0), clear: 100 * A.symScale / 4 };
    }
    b = A.tagV.box; tw = b[2] * A.tagV.k; block = Math.max(w.w, tw, 100 * A.vSymScale);
    return {
      vb: [0, 0, block, b[1] + b[3] * A.tagV.k],
      body: '<g transform="translate(' + f(block / 2 - 50 * A.vSymScale) + ' 0) scale(' + A.vSymScale + ')">' + sym + '</g><g transform="translate(' + f((block - w.w) / 2) + ' ' + A.vWordY + ')">' + w.body + '</g>' + tag(A.tagV, (block - tw) / 2 - b[0]),
      clear: 100 * A.vSymScale / 4
    };
  }
  function title() { return S.lockup === 'symbol' ? 'eki.labs' : 'eki.' + S.end; }
  function svg(px) {
    var a = art(), v = a.vb, pad = S.bg === 'none' ? 0 : a.clear;
    var x = f(v[0] - pad), y = f(v[1] - pad), w = f(v[2] + 2 * pad), h = f(v[3] + 2 * pad), W = px || 480, H = f(W * h / w);
    var sym = S.sym === SUN ? 'url(#eki-sun)' : S.sym === FULL ? 'url(#eki-sun-full)' : HEX[S.sym];
    var rows = S.sym === FULL ? 'url(#eki-sun-full)' : HEX[S.ink];
    var body = a.body.split('{sym}').join(sym).split('{rows}').join(rows).split('{ink}').join(HEX[S.ink]);
    var bg = S.bg === 'none' ? '' : '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + HEX[S.bg] + '"/>';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="' + [x, y, w, h].join(' ') + '" width="' + W + '" height="' + H + '"><title>' + title() + '</title>' + (S.sym === SUN ? ART.sunDefs : S.sym === FULL ? ART.fullDefs : '') + bg + body + '</svg>';
  }
  function checks() {
    var out = [], bgHex = S.bg === 'none' ? null : HEX[S.bg];
    if (S.sym !== SUN && S.sym !== FULL && S.sym !== S.ink) out.push(['warn', 'The symbol always carries a gradient. Only one-ink versions take the colour of the letters.']);
    if (S.bg === 'yerba' || S.bg === 'sol') out.push(['warn', 'Never place the logo on yerba or on sol.']);
    if (S.sym !== SUN && S.sym !== FULL && S.sym === S.bg) out.push(['warn', 'Sun and background are the same colour: the sun disappears.']);
    if (S.ink === S.bg) out.push(['warn', 'Letters, rows and background are the same colour.']);
    else if (bgHex && ratio(HEX[S.ink], bgHex) < 3) out.push(['warn', 'Letters and rows on this background are hard to read (contrast ' + ratio(HEX[S.ink], bgHex).toFixed(1) + ':1, minimum 3:1).']);
    if (!S.end && S.lockup !== 'logo' && S.lockup !== 'symbol') out.push(['warn', 'eki. on its own goes without the tagline. Sign with eki.labs.']);
    if ([S.ink, S.sym, S.bg].indexOf('blanco') > -1) out.push(['note', 'Blanco is only for other people’s surfaces: email, documents.']);
    if (!bgHex) out.push(['note', 'Transparent background: check it against the ground where it will sit.']);
    if (!out.some(function (c) { return c[0] === 'warn'; })) out.unshift(['ok', 'Within the brand rules.']);
    return out;
  }
  function name() { var who = S.lockup === 'symbol' ? 'eki-labs-symbol' : 'eki' + (S.end ? '-' + S.end : '') + '-' + (S.lockup === 'logo' ? 'logo' : S.lockup === 'signature' ? 'signature' : 'signature-vertical'); return who + '-' + [S.ink, S.sym === SUN ? 'sun' : S.sym === FULL ? 'full' : S.sym, S.bg].map(function (t) { return t.replace(/\s+/g, '-').replace('í', 'i'); }).join('-'); }
  function paint() {
    $('stage').innerHTML = svg();
    ['lockup', 'presets'].forEach(function (g) { $(g).querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', g === 'lockup' ? String(b.dataset.v === S.lockup) : String(b.dataset.ink === S.ink && b.dataset.sym === S.sym && b.dataset.bg === S.bg)); }); });
    ['sym', 'ink', 'bg'].forEach(function (k) {
      $('sw-' + k).querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.v === S[k])); });
      $('pk-' + k).textContent = S[k] === 'none' ? 'transparent' : S[k] === SUN ? 'sun gradient · %SUNHEX%' : S[k] === FULL ? 'full gradient · %FULLHEX%' : S[k] + ' · ' + HEX[S[k]];
    });
    $('checks').innerHTML = checks().map(function (c) { return '<li class="' + (c[0] === 'warn' ? 'warn' : c[0] === 'ok' ? 'ok' : '') + '">' + c[1] + '</li>'; }).join('');
  }
  function btn(parent, text, data, style, cls) { var b = document.createElement('button'); b.type = 'button'; if (text) b.textContent = text; Object.keys(data).forEach(function (k) { b.dataset[k] = data[k]; }); if (style) b.style.background = style; if (cls) b.className = cls; parent.appendChild(b); return b; }
  LOCKUPS.forEach(function (l) { btn($('lockup'), l[1], { v: l[0] }).onclick = function () { S.lockup = l[0]; paint(); }; });
  $('end').addEventListener('input', function () { var v = this.value.toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 16); if (v !== this.value) this.value = v; S.end = v; paint(); });
  PRESETS.forEach(function (p) { btn($('presets'), p[0], { ink: p[1], sym: p[2], bg: p[3] }).onclick = function () { S.ink = p[1]; S.sym = p[2]; S.bg = p[3]; paint(); }; });
  ['sym', 'ink', 'bg'].forEach(function (k) {
    var box = $('sw-' + k);
    if (k === 'bg') { var n = btn(box, '', { v: 'none' }, null, 'none'); n.title = 'transparent'; n.setAttribute('aria-label', 'transparent'); n.onclick = function () { S.bg = 'none'; paint(); }; }
    if (k === 'sym') {
      var g2 = btn(box, '', { v: FULL }, null, 'full'); g2.title = 'full gradient, sun and rows'; g2.setAttribute('aria-label', 'full gradient, sun and rows'); g2.onclick = function () { S.sym = FULL; paint(); };
      var g = btn(box, '', { v: SUN }, null, 'sun'); g.title = 'sun gradient, rows in ink'; g.setAttribute('aria-label', 'sun gradient, rows in ink'); g.onclick = function () { S.sym = SUN; paint(); };
    }
    TOKENS.forEach(function (t) { var b = btn(box, '', { v: t[0] }, t[1]); b.title = t[0] + ' ' + t[1]; b.setAttribute('aria-label', t[0]); b.onclick = function () { S[k] = t[0]; paint(); }; });
  });
  function save(blob, file) { var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = file; document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000); }
  $('dl-svg').onclick = function () { save(new Blob([svg()], { type: 'image/svg+xml' }), name() + '.svg'); };
  function png(px) {
    var s = svg(px), img = new Image(), url = URL.createObjectURL(new Blob([s], { type: 'image/svg+xml' }));
    img.onload = function () { var c = document.createElement('canvas'); c.width = px; c.height = Math.round(img.height); c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(url); c.toBlob(function (b) { save(b, name() + '-' + px + 'px.png'); }, 'image/png'); };
    img.src = url;
  }
  $('dl-png1').onclick = function () { png(1200); };
  $('dl-png4').onclick = function () { png(4000); };
  paint();
})();
</script>'''


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Brand downloads · eki.labs</title>
<meta name="description" content="Every file of the eki.labs brand kit, one by one, and a logo builder in the brand colours.">
<link rel="canonical" href="https://ekilabs.com/brand/download/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="eki.labs">
<meta property="og:title" content="Brand downloads · eki.labs">
<meta property="og:description" content="Every file of the eki.labs brand kit, one by one, and a logo builder in the brand colours.">
<meta property="og:url" content="https://ekilabs.com/brand/download/">
<meta property="og:image" content="https://ekilabs.com/social-preview.png">
<meta name="theme-color" content="#0A100C">
<link rel="icon" href="../../favicon.ico" sizes="32x32">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../../apple-touch-icon.png">
<link rel="preload" href="../../fonts/zilla-slab-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../../fonts/work-sans-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../../fonts/fonts.css">
<style>
%STYLE%
.inner{max-width:none}
.lead{font-size:19px;line-height:29px;max-width:720px;color:var(--pizarra)}
%BUILDER_CSS%
.files{margin-top:36px}
.files h3{font-family:'Zilla Slab',Georgia,serif;font-weight:400;font-size:24px;margin:0 0 4px}
.files ul{list-style:none;padding:0;margin:12px 0 0;columns:2;column-gap:32px}
.files li{display:flex;justify-content:space-between;gap:12px;break-inside:avoid;padding:7px 0;border-bottom:1px solid var(--linea);font-size:15px;line-height:22px}
.files li span{font-family:'Geist Mono',Menlo,monospace;font-size:12px;color:var(--pizarra);white-space:nowrap}
.files li a{overflow-wrap:anywhere}
.zips{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 0}
.zips .btn{font-size:14px;line-height:20px;padding:8px 12px;border-radius:4px;border:1px solid var(--linea);color:var(--noche)}
@media (max-width:1023px){.files ul{columns:1}}
</style>
</head>
<body>
%HEADER%
<main class="card"><div class="inner">
<p class="eyebrow"><span></span>Brand</p>
<h1>Brand downloads.</h1>
<p class="lead">Build the logo in the colours you need, or take any file of the kit on its own. The rules are on the <a href="../">brand page</a>.</p>

<h2 id="builder">Logo builder</h2>
<p class="muted">Write the name after «eki.», pick the artwork and three colours: the symbol (the full gradient, or the sun in its gradient with the rows in ink), the letters and the background. The tagline is always the same. The builder flags any combination the brand rules do not allow.</p>
%BUILDER_HTML%
<noscript><p class="muted">The logo builder needs JavaScript. The files below work without it.</p></noscript>

<h2 id="files">Every file, one by one</h2>
<p class="muted">%COUNT% files. Or take them in one go:</p>
<div class="zips"><a class="btn" href="../kit/eki-labs-brand-kit.zip">Whole kit (zip)</a><a class="btn" href="../kit/eki-labs-logos.zip">Logos</a><a class="btn" href="../kit/eki-labs-colours.zip">Colour</a><a class="btn" href="../kit/eki-labs-type.zip">Type</a><a class="btn" href="../kit/eki-labs-social.zip">Social</a></div>
%FILES%
</div></main>
%FUND%
%BUILDER_JS%
</body>
</html>
'''

if __name__ == '__main__':
    main()
