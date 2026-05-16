#!/usr/bin/env python3
"""Generate favicon + apple-touch-icon + a small social card variant."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parent.parent.parent

BG = (5, 10, 18, 255)
CYAN = (0, 212, 255)

def render_icon(size, dot_radius_frac=0.32):
    img = Image.new("RGBA", (size, size), BG)
    # outer faint glow
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = cy = size / 2
    rg = size * 0.46
    gd.ellipse((cx - rg, cy - rg, cx + rg, cy + rg), fill=(0, 212, 255, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=size * 0.08))
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)
    r = size * dot_radius_frac
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CYAN + (255,))
    # inner highlight
    rh = r * 0.55
    d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), fill=(220, 245, 255, 255))
    return img

# Browser tab favicons
for s in (16, 32, 48):
    icon = render_icon(s)
    icon.save(REPO / "assets" / f"favicon-{s}x{s}.png", "PNG")

# Apple touch icon (no transparency)
apple = render_icon(180)
apple.convert("RGB").save(REPO / "assets/apple-touch-icon.png", "PNG")

# Android home screen
for s in (192, 512):
    icon = render_icon(s)
    icon.convert("RGB").save(REPO / "assets" / f"icon-{s}.png", "PNG")

# SVG favicon (vector, crisp at any size)
svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <filter id="g" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.2"/>
    </filter>
    <radialGradient id="dot" cx="0.45" cy="0.4">
      <stop offset="0%" stop-color="#e0f5ff"/>
      <stop offset="55%" stop-color="#00d4ff"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </radialGradient>
  </defs>
  <rect width="32" height="32" fill="#050a12"/>
  <circle cx="16" cy="16" r="14" fill="#00d4ff" opacity="0.35" filter="url(#g)"/>
  <circle cx="16" cy="16" r="9" fill="url(#dot)"/>
</svg>
'''
(REPO / "assets/favicon.svg").write_text(svg)

print("Generated favicon-{16,32,48}.png, apple-touch-icon.png, icon-{192,512}.png, favicon.svg")
