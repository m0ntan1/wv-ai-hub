// Renders the YouTube thumbnail (1280x720 JPEG) in the site's own type and colors.
//   node video/thumbnail.js <footage-dir> <out.jpg>
// Uses footage/map_hero.png (made by build.py) as the background.
const { chromium } = require('playwright');
const path = require('path');
const [footage, out] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch();
  const page = await (await b.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 })).newPage();
  const map = 'data:image/png;base64,' + require('fs').readFileSync(path.resolve(footage, 'map_hero.png')).toString('base64');
  await page.setContent(`<!doctype html><meta charset="utf-8">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@500;700&display=swap">
  <style>
   *{margin:0;box-sizing:border-box} body{width:1280px;height:720px;background:#0B0D10;position:relative;overflow:hidden;color:#EDE8DC}
   .map{position:absolute;right:-120px;top:-40px;width:1100px;height:620px;background:url('${map}') center/cover;opacity:.95}
   .fade{position:absolute;inset:0;background:linear-gradient(90deg,#0B0D10 8%,rgba(11,13,16,.78) 42%,rgba(11,13,16,0) 72%)}
   .t{position:absolute;left:64px;top:96px}
   .k{font-family:'JetBrains Mono';font-weight:700;font-size:26px;letter-spacing:.2em;color:#C9CED6;text-transform:uppercase}
   .h1{font-family:'Instrument Serif';font-size:196px;line-height:.86;margin-top:22px}
   .h2{font-family:'Instrument Serif';font-style:italic;font-size:226px;line-height:.82;color:#00D4FF}
   .tag{position:absolute;left:64px;bottom:52px;display:flex;gap:16px;align-items:center;font-family:'JetBrains Mono';font-weight:700;font-size:26px;letter-spacing:.08em}
   .tag span{border:3px solid #C9CED6;color:#C9CED6;padding:8px 16px;border-radius:8px}
   .tag em{font-style:normal;color:#A9A497;font-weight:500}
   .wave{position:absolute;left:0;right:0;bottom:0;height:10px;background:linear-gradient(90deg,#C9CED6,#00D4FF)}
  </style>
  <div class="map"></div><div class="fade"></div>
  <div class="t"><div class="k">Rook explains</div><div class="h1">Follow the</div><div class="h2">money</div></div>
  <div class="tag"><span>ROOK · AI</span><em>West Virginia's AI Watch</em></div><div class="wave"></div>`, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out, type: 'jpeg', quality: 92 });
  await b.close();
  console.log('wrote', out);
})();
