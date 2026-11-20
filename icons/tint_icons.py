"""Recolours app icons into the dark red monochrome the macOS Tinted Dock uses."""
import sys
from PIL import Image, ImageOps

DARK, MID, LIGHT = (34, 6, 8), (170, 18, 28), (255, 70, 70)  # background, artwork, brightest artwork


def tint(path_in, path_out):
    im = Image.open(path_in).convert("RGBA")
    # inverted so light backgrounds turn dark and the artwork turns red, like the Tinted Dock
    grey = ImageOps.autocontrast(ImageOps.invert(im.convert("RGB")).convert("L"), cutoff=1)
    red = ImageOps.colorize(grey, black=DARK, mid=MID, white=LIGHT).convert("RGBA")
    red.putalpha(im.getchannel("A"))
    red.save(path_out)


if __name__ == "__main__":
    for name in sys.argv[1:]:
        tint(f"app_icons/{name}_orig.png", f"app_icons/{name}_red.png")
    print("ok")
