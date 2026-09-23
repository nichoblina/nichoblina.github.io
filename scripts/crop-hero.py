#!/usr/bin/env python3
# Light crop knobs live in CSS (.hero-photo--light). This script only rebuilds banner.jpeg.
# Dark crop knobs live in CSS (.hero-photo--dark) — edit background-size / background-position there.
from pathlib import Path
from PIL import Image, ImageFilter

# --- crop knobs (source is 864x1152) ---
CROP_LEFT = 240          # raise to cut more empty space on the left of the photo
CROP_TOP = 20            # raise to cut more above the hair
CROP_BOTTOM = 0.58       # fraction of source height to keep. 0.50 = upper chest, 0.58 = just below chest, 0.70 = mid-torso
MARGIN_RIGHT = 0.03      # empty canvas on the right, as a fraction of banner width
SITE_BG = (239, 232, 242)
BANNER_SIZE = (2880, 1234)

SRC = Path(__file__).resolve().parent.parent / "_originals" / "hero-arms-portrait.png"
OUT = Path(__file__).resolve().parent.parent


def main():
    src = Image.open(SRC).convert("RGBA")
    w, h = src.size
    crop = src.crop((CROP_LEFT, CROP_TOP, w, int(h * CROP_BOTTOM)))
    px = crop.load()
    cw, ch = crop.size
    R, G, B = SITE_BG
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = px[x, y]
            if min(r, g, b) > 195 and r > 205 and g > 205:
                lum = (r + g + b) / 3.0
                t = min(1.0, max(0.0, (lum - 200) / 55.0)) ** 0.35
                px[x, y] = (
                    int(r * (1 - t) + R * t),
                    int(g * (1 - t) + G * t),
                    int(b * (1 - t) + B * t),
                    255,
                )

    W, H = BANNER_SIZE
    canvas = Image.new("RGB", (W, H), SITE_BG)
    target_h = int(H * 0.98)
    scale = target_h / crop.height
    nw, nh = int(crop.width * scale), target_h
    photo = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    x = W - nw - int(W * MARGIN_RIGHT)
    y = H - nh + int(H * 0.02)
    canvas.paste(photo.convert("RGB"), (x, y))
    canvas.save(OUT / "banner.jpeg", "JPEG", quality=92, optimize=True, progressive=True, subsampling=0)
    print("wrote", OUT / "banner.jpeg", "crop", crop.size, "placed", (nw, nh), "at", (x, y))


if __name__ == "__main__":
    main()
