#!/usr/bin/env python3
"""Generate README header banner (WV outline + title) and MØNTAN1 badge."""

import re
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = Path("/Users/m0ntan1/github/WV-AI-HUB-INDEX/.claude/worktrees/wonderful-stonebraker-8196a5")
FONTS = Path(__file__).parent / "fonts"
ASSETS = REPO / "assets"
ASSETS.mkdir(exist_ok=True)

# --- Brand
BG = (5, 10, 18, 255)
GRID = (0, 212, 255, 18)
CYAN = (0, 212, 255)
CYAN_SOFT = (56, 189, 248)
WHITE = (255, 255, 255)
TEXT_DIM = (180, 195, 220)
RED_SLASH = (220, 38, 38)

# Extract WV polygon
html = (REPO / "index.html").read_text()
m = re.search(r"const WV = \[(.*?)\];", html, re.S)
pairs = re.findall(r"\[(-?\d+\.\d+),(-?\d+\.\d+)\]", m.group(1))
WV_COORDS = [(float(a), float(b)) for a, b in pairs]

# ============================================================
# 1. README HEADER BANNER (1200x340)
# ============================================================
W, H = 1200, 340
img = Image.new("RGBA", (W, H), BG)

# Grid
grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(grid)
for x in range(0, W, 80):
    gdraw.line([(x, 0), (x, H)], fill=GRID, width=1)
for y in range(0, H, 80):
    gdraw.line([(0, y), (W, y)], fill=GRID, width=1)
img = Image.alpha_composite(img, grid)

# Project WV polygon onto right side of banner
lngs = [c[0] for c in WV_COORDS]
lats = [c[1] for c in WV_COORDS]
MIN_LNG, MAX_LNG = min(lngs), max(lngs)
MIN_LAT, MAX_LAT = min(lats), max(lats)
mean_lat = (MIN_LAT + MAX_LAT) / 2
lng_scale = math.cos(math.radians(mean_lat))

# Map area (right portion)
MAP_X0, MAP_X1 = 720, 1160
MAP_Y0, MAP_Y1 = 30, 310
box_w = MAP_X1 - MAP_X0
box_h = MAP_Y1 - MAP_Y0
scale = min(box_w / ((MAX_LNG - MIN_LNG) * lng_scale), box_h / (MAX_LAT - MIN_LAT))
map_w = (MAX_LNG - MIN_LNG) * lng_scale * scale
map_h = (MAX_LAT - MIN_LAT) * scale
off_x = MAP_X0 + (box_w - map_w) / 2
off_y = MAP_Y0 + (box_h - map_h) / 2

def project(lng, lat):
    return (off_x + (lng - MIN_LNG) * lng_scale * scale,
            off_y + (MAX_LAT - lat) * scale)

wv_pts = [project(lng, lat) for lng, lat in WV_COORDS]

# Glow outline
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
gdraw.polygon(wv_pts, fill=(0, 212, 255, 14))
gdraw.line(wv_pts + [wv_pts[0]], fill=(0, 212, 255, 130), width=4)
glow_blurred = glow.filter(ImageFilter.GaussianBlur(radius=6))
img = Image.alpha_composite(img, glow_blurred)
draw = ImageDraw.Draw(img)
draw.line(wv_pts + [wv_pts[0]], fill=(0, 212, 255, 220), width=2)

# Hub dots (5 major + 7 emerging, just visual)
HUBS = [
    (-79.9559, 39.6295), (-80.1426, 39.4851), (-81.6326, 38.3498),
    (-82.4452, 38.4192), (-77.9639, 39.4562),
]
EMERGING = [
    (-81.5612, 39.2667), (-80.7209, 40.0640), (-80.5895, 40.4187),
    (-81.0976, 37.3667), (-81.1879, 37.7782), (-80.3445, 39.2806),
    (-79.4920, 39.0473),
]
nonlocal_img = img
for lng, lat in HUBS:
    x, y = project(lng, lat)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(layer)
    ldraw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(0, 212, 255, 110))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=8))
    nonlocal_img.alpha_composite(layer)
    d = ImageDraw.Draw(nonlocal_img)
    d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(220, 245, 255, 255))
for lng, lat in EMERGING:
    x, y = project(lng, lat)
    d = ImageDraw.Draw(nonlocal_img)
    d.ellipse((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(0, 212, 255, 200))
img = nonlocal_img
draw = ImageDraw.Draw(img)

# Typography (left side)
serif = ImageFont.truetype(str(FONTS / "InstrumentSerif-Regular.ttf"), 76)
serif_it = ImageFont.truetype(str(FONTS / "InstrumentSerif-Italic.ttf"), 76)
mono_tag = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 14)
mono_url = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 16)
sans = ImageFont.truetype(str(FONTS / "DMSans-Regular.ttf"), 18)

# Tag
draw.text((60, 50), "WV  AI  INNOVATION  INDEX", font=mono_tag, fill=(0, 212, 255, 200))
draw.line([(60, 75), (200, 75)], fill=(0, 212, 255, 100), width=1)

# Title
draw.text((60, 110), "Mountain State", font=serif, fill=WHITE)
# Italic "Frontier" with subtle glow
ai_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
agd = ImageDraw.Draw(ai_glow)
agd.text((60, 195), "AI Frontier.", font=serif_it, fill=(0, 212, 255, 200))
ai_glow_b = ai_glow.filter(ImageFilter.GaussianBlur(radius=10))
img = Image.alpha_composite(img, ai_glow_b)
draw = ImageDraw.Draw(img)
draw.text((60, 195), "AI Frontier.", font=serif_it, fill=(56, 189, 248, 255))

# URL
draw.text((60, 295), "wvaihub.com", font=mono_url, fill=(0, 212, 255, 200))

img.convert("RGB").save(ASSETS / "readme-banner.png", "PNG", optimize=True)
print(f"Wrote {ASSETS / 'readme-banner.png'}")

# ============================================================
# 2. MØNTAN1.com BADGE (480x110, transparent bg)
# ============================================================
BW, BH = 480, 110
badge = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
bdraw = ImageDraw.Draw(badge)

font = ImageFont.truetype(str(FONTS / "InstrumentSerif-Regular.ttf"), 72)
text = "M0NTAN1.com"
TEXT_COLOR = (8, 18, 35, 255)  # dark, readable on white README

# Measure full text
bbox = bdraw.textbbox((0, 0), text, font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]
text_top = bbox[1]
x0 = (BW - text_w) // 2
y0 = (BH - text_h) // 2 - text_top

bdraw.text((x0, y0), text, font=font, fill=TEXT_COLOR)

# Slash through "0" - it's the 2nd char (index 1)
w_M = font.getlength("M")
w_0 = font.getlength("0")
slash_x_start = x0 + w_M + w_0 * 0.08
slash_x_end   = x0 + w_M + w_0 * 0.92
# Slash goes from lower-left to upper-right (Scandinavian Ø style)
glyph_top = y0 + text_top + text_h * 0.10
glyph_bot = y0 + text_top + text_h * 0.85
bdraw.line(
    [(slash_x_start, glyph_bot), (slash_x_end, glyph_top)],
    fill=RED_SLASH + (255,), width=5,
)

badge.save(ASSETS / "montani-badge.png", "PNG", optimize=True)
print(f"Wrote {ASSETS / 'montani-badge.png'}")

# Also produce a dark-bg version for visibility on dark themes (GitHub dark mode)
badge_dark = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
bdraw2 = ImageDraw.Draw(badge_dark)
bdraw2.text((x0, y0), text, font=font, fill=(232, 237, 245, 255))  # light text
bdraw2.line(
    [(slash_x_start, glyph_bot), (slash_x_end, glyph_top)],
    fill=RED_SLASH + (255,), width=5,
)
badge_dark.save(ASSETS / "montani-badge-dark.png", "PNG", optimize=True)
print(f"Wrote {ASSETS / 'montani-badge-dark.png'}")
