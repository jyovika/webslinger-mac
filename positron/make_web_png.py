"""Renders the RStudio corner web as web.png for Positron's "background" extension (it can't show SVG)."""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rstudio"))
from make_web import RINGS, SIZE, STRANDS, pt  # noqa: E402

SCALE = 2  # 2x for Retina screens
ALPHA = round(0.13 * 255)  # same faintness as the RStudio web
COLOR = (0xE3, 0x24, 0x2B, ALPHA)


def s(p):
    return p[0] * SCALE, p[1] * SCALE


img = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
width = round(1.2 * SCALE)
angles = [math.radians(2 + i * 86 / (STRANDS - 1)) for i in range(STRANDS)]
for a in angles:
    draw.line([s(pt(0, a)), s(pt(SIZE * 1.05, a))], fill=COLOR, width=width)
for k in range(1, RINGS + 1):
    r = SIZE * (k / RINGS) ** 1.15
    for i in range(STRANDS - 1):
        p0, p2 = pt(r, angles[i]), pt(r, angles[i + 1])
        p1 = pt(r * 0.86, (angles[i] + angles[i + 1]) / 2)
        curve = [tuple((1 - t) ** 2 * p0[j] + 2 * (1 - t) * t * p1[j] + t * t * p2[j] for j in (0, 1))
                 for t in (n / 24 for n in range(25))]
        draw.line([s(p) for p in curve], fill=COLOR, width=width)

out = Path(__file__).resolve().parent / "web.png"
img.save(out)
assert img.getbbox() is not None and img.getpixel((SIZE * SCALE - 1, 0))[3] > 0  # web drawn, anchored top-right
print(out)
