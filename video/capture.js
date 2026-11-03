// Captures footage of the live site for the Rook video: stills and frame sequences at 1920x1080.
// The page is laid out at 1280x720 and rendered at 1.5x, so type stays readable on a phone screen.
// The date is pinned with ?today=, so every countdown matches the narration.
//
//   node video/capture.js <out-dir> [only,names]
//
// Not captured on purpose: pages on sec.gov. The SEC blocks scripted browsers (it serves an "undeclared automated tool"
// page), so the filing is shown through the site's own pages, which link to it.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = process.argv[2];
const ONLY = process.argv[3] ? new Set(process.argv[3].split(',')) : null;
const SITE = process.env.SITE || 'https://wvaihub.com';
const TODAY = process.env.PIN_DATE || '2026-11-03';
const FPS = 20;
const SCROLL_FPS = 30;   // scroll sequences are shot at the video's frame rate so every video frame is a real frame (no blending)
const ease = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

const STILLS = [
  ['front', '#/'], ['projects', '#/projects'], ['monarch_top', '#/project/monarch'], ['summit_top', '#/project/summit'], ['docket', '#/docket'],
  ['calendar', '#/calendar'], ['people', '#/people'], ['people_nscale', '#/people?focus=nscale'], ['county', '#/county/mason'],
  ['news', '#/news'], ['receipts', '#/receipts'], ['money_top', '#/money'], ['nscale_top', '#/company/nscale'], ['anthropic_top', '#/company/anthropic'],
  ['desk', '#/desk'], ['desk_rook', '#/desk/rook'], ['desk_mercer', '#/desk/mercer'], ['rook_archive', '#/rook'], ['contact', '#/contact'],
];
// name, route, scroll distance (px), seconds
// The seconds match how long each shot is on screen in the cut (see out/timing.json), so playback is 1 source frame per video frame.
const SCROLLS = [['seq_monarch', '#/project/monarch', 760, 14], ['seq_docket', '#/docket', 1300, 9], ['seq_calendar', '#/calendar', 700, 8],
  ['seq_money', '#/money', 2600, 20], ['seq_nscale', '#/company/nscale', 1250, 34]];

// Optional: BLUR_PEOPLE=1 blurs the "People" rows on case files. Off by default: the video shows the site as published,
// and the site's own naming rule (sourced, from published reporting) is the editor's policy, not the video's.
async function redact(page) {
  await page.evaluate(() => {
    document.querySelectorAll('.facts > div').forEach(r => {
      const dt = r.querySelector('dt'), dd = r.querySelector('dd');
      if (dt && dd && /^people$/i.test(dt.textContent.trim())) dd.style.filter = 'blur(9px)';
    });
  });
}
async function open(page, hash) {
  try { await page.goto(`${SITE}/?today=${TODAY}${hash}`, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch (e) { await page.waitForLoadState('domcontentloaded'); }   // a preview's drawer can keep a connection open
  await page.waitForTimeout(900);
  // Netlify deploy previews add a "Collaborate on this Deploy Preview" bar in an iframe; it must not appear in the video.
  // The preview's CSP can block an injected stylesheet, so remove the bar from the DOM itself (and keep removing it).
  await page.addStyleTag({ content: 'iframe[src*="netlify" i]{display:none!important}' }).catch(() => {});
  await page.evaluate(() => {
    const kill = () => document.querySelectorAll('iframe[src*="netlify" i]').forEach(f => (f.closest('div') || f).remove());
    kill(); new MutationObserver(kill).observe(document.documentElement, { childList: true, subtree: true });
  });
  if (process.env.BLUR_PEOPLE === '1') await redact(page);
}
const want = n => !ONLY || ONLY.has(n);

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  await ctx.route(/app\.netlify\.com/, r => r.abort());   // the deploy-preview bar loads from here
  const page = await ctx.newPage();

  for (const [name, hash] of STILLS) {
    if (!want(name)) continue;
    await open(page, hash);
    await page.screenshot({ path: path.join(OUT, name + '.png') });
    console.log('still', name);
  }

  // The county's money section and a second Money shot further down.
  if (want('money_tranches')) {
    await open(page, '#/money');
    await page.evaluate(() => document.getElementById('tr-companies')?.scrollIntoView());
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(OUT, 'money_tranches.png') });
    console.log('still money_tranches');
  }
  if (want('anthropic_filing')) {
    await open(page, '#/company/anthropic');
    await page.evaluate(() => document.getElementById('s-facts')?.scrollIntoView());
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(OUT, 'anthropic_filing.png') });
    console.log('still anthropic_filing');
  }
  if (want('nscale_filing')) {
    await open(page, '#/company/nscale');
    await page.evaluate(() => document.getElementById('s-facts')?.scrollIntoView());
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(OUT, 'nscale_filing.png') });
    console.log('still nscale_filing');
  }

  // A header-free picture of the map as it stands today, for the cold open and the title card.
  if (want('map_hero')) {
    await open(page, '#/map');
    await page.waitForSelector('#bigMap svg');
    await page.waitForTimeout(800);
    await (await page.$('#bigMap svg')).screenshot({ path: path.join(OUT, 'map_hero_raw.png') });
    console.log('still map_hero_raw');
  }

  for (const [name, hash, dist, secs] of SCROLLS) {
    if (!want(name)) continue;
    await open(page, hash);
    const dir = path.join(OUT, name); fs.mkdirSync(dir, { recursive: true });
    const n = Math.round(secs * SCROLL_FPS);
    for (let i = 0; i < n; i++) {
      await page.evaluate(y => window.scrollTo(0, y), Math.round(dist * ease(i / (n - 1))));
      await page.waitForTimeout(30);
      await page.screenshot({ path: path.join(dir, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 92 });
    }
    console.log('sequence', name, n, 'frames');
  }

  // The map: sweep the time slider from the day HB 2014 became law to today. Only the map itself is shot; the
  // date and caption text are saved alongside so the video can set them in large type.
  if (want('seq_map')) {
    await open(page, '#/map');
    await page.waitForSelector('.scrub input[type=range]');
    const today = await page.$eval('.scrub input[type=range]', el => +el.value);
    const dir = path.join(OUT, 'seq_map'); fs.mkdirSync(dir, { recursive: true });
    const svg = await page.$('#bigMap svg');
    const secs = 18, n = secs * FPS, caps = [];
    for (let i = 0; i < n; i++) {
      const v = Math.round(today * ease(i / (n - 1)));
      await page.$eval('.scrub input[type=range]', (el, val) => { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); }, v);
      await page.waitForTimeout(40);
      await svg.screenshot({ path: path.join(dir, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 92 });
      caps.push(await page.$eval('.scrub-cap', el => ({ label: (el.querySelector('b') || {}).innerText || '', text: (el.querySelector('span') || {}).innerText || '' })));
    }
    fs.writeFileSync(path.join(dir, 'captions.json'), JSON.stringify(caps));
    console.log('sequence seq_map', n, 'frames (slider today =', today + ')');
  }

  // The capex chart's hover tooltip.
  if (want('seq_money_hover')) {
    await open(page, '#/money');
    await page.evaluate(() => document.querySelector('.sig-wide')?.scrollIntoView({ block: 'center' }));
    await page.waitForTimeout(500);
    const box = await (await page.$('.sig-wide .viz svg')).boundingBox();
    const dir = path.join(OUT, 'seq_money_hover'); fs.mkdirSync(dir, { recursive: true });
    const n = 3 * FPS;
    for (let i = 0; i < n; i++) {
      await page.mouse.move(box.x + box.width * (0.12 + 0.78 * ease(i / (n - 1))), box.y + box.height * 0.5);
      await page.waitForTimeout(30);
      await page.screenshot({ path: path.join(dir, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 92 });
    }
    console.log('sequence seq_money_hover', n, 'frames');
  }

  await b.close();
})();
