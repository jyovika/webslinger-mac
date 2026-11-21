"""Builds WebSlinger.rstheme by recolouring RStudio's bundled Tomorrow Night theme."""
import re
from urllib.parse import quote

from make_web import web_svg

SRC = "/Applications/RStudio.app/Contents/Resources/app/resources/themes/tomorrow_night.rstheme"
PALETTE = {  # Tomorrow Night colour -> WebSlinger colour
    "25282c": "12131A",  # gutter background
    "c5c8c6": "E4DEE2",  # main text
    "1d1f21": "0C0D12",  # editor background
    "aeafad": "FF3340",  # cursor
    "373b41": "4A1520",  # selection
    "4b4e55": "3A3D4E",  # bracket match, invisibles
    "282a2e": "181A24",  # current line
    "b294bb": "E3242B",  # keywords: function, if, for
    "8abeb7": "FF4D5A",  # operators: <- %>% +
    "de935f": "A9C1FF",  # numbers, TRUE, NULL, arguments
    "ced1cf": "E4DEE2",
    "ced2cf": "E4DEE2",
    "df5f5f": "8B0A14",  # errors
    "b798bf": "3D4F8F",  # deprecated
    "81a2be": "5B8CFF",  # function names
    "f0c674": "FF6E6E",  # classes, types
    "b5bd68": "FF8C94",  # strings, headings
    "cc6666": "F2ECEF",  # variables
    "969896": "6B6880",  # comments
}

text = open(SRC).read()
head, sep, tail = text.partition(".xtermInvertColor")  # leave console ANSI colours alone
head = head.replace("rs-theme-name: Tomorrow Night", "rs-theme-name: WebSlinger")
head = head.replace("background: #444;", "background: #2A1A22;")  # print margin
head = re.sub(r"#([0-9a-fA-F]{6})\b", lambda m: "#" + PALETTE.get(m.group(1).lower(), m.group(1)), head)
head += "\n.ace_comment { font-style: italic; }\n"
# faint web in the code editor's top-right corner; it stays put while the code scrolls.
# Scoped to the source editor's scroller: a plain .ace_editor rule lands on the console instead.
# Drawn as an overlay: RStudio paints layers over the scroller's own background in the source pane.
head += ('#rstudio_source_text_editor .ace_scroller::after { content: ""; position: absolute; top: 0; right: 0;'
         ' width: 420px; height: 420px; pointer-events: none; z-index: 10;'
         ' background: url("data:image/svg+xml;utf8,' + quote(web_svg()) + '") no-repeat right top / 420px 420px; }\n')
open("WebSlinger.rstheme", "w").write(head + sep + tail)

leftover = [c for c in PALETTE if re.search("#" + c, head, re.I)]
assert not leftover, leftover
print("ok")
