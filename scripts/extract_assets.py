#!/usr/bin/env python3
"""Crop photo assets from Sample1.png into assets/img/.

The mockup is the only available source for photographic content
(this environment cannot fetch stock photos). Crops are inset a few px
to avoid the baked-in rounded corners; CSS re-applies the radius.
Small crops are upscaled 2x with Lanczos + light sharpening, which
looks better than letting the browser upscale.
"""
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Sample1.png"
OUT = ROOT / "assets" / "img"

# name -> (left, top, right, bottom) in mockup coordinates (941x1672)
REGIONS = {
    "hero": (415, 66, 941, 345),
    "about": (400, 471, 889, 692),
    "class-toddler": (62, 758, 237, 837),
    "class-junior": (269, 758, 444, 837),
    "class-middle": (475, 758, 650, 837),
    "class-senior": (690, 758, 865, 837),
    "teacher-emily": (64, 988, 128, 1052),
    "teacher-lin": (274, 988, 338, 1052),
    "teacher-jason": (474, 988, 538, 1052),
    "teacher-chen": (683, 988, 747, 1052),
    "life-learning": (59, 1126, 211, 1214),
    "life-outdoor": (231, 1126, 383, 1214),
    "life-story": (405, 1126, 544, 1214),
    "life-steam": (568, 1126, 704, 1214),
    "life-music": (725, 1126, 871, 1214),
    "avatar-xiaoyu": (74, 1344, 112, 1382),
    "avatar-emma": (354, 1344, 392, 1382),
    "avatar-junjie": (620, 1344, 658, 1382),
}

UPSCALE = 2  # Lanczos upscale factor for all crops


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(SRC).convert("RGB")
    for name, box in REGIONS.items():
        crop = img.crop(box)
        w, h = crop.size
        crop = crop.resize((w * UPSCALE, h * UPSCALE), Image.LANCZOS)
        crop = ImageEnhance.Sharpness(crop).enhance(1.3)
        path = OUT / f"{name}.jpg"
        crop.save(path, quality=92)
        print(f"{path.name}: {crop.size[0]}x{crop.size[1]}")


if __name__ == "__main__":
    main()
