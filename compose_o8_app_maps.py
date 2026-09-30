"""Output 8 (Sep 2026): legends, area labels and the occupancy grid for the app prints."""
import json
from PIL import Image, ImageDraw, ImageFont
D = r"C:/Users/user/Yerevan-Parking/Final Presentation/SEP'26/O8 app maps/raw/"
O = D + "../"
import os; os.makedirs(O, exist_ok=True)


def save(img, name):
    """JPEG at 2400 px wide: ~380 dpi at the 6.3 in the report uses, a fraction of the PNG size."""
    img = img.convert("RGB")
    if img.width > 2400:
        img = img.resize((2400, round(img.height * 2400 / img.width)), Image.LANCZOS)
    img.save(O + name + ".jpg", quality=90)
F = lambda s, b=False: ImageFont.truetype("C:/Windows/Fonts/" + ("segoeuib.ttf" if b else "segoeui.ttf"), s)
PANEL, EDGE, TXT = (12, 12, 22, 235), (60, 60, 80), (235, 235, 240)

def legend(img, items, title=None, pos="br", s=2):
    d = ImageDraw.Draw(img, "RGBA"); f = F(15*s); ft = F(13*s, True)
    rows = len(items) + (1 if title else 0)
    w = 20*s + max(d.textlength(t, font=f) for t, _ in items) + 34*s
    if title: w = max(w, d.textlength(title, font=ft) + 40*s)
    h = 16*s + rows * 28*s
    W, H = img.size
    x0 = W - w - 24*s if pos == "br" else 24*s
    y0 = H - h - 50*s
    d.rounded_rectangle([x0, y0, x0+w, y0+h], 10*s, fill=PANEL, outline=EDGE, width=s)
    y = y0 + 10*s
    if title:
        d.text((x0+18*s, y), title.upper(), font=ft, fill=(170, 170, 185)); y += 28*s
    for t, col in items:
        d.rounded_rectangle([x0+18*s, y+6*s, x0+32*s, y+20*s], 3*s, fill=col)
        d.text((x0+42*s, y), t, font=f, fill=TXT); y += 28*s
    return img

LOC = [("On-street", "#42a5f5"), ("Pocket", "#ab47bc"), ("Set-back", "#ffaa00"), ("Off-street lot", "#2ecc71")]
for c in ("c1", "c2"):
    save(legend(Image.open(D + f"loc_{c}.png").convert("RGB"), LOC, "Parking location"), f"loc_{c}")
save(legend(Image.open(D + "removed.png").convert("RGB"),
       [("Retained in the conceptual design", "#4CAF50"), ("Removed", "#EF5350")], "On-corridor on-street"), "removed")
for n in ("reg", "method", "signage", "marking"):
    save(Image.open(D + n + ".png"), n)

NAMES = {"kentron": "Kentron", "komitas": "Komitas Avenue", "mega": "Gai Avenue", "garegin": "Garegin Nzhdeh",
         "shiraz": "Shiraz/Hasratyan", "malatia": "Malatia-Sebastia"}
OFF = {"kentron": (90, 40), "komitas": (60, 70), "mega": (-230, 40), "garegin": (70, -60), "shiraz": (60, 20), "malatia": (40, 90)}
img = Image.open(D + "areas.png").convert("RGB"); d = ImageDraw.Draw(img, "RGBA")
pts = json.load(open(D + "areas_px.json")); f = F(34, True)
for k, (x, y) in pts.items():
    x, y = 2*x, 2*y; dx, dy = OFF[k]; tx, ty = x + 2*dx, y + 2*dy
    tw = d.textlength(NAMES[k], font=f)
    d.line([x, y, tx, ty + 24], fill=(255, 255, 255, 200), width=3)
    d.rounded_rectangle([tx - 14, ty - 6, tx + tw + 14, ty + 50], 10, fill=PANEL, outline=(0, 206, 209), width=3)
    d.text((tx, ty), NAMES[k], font=f, fill=TXT)
save(legend(img, [("Surveyed zone", "#2ecc71"), ("Off-street yard", "#7c4dff")]), "areas")

# occupancy grid: 3 x 2 crops of the per-area views
ORDER = ["kentron", "komitas", "mega", "garegin", "shiraz", "malatia"]
cw, ch = 1500, 1050
tiles = []
for k in ORDER:
    im = Image.open(D + f"occ_{k}.png").convert("RGB")
    W, H = im.size; bw, bh = int(H*cw/ch), H
    if bw > W: bw, bh = W, int(W*ch/cw)
    im = im.crop(((W-bw)//2, (H-bh)//2, (W+bw)//2, (H+bh)//2)).resize((cw, ch), Image.LANCZOS)
    dd = ImageDraw.Draw(im, "RGBA"); ft = F(46, True); tw = dd.textlength(NAMES[k], font=ft)
    dd.rounded_rectangle([20, 20, 60 + tw, 100], 12, fill=PANEL, outline=EDGE, width=2)
    dd.text((40, 30), NAMES[k], font=ft, fill=TXT)
    tiles.append(im)
# white gutters between the six panels so each area reads as its own map
g = 28; leg_h = 130
grid = Image.new("RGB", (3*cw + 4*g, 2*ch + 3*g + leg_h + g), (255, 255, 255))
for i, t in enumerate(tiles):
    grid.paste(t, (g + (i % 3)*(cw + g), g + (i // 3)*(ch + g)))
ly = 2*ch + 3*g
dg = ImageDraw.Draw(grid)
dg.rectangle([g, ly, grid.width - g - 1, ly + leg_h - 1], fill=(8, 8, 14))
fl = F(44); x = g + 30; y = ly + 38
for t, col in [("Daily average occupancy:", None), ("85% or less", "#2ecc71"), ("86-100%", "#ff8a8a"),
               ("over 100%", "#ff4d4d"), ("dashed purple outline: off-street yard", "#7c4dff")]:
    if col: dg.rounded_rectangle([x, y+8, x+40, y+48], 6, fill=col); x += 56
    dg.text((x, y), t, font=fl, fill=TXT); x += dg.textlength(t, font=fl) + 60
save(grid, "occ_grid")
print("done")
