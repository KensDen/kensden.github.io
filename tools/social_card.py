#!/usr/bin/env python3
"""Share cards for the dispatches: 1200x630 JPEGs, each a dispatch's own image
with its title and "Ken Connell" set on it in the site's fonts.

    python3 tools/social_card.py            # build every card in CARDS
    python3 tools/social_card.py sanctuary  # build only cards whose file name contains "sanctuary"

Needs Google Chrome (or set CHROME=/path/to/chrome) and macOS sips. Each card
must come out under 300 KB; the script lowers the JPEG quality until it does.
"""
import html
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = os.environ.get(
    "CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
W, H = 1200, 630
MAX_BYTES = 300 * 1024

# layout "cover": the image fills the card. "side": a portrait image stands at
# full height on the right, over a blurred copy of itself (as on the Multiverse card).
# "text_at": "top" sets the text in the sky instead, for a subject low in the frame.
# "band": N, for a light background: the image is fitted, whole, into the white
# space above a solid dark band N px tall that carries the text.
# "font_size" and "text_width" override the title's size and the text block's width.
CARDS = [
    {"out": "social-card-batman.jpg", "image": "batmobile.webp", "layout": "side",
     "title": "Batman Has No Superpowers. That’s the Whole Point."},
    {"out": "social-card-seat-at-the-table.jpg", "image": "chair.jpg", "layout": "cover",
     "position": "center 40%", "title": "Building a Seat at the Table"},
    {"out": "social-card-measuring-security.jpg", "image": "boxes.jpg", "layout": "cover",
     "position": "center 45%", "title": "Measuring Security"},
    {"out": "social-card-sanctuary.jpg", "image": "sanctuary.jpg", "layout": "cover",
     "position": "center 60%", "text_at": "top", "title": "Sanctuary Protocol"},
    {"out": "social-card-multiverse-titled.jpg", "image": "social-card-multiverse.jpg", "layout": "cover",
     "font_size": 60, "text_width": 900,
     "title": "The Multiverse Is a System Architecture, Complete with a Control Plane"},
    {"out": "social-card-10-cent-dreams-titled.jpg", "image": "social-card-10-cent-dreams.jpg", "layout": "cover",
     "band": 200, "font_size": 54, "text_width": 1080, "title": "10-Cent Dreams of a Two-Sided Coin"},
]

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"Space Grotesk";font-weight:300 700;src:url("%(root)s/fonts/space-grotesk-latin.woff2") format("woff2")}
@font-face{font-family:"JetBrains Mono";font-weight:400 800;src:url("%(root)s/fonts/jetbrains-mono-latin.woff2") format("woff2")}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:#0a0e12}
.card{position:relative;width:%(w)dpx;height:%(h)dpx;overflow:hidden}
.bg{position:absolute;inset:0;background:url("%(img)s") %(pos)s/cover no-repeat}
.blur{position:absolute;inset:-40px;background:url("%(img)s") center/cover no-repeat;filter:blur(28px) brightness(.45)}
.side{position:absolute;top:0;right:0;height:%(h)dpx;width:auto;box-shadow:0 0 40px rgba(0,0,0,.6)}
.shade{position:absolute;inset:0;background:
  linear-gradient(to top, rgba(10,14,18,.94) 0%%, rgba(10,14,18,.78) 34%%, rgba(10,14,18,.18) 64%%, rgba(10,14,18,0) 80%%),
  linear-gradient(to right, rgba(10,14,18,.55) 0%%, rgba(10,14,18,0) 60%%)}
.side-shade{position:absolute;inset:0;background:linear-gradient(to right, rgba(10,14,18,.92) 0%%, rgba(10,14,18,.86) 48%%, rgba(10,14,18,.2) 66%%, rgba(10,14,18,0) 74%%)}
.top-shade{position:absolute;inset:0;background:linear-gradient(to bottom, rgba(10,14,18,.82) 0%%, rgba(10,14,18,.5) 34%%, rgba(10,14,18,0) 58%%)}
.fit{position:absolute;left:0;right:0;top:0;padding:14px 0;background:#fff center/contain no-repeat;background-origin:content-box}
.band{position:absolute;left:0;right:0;bottom:0;background:rgba(10,14,18,.93);border-top:3px solid #3fb950}
.text{position:absolute;left:64px;bottom:56px;width:%(tw)dpx}
.text.top{bottom:auto;top:56px}
.in-band{bottom:36px}.in-band .eyebrow{margin-bottom:14px}.in-band .by{margin-top:18px}
.eyebrow{font:500 22px/1 "JetBrains Mono",monospace;color:#3fb950;margin-bottom:18px}
.title{font:700 %(fs)dpx/1.06 "Space Grotesk",sans-serif;color:#e6edf3;letter-spacing:-.01em;text-wrap:balance;text-shadow:0 2px 18px rgba(0,0,0,.55)}
.by{font:500 30px/1 "JetBrains Mono",monospace;color:#39d3c5;margin-top:24px}
</style></head><body><div class="card">%(art)s<div class="%(text_class)s">
<div class="eyebrow">&gt; kensden.github.io</div>
<div class="title">%(title)s</div>
<div class="by">Ken Connell</div>
</div></div></body></html>"""


def build(card):
    img = "file://" + os.path.join(ROOT, card["image"])
    if card["layout"] == "side":
        art = '<div class="blur"></div><img class="side" src="%s" alt=""><div class="side-shade"></div>' % img
        tw, fs = 660, 64
    else:
        if card.get("band"):
            art = ('<div class="fit" style="height:%dpx;background-image:url(\'%s\')"></div>'
                   '<div class="band" style="height:%dpx"></div>' % (H - card["band"], img, card["band"]))
        else:
            shade = "top-shade" if card.get("text_at") == "top" else "shade"
            art = '<div class="bg"></div><div class="%s"></div>' % shade
        tw, fs = 1000, 76
    text_class = "text top" if card.get("text_at") == "top" else "text"
    if card.get("band"):
        text_class += " in-band"
    tw = card.get("text_width", tw)
    fs = card.get("font_size", fs)
    page = TEMPLATE % {"root": "file://" + ROOT, "w": W, "h": H, "img": img,
                       "pos": card.get("position", "center"), "art": art,
                       "tw": tw, "fs": fs,
                       "text_class": text_class, "title": html.escape(card["title"])}
    out = os.path.join(ROOT, card["out"])
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "card.html")
        png = os.path.join(tmp, "card.png")
        with open(src, "w", encoding="utf-8") as f:
            f.write(page)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--allow-file-access-from-files", "--force-device-scale-factor=1",
                        "--virtual-time-budget=4000", "--window-size=%d,%d" % (W, H),
                        "--screenshot=" + png, "file://" + src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for quality in (86, 82, 78, 74, 70, 66, 62):
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
                            png, "--out", out], check=True, stdout=subprocess.DEVNULL)
            size = os.path.getsize(out)
            if size <= MAX_BYTES:
                break
        else:
            sys.exit("%s is still %d bytes at quality %d" % (card["out"], size, quality))
    print("%s  %d KB  (quality %d)" % (card["out"], (size + 1023) // 1024, quality))


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for c in CARDS:
        if only in c["out"]:
            build(c)
