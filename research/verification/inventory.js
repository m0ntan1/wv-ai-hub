const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('http://localhost:8765/', {waitUntil:'networkidle'});
  const inv = await p.evaluate(() => {
    const out = [];
    const ext = el => [...el.querySelectorAll('a[href^="http"]')].map(a=>a.href);
    document.querySelectorAll('.city-section').forEach(sec => {
      const city = sec.querySelector('.city-name').textContent;
      sec.querySelectorAll('.story-item').forEach(it => out.push({sec:'hub:'+city, title: it.querySelector('strong').textContent, text: it.textContent.trim(), urls: ext(it)}));
    });
    document.querySelectorAll('.future-hub-card').forEach(c => {
      const city = c.querySelector('.future-hub-name').textContent;
      c.querySelectorAll('.future-hub-story').forEach(it => out.push({sec:'hub:'+city, title: it.querySelector('strong').textContent, text: it.textContent.trim(), urls: ext(it)}));
    });
    document.querySelectorAll('.docket-item').forEach(it => out.push({sec:'docket', title: it.querySelector('.docket-name').textContent, text: it.querySelector('p').textContent, urls: ext(it)}));
    document.querySelectorAll('#people li').forEach(it => out.push({sec:'people', title: it.textContent.trim().slice(0,90), urls: ext(it)}));
    PROJECTS.forEach(pr => out.push({sec:'project', title: pr.name, urls: pr.sources.map(s=>s[1])}));
    EVENTS.forEach(e => out.push({sec:'event', title: e.title, urls: (e.sources||[]).map(s=>s[1])}));
    STANDING.forEach(s => out.push({sec:'standing', title: s.body, urls: [s.url]}));
    return out;
  });
  fs.writeFileSync(process.env.SP+'/inventory.json', JSON.stringify(inv, null, 1));
  const urls = [...new Set(inv.flatMap(i=>i.urls))];
  fs.writeFileSync(process.env.SP+'/urls.txt', urls.join('\n'));
  const bySec = {}; inv.forEach(i=>{ bySec[i.sec.split(':')[0]] = (bySec[i.sec.split(':')[0]]||0)+1; });
  console.log('items', inv.length, bySec, 'unique urls', urls.length, 'items with no source', inv.filter(i=>!i.urls.length).map(i=>i.sec+' | '+i.title));
  await b.close();
})();
