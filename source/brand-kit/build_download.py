"""Builds /brand/download/: every file of the brand kit, one by one, and the logo builder.

Run from the repo root after the kit zips are in place:
    python3 source/brand-kit/build_download.py
It unpacks site/brand/kit/eki-labs-brand-kit.zip into site/brand/kit/files/ and writes
site/brand/download/index.html. The builder takes its artwork from the day SVGs of the kit,
so it always draws the same curves as the logo files.
"""
import html, json, os, re, shutil, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, 'site')
KIT_ZIP = os.path.join(SITE, 'brand', 'kit', 'eki-labs-brand-kit.zip')
FILES = os.path.join(SITE, 'brand', 'kit', 'files')
PAGE = os.path.join(SITE, 'brand', 'download', 'index.html')
TOP = 'eki-labs-brand-kit/'

# The 16 colour tokens (CLAUDE.md, /brand). Order = how they appear in the pickers.
TOKENS = [
    ('sol', '#FFD54A'), ('yerba', '#58E9AE'), ('tierra', '#CF8166'), ('noche', '#0A100C'),
    ('yerba honda', '#056C4A'), ('tierra honda', '#964A2F'), ('origen', '#311D16'), ('bosque', '#0A281A'),
    ('arena', '#F4F2EC'), ('piedra', '#EBE6D8'), ('línea', '#D6D1C3'), ('pizarra', '#555A52'),
    ('grafito', '#141B16'), ('acero', '#2B332D'), ('niebla', '#A1A69F'), ('blanco', '#FFFFFF'),
]

# Lockups: kit file, and the symbol's diameter in that file's units (clear space = a quarter of it).
LOCKUPS = [
    ('symbol', 'Symbol', '01-logo/symbol/eki-labs-symbol-day.svg', 100),
    ('logo', 'Logo', '01-logo/logo/eki-labs-logo-day.svg', 923),
    ('signature', 'Logo and tagline', '01-logo/signature/eki-labs-signature-day.svg', 923),
    ('signature-vertical', 'Logo and tagline, stacked', '01-logo/signature-vertical/eki-labs-signature-vertical-day.svg', 1349),
]

SECTIONS = [
    ('01-logo/logo', 'Logo', 'Sun and wordmark, the everyday logo.'),
    ('01-logo/symbol', 'Symbol', 'The sun over three rows, on its own.'),
    ('01-logo/symbol-small', 'Small symbol', 'Two rows, for 16–31 px: favicons and tiny icons.'),
    ('01-logo/signature', 'Logo and tagline', 'One block, as it always travels.'),
    ('01-logo/signature-vertical', 'Logo and tagline, stacked', 'For square and tall spaces.'),
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


def artwork(rel):
    """viewBox, the sun path(s) and the ink path(s) of a day SVG, keeping its transforms."""
    s = open(os.path.join(FILES, rel), encoding='utf-8').read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    body = s[s.index('>', s.index('<svg')) + 1:s.rindex('</svg>')]
    body = re.sub(r'<title>.*?</title>', '', body)
    assert body.count('#FFD54A') == 1, rel
    # the symbol (sun + three rows) is the first group in logo files and the whole file in the symbol;
    # its ink paths are the rows, every other ink path is lettering (wordmark, tagline)
    i = body.find('</g>')
    sym, rest = (body, '') if '<g' not in body else (body[:i], body[i:])
    sym = sym.replace('fill="#FFD54A"', 'fill="{sun}"').replace('fill="#0A100C"', 'fill="{rows}"')
    body = sym + rest.replace('fill="#0A100C"', 'fill="{ink}"')
    assert body.count('{sun}') == 1 and body.count('{rows}') == 3, rel
    assert '#' not in re.sub(r'fill="\{(sun|rows|ink)\}"', '', body), rel
    return {'viewBox': vb, 'body': body}


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
    art = {key: dict(artwork(rel), label=label, clear=diam / 4) for key, label, rel, diam in LOCKUPS}
    head = open(os.path.join(SITE, 'legal', 'index.html'), encoding='utf-8').read()
    style = re.search(r'<style>(.*?)</style>', head, re.S).group(1)
    header = re.search(r'<header class="top">.*?</header>', head, re.S).group(0)
    fund = re.search(r'<footer>.*?</footer>\s*<div class="logos">.*?</div>', head, re.S).group(0)
    up = lambda x: x.replace('href="../', 'href="../../').replace('src="../', 'src="../../')  # one folder deeper than legal/
    header, fund = up(header), up(fund)
    page = TEMPLATE
    for k, v in {
        '%STYLE%': style, '%HEADER%': header, '%FUND%': fund, '%FILES%': file_list(names),
        '%COUNT%': str(len(names)), '%ART%': json.dumps(art, ensure_ascii=False),
        '%TOKENS%': json.dumps(TOKENS, ensure_ascii=False),
    }.items():
        page = page.replace(k, v)
    os.makedirs(os.path.dirname(PAGE), exist_ok=True)
    open(PAGE, 'w', encoding='utf-8').write(page)
    print(len(names), 'files ·', PAGE)


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
.builder{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:32px;margin:24px 0 8px;align-items:start}
.stage{border:1px solid var(--linea);border-radius:16px;min-height:360px;display:flex;align-items:center;justify-content:center;padding:32px;background-image:linear-gradient(45deg,#e7e3d6 25%,transparent 25%,transparent 75%,#e7e3d6 75%),linear-gradient(45deg,#e7e3d6 25%,transparent 25%,transparent 75%,#e7e3d6 75%);background-size:20px 20px;background-position:0 0,10px 10px}
.stage svg{display:block;max-width:100%;max-height:420px;height:auto}
.panel{display:flex;flex-direction:column;gap:20px}
.label{display:block;font-family:'Geist Mono',Menlo,monospace;font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:var(--pizarra);margin:0 0 8px}
.seg{display:flex;flex-wrap:wrap;gap:6px}
.seg button,.btn{font:inherit;font-size:14px;line-height:20px;padding:8px 12px;border-radius:4px;border:1px solid var(--linea);background:#fff0;color:var(--noche);cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--noche);border-color:var(--noche);color:var(--arena)}
.sw{display:grid;grid-template-columns:repeat(8,1fr);gap:6px}
.sw button{aspect-ratio:1;border-radius:6px;border:1px solid var(--linea);cursor:pointer;padding:0;position:relative}
.sw button[aria-pressed="true"]{outline:2px solid var(--noche);outline-offset:2px}
.sw button.none{background:repeating-linear-gradient(45deg,#fff 0 4px,#e7e3d6 4px 8px)}
.picked{font-family:'Geist Mono',Menlo,monospace;font-size:12px;color:var(--pizarra);margin-top:6px}
.checks{margin:0;padding:12px 14px;border-radius:12px;background:var(--piedra);font-size:14px;line-height:21px;list-style:none}
.checks li{margin:0}.checks li+li{margin-top:6px}
.checks .ok{color:var(--yhonda)}.checks .warn{color:#964A2F}
.dl{display:flex;flex-wrap:wrap;gap:8px}
.btn.primary{background:var(--noche);border-color:var(--noche);color:var(--arena)}
.files{margin-top:36px}
.files h3{font-family:'Zilla Slab',Georgia,serif;font-weight:400;font-size:24px;margin:0 0 4px}
.files ul{list-style:none;padding:0;margin:12px 0 0;columns:2;column-gap:32px}
.files li{display:flex;justify-content:space-between;gap:12px;break-inside:avoid;padding:7px 0;border-bottom:1px solid var(--linea);font-size:15px;line-height:22px}
.files li span{font-family:'Geist Mono',Menlo,monospace;font-size:12px;color:var(--pizarra);white-space:nowrap}
.files li a{overflow-wrap:anywhere}
.zips{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0 0}
@media (max-width:1023px){.builder{grid-template-columns:1fr}.files ul{columns:1}}
</style>
</head>
<body>
%HEADER%
<main class="card"><div class="inner">
<p class="eyebrow"><span></span>Brand</p>
<h1>Brand downloads.</h1>
<p class="lead">Build the logo in the colours you need, or take any file of the kit on its own. The rules are on the <a href="../">brand page</a>.</p>

<h2 id="builder">Logo builder</h2>
<p class="muted">Pick the artwork and four colours: the letters, the rows, the sun and the background. The builder flags any combination the brand rules do not allow.</p>
<div class="builder">
  <div class="stage" id="stage" aria-live="polite"></div>
  <div class="panel">
    <div><span class="label">Artwork</span><div class="seg" id="lockup"></div></div>
    <div><span class="label">Ready-made</span><div class="seg" id="presets"></div></div>
    <div><span class="label">Letters</span><div class="sw" id="sw-ink"></div><div class="picked" id="pk-ink"></div></div>
    <div><span class="label">Rows</span><div class="sw" id="sw-rows"></div><div class="picked" id="pk-rows"></div></div>
    <div><span class="label">Sun</span><div class="sw" id="sw-sun"></div><div class="picked" id="pk-sun"></div></div>
    <div><span class="label">Background</span><div class="sw" id="sw-bg"></div><div class="picked" id="pk-bg"></div></div>
    <ul class="checks" id="checks"></ul>
    <div><span class="label">Download</span><div class="dl">
      <button class="btn primary" id="dl-svg" type="button">SVG</button>
      <button class="btn" id="dl-png1" type="button">PNG 1200 px</button>
      <button class="btn" id="dl-png4" type="button">PNG 4000 px</button>
    </div></div>
  </div>
</div>
<noscript><p class="muted">The logo builder needs JavaScript. The files below work without it.</p></noscript>

<h2 id="files">Every file, one by one</h2>
<p class="muted">%COUNT% files. Or take them in one go:</p>
<div class="zips"><a class="btn" href="../kit/eki-labs-brand-kit.zip">Whole kit (zip)</a><a class="btn" href="../kit/eki-labs-logos.zip">Logos</a><a class="btn" href="../kit/eki-labs-colours.zip">Colour</a><a class="btn" href="../kit/eki-labs-type.zip">Type</a><a class="btn" href="../kit/eki-labs-social.zip">Social</a></div>
%FILES%
</div></main>
%FUND%
<script>
(function () {
  var ART = %ART%, TOKENS = %TOKENS%;
  var HEX = {}; TOKENS.forEach(function (t) { HEX[t[0]] = t[1]; });
  var PRESETS = [['Day', 'noche', 'sol', 'arena'], ['Night', 'arena', 'sol', 'noche'], ['Black', 'noche', 'noche', 'none'], ['White', 'blanco', 'blanco', 'none']];
  var S = { lockup: 'logo', ink: 'noche', rows: 'noche', sun: 'sol', bg: 'arena' };
  var $ = function (id) { return document.getElementById(id); };
  function lum(h) { var c = [1, 3, 5].map(function (i) { var v = parseInt(h.substr(i, 2), 16) / 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }); return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]; }
  function ratio(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  function svg(px) {
    var a = ART[S.lockup], v = a.viewBox.split(/\s+/).map(Number), pad = S.bg === 'none' ? 0 : a.clear;
    var x = v[0] - pad, y = v[1] - pad, w = v[2] + 2 * pad, h = v[3] + 2 * pad, W = px || 480, H = Math.round(W * h / w * 100) / 100;
    var body = a.body.split('{sun}').join(HEX[S.sun]).split('{rows}').join(HEX[S.rows]).split('{ink}').join(HEX[S.ink]);
    var bg = S.bg === 'none' ? '' : '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" fill="' + HEX[S.bg] + '"/>';
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="' + [x, y, w, h].join(' ') + '" width="' + W + '" height="' + H + '"><title>eki.labs</title>' + bg + body + '</svg>';
  }
  function checks() {
    var out = [], bgHex = S.bg === 'none' ? null : HEX[S.bg];
    var oneInk = S.sun === S.ink && S.rows === S.ink;
    if (S.sun !== 'sol' && !oneInk) out.push(['warn', 'The sun is always sol. Only one-ink versions put sun, rows and letters in one colour.']);
    if (S.rows !== S.ink) out.push(['note', 'Rows and letters in different colours: the kit always has them in one ink. Use it only where it has been agreed.']);
    if (S.bg === 'yerba' || S.bg === 'sol') out.push(['warn', 'Never place the logo on yerba or on sol.']);
    var used = [S.ink, S.rows, S.sun, S.bg];
    if (used.indexOf('sol') > -1 && used.indexOf('yerba') > -1) out.push(['warn', 'Sol and yerba never go together.']);
    if (bgHex && S.rows !== S.bg && ratio(HEX[S.rows], bgHex) < 3) out.push(['warn', 'Rows on this background are hard to see (contrast ' + ratio(HEX[S.rows], bgHex).toFixed(1) + ':1, minimum 3:1).']);
    if (S.rows === S.bg) out.push(['warn', 'Rows and background are the same colour: the rows disappear.']);
    if (S.ink === S.bg) out.push(['warn', 'Letters and background are the same colour.']);
    else if (bgHex && ratio(HEX[S.ink], bgHex) < 3) out.push(['warn', 'Letters on this background are hard to read (contrast ' + ratio(HEX[S.ink], bgHex).toFixed(1) + ':1, minimum 3:1).']);
    if (used.indexOf('blanco') > -1) out.push(['note', 'Blanco is only for other people’s surfaces: email, documents.']);
    if (!bgHex) out.push(['note', 'Transparent background: check it against the ground where it will sit.']);
    if (!out.some(function (c) { return c[0] === 'warn'; })) out.unshift(['ok', 'Within the brand rules.']);
    return out;
  }
  function name() { return 'eki-labs-' + S.lockup + '-' + (S.rows === S.ink ? [S.ink, S.sun, S.bg] : [S.ink, S.rows, S.sun, S.bg]).map(function (t) { return t.replace(/\s+/g, '-').replace('í', 'i'); }).join('-'); }
  function paint() {
    $('stage').innerHTML = svg();
    ['lockup', 'presets'].forEach(function (g) { $(g).querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', g === 'lockup' ? String(b.dataset.v === S.lockup) : String(b.dataset.ink === S.ink && S.rows === S.ink && b.dataset.sun === S.sun && b.dataset.bg === S.bg)); }); });
    ['ink', 'rows', 'sun', 'bg'].forEach(function (k) {
      $('sw-' + k).querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.v === S[k])); });
      $('pk-' + k).textContent = S[k] === 'none' ? 'transparent' : S[k] + ' · ' + HEX[S[k]];
    });
    $('checks').innerHTML = checks().map(function (c) { return '<li class="' + (c[0] === 'warn' ? 'warn' : c[0] === 'ok' ? 'ok' : '') + '">' + c[1] + '</li>'; }).join('');
  }
  function btn(parent, text, data, style, cls) { var b = document.createElement('button'); b.type = 'button'; if (text) b.textContent = text; Object.keys(data).forEach(function (k) { b.dataset[k] = data[k]; }); if (style) b.style.background = style; if (cls) b.className = cls; parent.appendChild(b); return b; }
  Object.keys(ART).forEach(function (k) { btn($('lockup'), ART[k].label, { v: k }).onclick = function () { S.lockup = k; paint(); }; });
  PRESETS.forEach(function (p) { btn($('presets'), p[0], { ink: p[1], sun: p[2], bg: p[3] }).onclick = function () { S.ink = p[1]; S.rows = p[1]; S.sun = p[2]; S.bg = p[3]; paint(); }; });
  ['ink', 'rows', 'sun', 'bg'].forEach(function (k) {
    var box = $('sw-' + k);
    if (k === 'bg') { var n = btn(box, '', { v: 'none' }, null, 'none'); n.title = 'transparent'; n.setAttribute('aria-label', 'transparent'); n.onclick = function () { S.bg = 'none'; paint(); }; }
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
</script>
</body>
</html>
'''

if __name__ == '__main__':
    main()
