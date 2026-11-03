// Evaluate the old site's inline data arrays in Node and dump them as JSON.
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const out = process.argv[3];
const grab = (startMarker, endMarker) => {
  const a = html.indexOf(startMarker), b = html.indexOf(endMarker, a);
  if (a < 0 || b < 0) throw new Error('marker not found: ' + startMarker);
  return html.slice(a, b);
};
const geo = grab('const WV = [', '// PROJECTION UTILITIES');
const watch = grab('const STATUS = {', '// AI WATCH: RENDERING');
const cal = grab('const EVENTS = [', '// CALENDAR: RENDERING');
const code = `${geo}\n${watch}\n${cal}\nmodule.exports = { WV, HUBS, TOP10: typeof TOP10 !== 'undefined' ? TOP10 : null, EMERGING_HUBS, STATUS, PROJECTS, LINES, EVENTS, STANDING };`;
fs.writeFileSync(out + '/_old_data.js', code);
const d = require(out + '/_old_data.js');
fs.writeFileSync(out + '/old_data.json', JSON.stringify(d, null, 1));
console.log(Object.fromEntries(Object.entries(d).map(([k, v]) => [k, Array.isArray(v) ? v.length : typeof v])));
console.log('project keys', [...new Set(d.PROJECTS.flatMap(p => Object.keys(p)))].join(','));
console.log('event keys', [...new Set(d.EVENTS.flatMap(p => Object.keys(p)))].join(','));
console.log('standing keys', [...new Set(d.STANDING.flatMap(p => Object.keys(p)))].join(','));
console.log('line sample', JSON.stringify(d.LINES[0]).slice(0, 300));
console.log('hub sample', JSON.stringify(d.HUBS[0]), JSON.stringify(d.EMERGING_HUBS[0]));
