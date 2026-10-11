// render SVG files to PNG with Chromium (uses the fonts installed through fontconfig)
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';
const jobs = JSON.parse(readFileSync(process.argv[2], 'utf8')); // [{svg, out, w, h, scale}]
const b = await chromium.launch();
for (const j of jobs) {
  const ctx = await b.newContext({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: j.scale || 1 });
  const p = await ctx.newPage();
  const svg = readFileSync(j.svg, 'utf8');
  await p.setContent(`<!doctype html><html><head><style>html,body{margin:0;padding:0;overflow:hidden}svg{display:block}</style></head><body>${svg.replace(/<svg /, `<svg style="width:${j.w}px;height:${j.h}px" `)}</body></html>`);
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(80);
  await p.screenshot({ path: j.out, clip: { x: 0, y: 0, width: j.w, height: j.h } });
  await ctx.close();
}
await b.close();
console.log('rendered', jobs.length);
