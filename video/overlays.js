// Renders text overlays (captions, callouts, title cards) to transparent PNGs, in the site's own typefaces.
//   node video/overlays.js <spec.json> <out-dir>
// spec: [{ id, html, width? }]. Each becomes <out-dir>/<id>.png, cropped to the element. Also writes sizes.json.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FONTS = 'https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;700&display=swap';
const CSS = `
:root{--bg:#0B0D10;--fg:#EDE8DC;--fg2:#A9A497;--cyan:#00D4FF;--signal:#FFB020;--rook:#C9CED6;--copper:#D08A4E;--ok:#5BD69A;--alarm:#FF5C5C}
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:'DM Sans',system-ui,sans-serif;color:var(--fg);-webkit-font-smoothing:antialiased}
.serif{font-family:'Instrument Serif',Georgia,serif;font-weight:400}
.mono{font-family:'JetBrains Mono',monospace}
.cap{font-size:44px;font-weight:600;line-height:1.22;text-align:center;color:#fff;max-width:1240px;padding:8px 26px 10px;background:rgba(11,13,16,.88);border-radius:14px;text-shadow:0 1px 4px rgba(0,0,0,.9)}
.chip{display:inline-flex;align-items:center;gap:14px;background:rgba(11,13,16,.9);border:2px solid var(--cyan);border-left-width:8px;border-radius:10px;padding:16px 26px;font-family:'JetBrains Mono',monospace;font-size:31px;font-weight:700;letter-spacing:.02em;color:var(--fg);max-width:1260px;line-height:1.25}
.chip.signal{border-color:var(--signal)} .chip.ok{border-color:var(--ok)} .chip.copper{border-color:var(--copper)} .chip.rook{border-color:var(--rook)}
.chip small{font-size:22px;font-weight:500;color:var(--fg2);letter-spacing:.04em}
.lt{display:block;padding:10px 0 10px 30px;border-left:8px solid var(--rook);background:linear-gradient(90deg,rgba(11,13,16,.92),rgba(11,13,16,.0))}
.lt .n{font-family:'Instrument Serif',serif;font-size:86px;line-height:1;color:var(--fg)}
.lt .r{font-family:'JetBrains Mono',monospace;font-size:26px;letter-spacing:.14em;color:var(--rook);margin-top:8px;padding-right:200px}
.bar{width:1920px;height:60px;background:rgba(11,13,16,.94);border-bottom:2px solid var(--copper);display:flex;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-size:24px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg)}
.bar b{color:var(--copper);margin-right:14px}
.asof{font-family:'JetBrains Mono',monospace;font-size:21px;letter-spacing:.08em;color:rgba(237,232,220,.85);background:rgba(11,13,16,.72);border-radius:8px;padding:6px 14px}
.title{width:1920px;padding-left:150px}
.title .k{font-family:'JetBrains Mono',monospace;font-size:26px;letter-spacing:.22em;color:var(--fg2);text-transform:uppercase;margin-bottom:18px}
.title .a{font-family:'Instrument Serif',serif;font-size:190px;line-height:.92;color:var(--fg)}
.title .b{font-family:'Instrument Serif',serif;font-style:italic;font-size:230px;line-height:.9;color:var(--cyan)}
.title .c{font-family:'JetBrains Mono',monospace;font-size:28px;letter-spacing:.12em;color:var(--fg2);margin-top:26px;text-transform:uppercase}
.end{width:1920px;padding-left:150px}
.end .u{font-family:'Instrument Serif',serif;font-size:170px;line-height:.95}
.end .u i{color:var(--cyan)}
.end .t{font-family:'Instrument Serif',serif;font-style:italic;font-size:64px;color:var(--rook);margin-top:22px}
.end .s{font-family:'JetBrains Mono',monospace;font-size:24px;letter-spacing:.06em;color:var(--fg2);margin-top:34px;line-height:1.6;max-width:1000px}
`;

(async () => {
  const [specPath, outDir] = process.argv.slice(2);
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch();
  const page = await (await b.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })).newPage();
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="${FONTS}"><style>${CSS}</style></head><body><div id="x" style="display:inline-block"></div></body></html>`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  const sizes = {};
  for (const it of spec) {
    await page.evaluate(([html, width]) => { const x = document.getElementById('x'); x.style.width = width ? width + 'px' : ''; x.innerHTML = html; }, [it.html, it.width || 0]);
    await page.evaluate(() => document.fonts.ready);
    const el = await page.$('#x');
    const box = await el.boundingBox();
    await el.screenshot({ path: path.join(outDir, it.id + '.png'), omitBackground: true });
    sizes[it.id] = [Math.round(box.width), Math.round(box.height)];
  }
  fs.writeFileSync(path.join(outDir, 'sizes.json'), JSON.stringify(sizes));
  await b.close();
  console.log('rendered', spec.length, 'overlays');
})();
