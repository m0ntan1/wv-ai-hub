#!/usr/bin/env python3
"""Generate the WV AI Hub Index OG image using the real WV polygon from index.html."""

import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = Path("/Users/m0ntan1/github/WV-AI-HUB-INDEX/.claude/worktrees/wonderful-stonebraker-8196a5")
FONTS = Path(__file__).parent / "fonts"

# --- Brand
W, H = 1200, 630
BG = (5, 10, 18, 255)              # #050a12
GRID = (0, 212, 255, 18)           # very faint cyan grid
CYAN = (0, 212, 255)               # accent
CYAN_SOFT = (56, 189, 248)
WHITE = (255, 255, 255)
TEXT_DIM = (180, 195, 220)
TEXT_FADE = (130, 145, 175)

# --- Extract WV polygon from index.html
html = (REPO / "index.html").read_text()
m = re.search(r"const WV = \[(.*?)\];", html, re.S)
if not m:
    sys.exit("Could not find WV polygon in index.html")
pairs = re.findall(r"\[(-?\d+\.\d+),(-?\d+\.\d+)\]", m.group(1))
WV_COORDS = [(float(a), float(b)) for a, b in pairs]
print(f"Loaded {len(WV_COORDS)} WV polygon points")

# --- Major hubs (lng, lat, name, is_capital)
HUBS = [
    (-79.9559, 39.6295, "Morgantown", False),
    (-80.1426, 39.4851, "Fairmont", False),
    (-81.6326, 38.3498, "Charleston", True),
    (-82.4452, 38.4192, "Huntington", False),
    (-77.9639, 39.4562, "Berkeley Co.", False),
]
EMERGING = [
    (-81.5612, 39.2667, "Parkersburg"),
    (-80.7209, 40.0640, "Wheeling"),
    (-80.5895, 40.4187, "Weirton"),
    (-81.0976, 37.3667, "Princeton"),
    (-81.1879, 37.7782, "Beckley"),
    (-80.3445, 39.2806, "Clarksburg"),
    (-79.4920, 39.0473, "Tucker County"),
]

# --- Map projection
lngs = [c[0] for c in WV_COORDS]
lats = [c[1] for c in WV_COORDS]
MIN_LNG, MAX_LNG = min(lngs), max(lngs)
MIN_LAT, MAX_LAT = min(lats), max(lats)

# Map area (right side of canvas)
MAP_X0, MAP_X1 = 600, 1150
MAP_Y0, MAP_Y1 = 60, 580

# Preserve aspect ratio
lng_range = MAX_LNG - MIN_LNG
lat_range = MAX_LAT - MIN_LAT
# Latitude needs compression by cos(mean_lat) for proper proportions
import math
mean_lat = (MIN_LAT + MAX_LAT) / 2
lng_scale = math.cos(math.radians(mean_lat))
effective_lng_range = lng_range * lng_scale

box_w = MAP_X1 - MAP_X0
box_h = MAP_Y1 - MAP_Y0
# Fit polygon into box maintaining aspect
scale = min(box_w / effective_lng_range, box_h / lat_range)

# Center the map in the box
map_w = effective_lng_range * scale
map_h = lat_range * scale
off_x = MAP_X0 + (box_w - map_w) / 2
off_y = MAP_Y0 + (box_h - map_h) / 2

def project(lng, lat):
    x = off_x + (lng - MIN_LNG) * lng_scale * scale
    y = off_y + (MAX_LAT - lat) * scale
    return (x, y)

# --- Canvas
img = Image.new("RGBA", (W, H), BG)

# --- Grid
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(grid)
for x in range(0, W, 80):
    gdraw.line([(x, 0), (x, H)], fill=GRID, width=1)
for y in range(0, H, 80):
    gdraw.line([(0, y), (W, y)], fill=GRID, width=1)
img = Image.alpha_composite(img, grid)

# --- WV outline glow
wv_pts = [project(lng, lat) for lng, lat in WV_COORDS]

glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
gdraw.polygon(wv_pts, fill=(0, 212, 255, 14))   # subtle fill
gdraw.line(wv_pts + [wv_pts[0]], fill=(0, 212, 255, 130), width=4)
glow_blurred = glow.filter(ImageFilter.GaussianBlur(radius=6))
img = Image.alpha_composite(img, glow_blurred)

# --- Sharp outline
draw = ImageDraw.Draw(img)
draw.line(wv_pts + [wv_pts[0]], fill=(0, 212, 255, 220), width=2)

# --- Connection lines between major hubs (matches site's "hub streams")
major_proj = [project(h[0], h[1]) for h in HUBS]
stream_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(stream_layer)
for i in range(len(major_proj)):
    for j in range(i + 1, len(major_proj)):
        sdraw.line([major_proj[i], major_proj[j]], fill=(0, 212, 255, 50), width=1)
stream_blurred = stream_layer.filter(ImageFilter.GaussianBlur(radius=1.2))
img = Image.alpha_composite(img, stream_blurred)
draw = ImageDraw.Draw(img)

# --- Hub dots
def draw_dot(x, y, r_glow, r_dot, alpha_glow=120):
    # outer glow rings
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    ldraw.ellipse((x - r_glow, y - r_glow, x + r_glow, y + r_glow),
                  fill=(0, 212, 255, alpha_glow))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=r_glow / 2))
    nonlocal_img.alpha_composite(layer)
    d = ImageDraw.Draw(nonlocal_img)
    d.ellipse((x - r_dot, y - r_dot, x + r_dot, y + r_dot),
              fill=(0, 212, 255, 255))
    d.ellipse((x - r_dot + 1, y - r_dot + 1, x + r_dot - 1, y + r_dot - 1),
              fill=(220, 245, 255, 255))

nonlocal_img = img  # used inside draw_dot

# Major hubs — larger, with glow
for lng, lat, name, capital in HUBS:
    x, y = project(lng, lat)
    draw_dot(x, y, r_glow=20, r_dot=6, alpha_glow=110)

# Emerging hubs — smaller, dimmer
for lng, lat, name in EMERGING:
    x, y = project(lng, lat)
    draw_dot(x, y, r_glow=10, r_dot=3, alpha_glow=70)

img = nonlocal_img
draw = ImageDraw.Draw(img)

# --- Typography
serif_big = ImageFont.truetype(str(FONTS / "InstrumentSerif-Regular.ttf"), 92)
serif_italic = ImageFont.truetype(str(FONTS / "InstrumentSerif-Italic.ttf"), 92)
mono_sub = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 18)
mono_url = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 16)
sans_body = ImageFont.truetype(str(FONTS / "DMSans-Regular.ttf"), 22)
sans_med = ImageFont.truetype(str(FONTS / "DMSans-Medium.ttf"), 22)
sans_num = ImageFont.truetype(str(FONTS / "DMSans-Medium.ttf"), 56)
mono_tag = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 13)

# Top-left tag
draw.text((72, 70), "WV  AI  INDEX  /  2026", font=mono_tag,
          fill=(0, 212, 255, 180))
# Faint horizontal line under tag
draw.line([(72, 96), (200, 96)], fill=(0, 212, 255, 100), width=1)

# Title block
draw.text((72, 180), "West Virginia's", font=serif_big, fill=WHITE)
# Italic colored second line with glow
ai_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
agdraw = ImageDraw.Draw(ai_glow)
agdraw.text((72, 280), "AI Frontier", font=serif_italic, fill=(0, 212, 255, 200))
ai_glow_blurred = ai_glow.filter(ImageFilter.GaussianBlur(radius=12))
img = Image.alpha_composite(img, ai_glow_blurred)
draw = ImageDraw.Draw(img)
draw.text((72, 280), "AI Frontier", font=serif_italic, fill=(56, 189, 248, 255))

# Subtitle
draw.text((76, 400), "MAPPING  INNOVATION  ACROSS  THE  MOUNTAIN  STATE",
          font=mono_sub, fill=TEXT_DIM)

# Stats row
draw.text((72, 460), "12", font=sans_num, fill=CYAN)
bbox = draw.textbbox((0, 0), "12", font=sans_num)
w11 = bbox[2] - bbox[0]
draw.text((72 + w11 + 14, 488), "Innovation Hubs", font=sans_body, fill=TEXT_DIM)

stat2_x = 72 + w11 + 14 + 200
draw.text((stat2_x, 460), "53", font=sans_num, fill=CYAN)
bbox2 = draw.textbbox((0, 0), "53", font=sans_num)
w40 = bbox2[2] - bbox2[0]
draw.text((stat2_x + w40 + 14, 488), "Stories Tracked", font=sans_body, fill=TEXT_DIM)

# Bottom URL
draw.line([(72, 555), (130, 555)], fill=(0, 212, 255, 200), width=2)
draw.text((72, 568), "wvaihub.com", font=mono_url, fill=(0, 212, 255, 220))

# Bottom-right small marker
mono_corner = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 11)
draw.text((W - 320, 600), "MONTANI · SEMPER · LIBERI", font=mono_corner,
          fill=(180, 195, 220, 110))

# --- Save
out = REPO / "assets/og-image.png"
img.convert("RGB").save(out, "PNG", optimize=True)
print(f"Wrote {out} ({out.stat().st_size} bytes)")
