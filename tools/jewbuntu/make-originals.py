#!/usr/bin/env python3
"""Generate original Mac-style squircle app icons to replace upstream icons that copy
Apple's own designs. usage: make-originals.py ADWAITA_SYMBOLIC_ROOT OUT_DIR"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Superellipse-like rounded square on GNOME's 128px grid (112px body, like macOS proportions).
SQUIRCLE = "M64 8C98 8 120 8 120 30v68c0 22-22 22-56 22S8 120 8 98V30C8 8 30 8 64 8z"


def find_glyph(root, name):
    for dirpath, _, files in os.walk(root):
        if name + ".svg" in files:
            return os.path.join(dirpath, name + ".svg")
    raise SystemExit(f"glyph not found: {name}")


def glyph_body(path):
    svg = open(path, encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', svg)
    w, h = (float(x) for x in vb.group(1).split()[2:4]) if vb else (16.0, 16.0)
    body = re.sub(r"(?s)^.*?<svg[^>]*>|</svg>\s*$", "", svg)
    body = re.sub(r'\s(fill|style|class|opacity|fill-opacity)="[^"]*"', "", body)
    body = re.sub(r"(?s)<defs>.*?</defs>|<title>.*?</title>", "", body)
    return body, w, h


# Simple original glyphs (16x16 grid, white strokes/fills) where no Adwaita symbol fits well.
CUSTOM = {
    "bag": ('<path d="M3.5 5.5h9l-.7 8.2a1 1 0 0 1-1 .8H5.2a1 1 0 0 1-1-.8z"/>'
            '<path d="M5.6 6.5V4.8a2.4 2.4 0 0 1 4.8 0v1.7" fill="none" stroke="#fff" stroke-width="1.3" stroke-linecap="round"/>'),
    "globe": ('<g fill="none" stroke="#fff" stroke-width="1.1"><circle cx="8" cy="8" r="6.3"/>'
              '<ellipse cx="8" cy="8" rx="2.7" ry="6.3"/><path d="M1.9 6h12.2M1.9 10h12.2M8 1.7v12.6"/></g>'),
}


def make(name, spec, root):
    if spec["glyph"].startswith("custom:"):
        body, w, h = CUSTOM[spec["glyph"].split(":", 1)[1]], 16.0, 16.0
    else:
        body, w, h = glyph_body(find_glyph(root, spec["glyph"]))
    size = 60.0
    s = size / max(w, h)
    tx = 64 - w * s / 2
    ty = 64 - h * s / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <!-- Jewbuntu original ({name}): gradient squircle + glyph "{spec['glyph']}" (custom: original; otherwise Adwaita symbolic, GNOME, CC BY-SA 3.0). -->
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{spec['top']}"/><stop offset="1" stop-color="{spec['bottom']}"/></linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity=".25"/></filter>
  </defs>
  <path d="{SQUIRCLE}" fill="url(#bg)" filter="url(#sh)"/>
  <path d="{SQUIRCLE}" fill="url(#sheen)"/>
  <g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})" fill="#ffffff">{body}</g>
</svg>
'''


def main():
    root, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(os.path.join(HERE, "originals.json")))["icons"]
    os.makedirs(out, exist_ok=True)
    rendered = {name: make(name, item, root) for name, item in spec.items()}  # all glyphs checked before writing
    for name, svg in rendered.items():
        with open(os.path.join(out, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"wrote {len(spec)} icons to {out}")


if __name__ == "__main__":
    main()
