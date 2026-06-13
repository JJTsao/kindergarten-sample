#!/usr/bin/env python3
"""Crop placeholder photos from Sample2.png into site2/assets/img/.
Mockup is the only photo source here (env can't fetch/generate). Semantic
names + fixed display aspect so real photos drop in later without HTML/CSS edits.
"""
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "Sample2.png"
OUT = Path(__file__).resolve().parents[1] / "assets" / "img"

REGIONS = {
    "hero": (10, 92, 520, 312),
    "mission-happy":   (150, 552, 305, 658),
    "mission-quality": (448, 552, 600, 658),
    "mission-care":    (650, 552, 800, 658),
    "campus-safe":    (58, 1180, 192, 1338),
    "campus-teacher": (252, 1180, 388, 1338),
    "campus-course":  (446, 1180, 582, 1338),
    "campus-meal":    (642, 1180, 784, 1338),
    "gallery-outdoor":  (62, 1492, 232, 1628),
    "gallery-theme":    (252, 1492, 420, 1628),
    "gallery-talent":   (442, 1492, 610, 1628),
    "gallery-festival": (622, 1492, 792, 1628),
}
UP = 2

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(SRC).convert("RGB")
    for name, box in REGIONS.items():
        c = img.crop(box); w, h = c.size
        c = c.resize((w*UP, h*UP), Image.LANCZOS)
        c = ImageEnhance.Sharpness(c).enhance(1.3)
        c.save(OUT / f"{name}.jpg", quality=90)
        print(name, c.size)

if __name__ == "__main__":
    main()
