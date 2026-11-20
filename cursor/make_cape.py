"""Builds WebSlinger.cape: a dark web-pattern arrow and a spider link cursor for Mousecape."""
import io, math, plistlib
from PIL import Image, ImageDraw, ImageFilter

INK, NAVY = (12, 12, 16), (20, 30, 78)
CRIMSON, EMBER = (205, 18, 34, 255), (255, 60, 60, 255)
RIM = (205, 208, 216, 255)  # thin light rim so the dark cursor stays visible on dark windows
BLACK = (6, 6, 8, 255)
SS = 8  # supersample factor, drawn large then downscaled for smooth edges


def gradient(size, top, bottom, y0, y1):
    """Vertical gradient from top colour at y0 to bottom colour at y1."""
    w, h = size
    g = Image.new("RGBA", size)
    px = g.load()
    for y in range(h):
        t = min(max((y - y0) / (y1 - y0), 0), 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,)
        for x in range(w):
            px[x, y] = c
    return g


def clip(layer, mask):
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.paste(layer, (0, 0), Image.composite(layer, out, mask).getchannel("A"))
    return out


def glow(layer, radius):
    """Layer plus a soft blurred copy underneath it."""
    out = layer.filter(ImageFilter.GaussianBlur(radius))
    out.alpha_composite(layer)
    return out


def shrink(img, f, hot, k):
    """Scale the drawing by f around the hotspot so the click point stays put."""
    small = img.resize((int(img.width * f), int(img.height * f)), Image.LANCZOS)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hx, hy = hot[0] * k, hot[1] * k
    out.alpha_composite(small, (int(hx - hx * f), int(hy - hy * f)))
    return out


ARROW_F, SPIDER_F = 0.54, 0.6  # solid glyph ~= macOS 26 arrow (10x18 pt) and hand (15x19 pt)
LINE = 1.6  # thicker outlines so they survive the shrink


def arrow(scale):
    W, H = 28, 40  # points, matches the macOS 26 arrow
    k = scale * SS
    size = (W * k, H * k)
    pts = [(5, 5), (5, 31), (11, 25), (15, 35), (19, 33), (15, 24), (23, 24)]
    P = [(x * k, y * k) for x, y in pts]
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(P, fill=255)

    img = Image.new("RGBA", size, (0, 0, 0, 0))
    img.alpha_composite(clip(gradient(size, INK, NAVY, 8 * k, 34 * k), mask))
    # glowing crimson web: strands from the tip plus arcs, clipped to the arrow
    web = Image.new("RGBA", size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(web)
    tip = (5 * k, 5 * k)
    for ang in range(48, 96, 8):
        a = math.radians(ang)
        wd.line([tip, (tip[0] + 40 * k * math.cos(a), tip[1] + 40 * k * math.sin(a))], fill=CRIMSON, width=int(0.55 * k))
    for r in range(6, 38, 5):
        wd.arc([tip[0] - r * k, tip[1] - r * k, tip[0] + r * k, tip[1] + r * k], 42, 98, fill=CRIMSON, width=int(0.55 * k))
    img.alpha_composite(clip(glow(web, 0.9 * k), mask))

    d = ImageDraw.Draw(img)
    d.line(P + [P[0]], fill=RIM, width=int(2.2 * LINE * k), joint="curve")
    d.line(P + [P[0]], fill=BLACK, width=int(1.2 * LINE * k), joint="curve")
    d.line(P[:2], fill=CRIMSON, width=int(0.35 * LINE * k))  # crimson edge highlight on the left side
    img = shrink(img, ARROW_F, (5, 5), k)
    return img.resize((W * scale, H * scale), Image.LANCZOS), (W, H), (5.0, 5.0)


def spider(scale):
    W = H = 32
    k = scale * SS
    size = (W * k, H * k)
    c = lambda x, y: (x * k, y * k)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # silk thread from the top: the hotspot sits where the spider hangs
    d.line([c(16, 0), c(16, 9)], fill=RIM, width=int(1.6 * k))
    d.line([c(16, 0), c(16, 9)], fill=BLACK, width=int(0.7 * k))
    legs = []
    for side in (-1, 1):  # four bent legs per side
        for i, (y0, dy) in enumerate([(15, -6), (17, -2), (19, 3), (21, 7)]):
            knee = c(16 + side * (7.5 + i % 2), y0 + dy * 0.4 - 3)
            foot = c(16 + side * 13.5, y0 + dy)
            legs.append([c(16, y0 - 1), knee, foot])
    for col, w in ((RIM, 2.6), (BLACK, 1.4)):
        for leg in legs:
            d.line(leg, fill=col, width=int(w * k), joint="curve")
    for col, grow in ((RIM, 0.7), (BLACK, 0)):
        d.ellipse([c(10.5 - grow, 15 - grow), c(21.5 + grow, 28 + grow)], fill=col)  # abdomen
        d.ellipse([c(12.5 - grow, 8 - grow), c(19.5 + grow, 15.5 + grow)], fill=col)  # head
    # navy sheen on the body, then a glowing crimson hourglass and eyes
    body = Image.new("L", size, 0)
    ImageDraw.Draw(body).ellipse([c(11.3, 15.8), c(20.7, 27.2)], fill=255)
    img.alpha_composite(clip(gradient(size, INK, NAVY, 16 * k, 27 * k), body))
    mark = Image.new("RGBA", size, (0, 0, 0, 0))
    md = ImageDraw.Draw(mark)
    md.polygon([c(13.6, 17.6), c(18.4, 17.6), c(16, 21.5)], fill=CRIMSON)
    md.polygon([c(13.6, 25.4), c(18.4, 25.4), c(16, 21.5)], fill=CRIMSON)
    for ex in (14.6, 17.4):
        md.ellipse([c(ex - 0.9, 10.2), c(ex + 0.9, 12.0)], fill=EMBER)
    img.alpha_composite(glow(mark, 0.8 * k))
    img = shrink(img, SPIDER_F, (16, 1), k)
    return img.resize((W * scale, H * scale), Image.LANCZOS), (W, H), (16.0, 1.0)


def ibeam(scale):
    W, H = 23, 22  # points, matches the macOS 26 text cursor
    k = scale * SS
    size = (W * k, H * k)
    c = lambda x, y: (x * k, y * k)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    shape = [[c(8, 2), c(10, 2), c(11.5, 3.5), c(13, 2), c(15, 2)], [c(11.5, 3.5), c(11.5, 18.5)],
             [c(8, 20), c(10, 20), c(11.5, 18.5), c(13, 20), c(15, 20)], [c(9.5, 11), c(13.5, 11)]]
    for col, w in ((RIM, 2.8), (BLACK, 1.6)):
        for seg in shape:
            d.line(seg, fill=col, width=int(w * k), joint="curve")
    core = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(core).line([c(11.5, 5), c(11.5, 17)], fill=CRIMSON, width=int(0.5 * k))
    img.alpha_composite(glow(core, 0.6 * k))
    return img.resize((W * scale, H * scale), Image.LANCZOS), (W, H), (12.0, 11.0)


WAIT_FRAMES = 24  # macOS rejects animated cursors with more than 24 frames


def wait_frame(scale, f):
    """One frame of a spinning web: crimson strands and spiral on a dark disc."""
    W = H = 24
    k = scale * SS
    size = (W * k, H * k)
    cx = cy = 12 * k
    R = 10.5 * k
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - R - 0.8 * k, cy - R - 0.8 * k, cx + R + 0.8 * k, cy + R + 0.8 * k], fill=RIM)
    disc = Image.new("L", size, 0)
    ImageDraw.Draw(disc).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    img.alpha_composite(clip(gradient(size, INK, NAVY, 2 * k, 22 * k), disc))
    rot = 2 * math.pi * f / WAIT_FRAMES
    web = Image.new("RGBA", size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(web)
    for i in range(8):  # radial strands
        a = rot + i * math.pi / 4
        wd.line([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a))], fill=CRIMSON, width=int(0.5 * k))
    spiral = [(cx + (1.5 * k + 8 * k * t / (4 * math.pi)) * math.cos(rot + t), cy + (1.5 * k + 8 * k * t / (4 * math.pi)) * math.sin(rot + t))
              for t in [j * 0.05 for j in range(int(4 * math.pi / 0.05))]]
    wd.line(spiral, fill=EMBER, width=int(0.6 * k), joint="curve")
    img.alpha_composite(clip(glow(web, 0.7 * k), disc))
    return img.resize((W * scale, H * scale), Image.LANCZOS)


def wait(scale):
    """All frames stacked top to bottom, the layout Mousecape uses for animated cursors."""
    frames = [wait_frame(scale, f) for f in range(WAIT_FRAMES)]
    strip = Image.new("RGBA", (frames[0].width, frames[0].height * WAIT_FRAMES))
    for i, fr in enumerate(frames):
        strip.paste(fr, (0, i * fr.height))
    return strip, (24, 24), (12.0, 12.0)


def png(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def entry(draw, frames=1):
    reps = [draw(s) for s in (1, 2)]
    _, (w, h), (hx, hy) = reps[0]
    return {"FrameCount": frames, "FrameDuration": 1 / frames if frames > 1 else 0.0, "HotSpotX": hx, "HotSpotY": hy,
            "PointsWide": float(w), "PointsHigh": float(h), "Representations": [png(r[0]) for r in reps]}


def preview():
    """Both cursors at 4x on a dark and a light strip."""
    imgs = [arrow(4)[0], spider(4)[0], ibeam(4)[0], wait_frame(4, 0)]
    half = sum(im.width + 24 for im in imgs) + 12
    h = max(im.height for im in imgs) + 24
    out = Image.new("RGBA", (2 * half, h))
    for i, bg in enumerate([(28, 28, 32, 255), (240, 240, 242, 255)]):
        x = i * half
        out.paste(bg, (x, 0, x + half, h))
        x += 12
        for im in imgs:
            out.alpha_composite(im, (x, (h - im.height) // 2))
            x += im.width + 24
    out.save("preview.png")


cursors = {
    "com.apple.coregraphics.Arrow": entry(arrow),
    "com.apple.coregraphics.ArrowCtx": entry(arrow),
    "com.apple.cursor.13": entry(spider),  # pointing hand (links)
    "com.apple.coregraphics.IBeam": entry(ibeam),
    "com.apple.coregraphics.Wait": entry(wait, WAIT_FRAMES),
}
cape = {"Author": "Me", "CapeName": "WebSlinger Dark", "CapeVersion": 2.0, "Cloud": False, "Cursors": cursors,
        "HiDPI": True, "Identifier": "local.me.WebSlinger", "MinimumVersion": 2.0, "Version": 2.0}

if __name__ == "__main__":
    with open("WebSlinger.cape", "wb") as f:
        plistlib.dump(cape, f, fmt=plistlib.FMT_XML)
    preview()
    back = plistlib.load(open("WebSlinger.cape", "rb"))  # self-check: round-trips and images decode
    for v in back["Cursors"].values():
        assert 1 <= v["FrameCount"] <= 24, v["FrameCount"]
        for i, r in enumerate(v["Representations"]):
            im = Image.open(io.BytesIO(r))
            assert im.size == (int(v["PointsWide"]) * (i + 1), int(v["PointsHigh"]) * (i + 1) * v["FrameCount"]), im.size
    print("ok", list(back["Cursors"]))
