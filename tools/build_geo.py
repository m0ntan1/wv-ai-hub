"""Build data/geo.json: West Virginia's 55 county outlines plus the state border.

Source: Plotly's US counties GeoJSON (geojson-counties-fips.json), which is
derived from the U.S. Census Bureau's cartographic boundary files.
https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json

Usage: python3 -I tools/build_geo.py <counties.json> data/geo.json

Coordinates are rounded to 3 decimals (about 100 m), which is plenty for a
statewide map. The state border is derived from the counties themselves
(edges that belong to only one county), so the outline and the county lines
always line up.
"""
import json, sys
from collections import Counter

src, out = sys.argv[1], sys.argv[2]
fc = json.load(open(src))
WV = '54'
counties = []
for f in fc['features']:
    if f['properties'].get('STATE') != WV:
        continue
    g = f['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    rings = []
    for poly in polys:
        ring = [[round(x, 3), round(y, 3)] for x, y in poly[0]]
        dedup = [ring[0]] + [p for i, p in enumerate(ring[1:], 1) if p != ring[i - 1]]
        rings.append(dedup)
    counties.append({'name': f['properties']['NAME'], 'fips': f['id'], 'rings': rings})
counties.sort(key=lambda c: c['name'])
assert len(counties) == 55, len(counties)

# Border = edges used by exactly one county ring.
seg = Counter()
for c in counties:
    for r in c['rings']:
        for a, b in zip(r, r[1:]):
            seg[tuple(sorted((tuple(a), tuple(b))))] += 1
border = [[list(a), list(b)] for (a, b), n in seg.items() if n == 1]

# Label point per county: the vertex average of its largest ring (good enough for compact WV counties).
for c in counties:
    r = max(c['rings'], key=len)
    c['label'] = [round(sum(p[0] for p in r) / len(r), 3), round(sum(p[1] for p in r) / len(r), 3)]

json.dump({'source': 'U.S. Census Bureau cartographic boundaries via plotly/datasets geojson-counties-fips.json',
           'counties': counties, 'border': border}, open(out, 'w'), separators=(',', ':'))
print(len(counties), 'counties,', len(border), 'border segments')
