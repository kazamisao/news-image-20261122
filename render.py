"""Render the news poster for 22 November 2026 (build-time only).

Draws "Atlas Garis Api": a stylised world map on a deep-navy atlas
sheet, red fire-lines linking the day's flashpoints, a gold highlight
on Shenzhen for APEC, quake/cyclone marks on Peru and India, and a
footer strip of short badges. Rendered at 3x and downscaled with
LANCZOS for crisp text. Deterministic: fixed geometry, no randomness.

Run:  python3 render.py   -> writes news.png (1024x1024) next to it.
Requires Pillow at build time only; the graded program (main.py)
never renders, it only copies the committed PNG.
"""

import math
from PIL import Image, ImageDraw, ImageFont

SS = 3                      # supersampling factor
W, H = 1024 * SS, 1024 * SS

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Map band (3x pixels): equirectangular, lon -180..180, lat 78..-58.
MAP_Y0, MAP_Y1 = 440, 2420
LAT_TOP, LAT_BOT = 78.0, -58.0


def project(lon: float, lat: float) -> tuple[float, float]:
    x = (lon + 180.0) / 360.0 * W
    y = MAP_Y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (MAP_Y1 - MAP_Y0)
    return x, y


# Simplified continent outlines (lon, lat) — stylised, not surveyed.
CONTINENTS = [
    # North America
    [(-168, 66), (-155, 71), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
     (-85, 66), (-80, 73), (-70, 70), (-60, 60), (-55, 52), (-60, 47),
     (-65, 44), (-70, 42), (-75, 38), (-76, 34), (-80, 32), (-81, 26),
     (-84, 30), (-85, 20), (-87, 15), (-90, 14), (-95, 18), (-100, 22),
     (-105, 20), (-110, 24), (-115, 28), (-120, 34), (-125, 40),
     (-130, 50), (-135, 58), (-145, 60), (-155, 58), (-165, 60), (-168, 66)],
    # South America
    [(-80, 9), (-77, 4), (-72, 8), (-64, 10), (-60, 8), (-52, 5), (-50, 0),
     (-44, -3), (-35, -7), (-35, -10), (-39, -15), (-40, -21), (-46, -24),
     (-49, -28), (-53, -33), (-58, -35), (-62, -39), (-66, -45), (-69, -50),
     (-71, -54), (-74, -48), (-73, -40), (-73, -30), (-71, -20), (-75, -15),
     (-79, -8), (-81, -4), (-80, 2), (-80, 9)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (0, 46), (3, 49), (7, 54), (9, 58),
     (13, 56), (18, 56), (22, 58), (27, 60), (30, 70), (38, 68), (44, 62),
     (44, 54), (38, 47), (30, 46), (24, 40), (19, 42), (13, 44), (5, 43),
     (-1, 38)],
    # Africa
    [(-17, 15), (-12, 27), (-6, 33), (3, 37), (10, 37), (19, 33),
     (28, 31), (33, 27), (37, 20), (43, 12), (51, 11), (48, 2),
     (41, -8), (36, -18), (33, -26), (27, -33), (19, -35), (15, -27),
     (12, -17), (12, -6), (9, 4), (-8, 5), (-14, 11)],
    # Asia
    [(38, 68), (50, 70), (66, 72), (82, 73), (98, 76), (112, 74),
     (128, 72), (145, 72), (160, 70), (178, 66), (170, 60), (162, 56),
     (156, 51), (142, 46), (135, 43), (130, 38), (127, 35), (122, 31),
     (120, 26), (113, 22), (108, 15), (104, 9), (100, 7), (97, 15),
     (92, 21), (88, 22), (84, 19), (80, 14), (77, 8), (73, 16),
     (70, 21), (66, 25), (61, 25), (57, 27), (53, 29), (49, 30),
     (44, 36), (41, 42), (38, 44)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (122, -34), (129, -32),
     (136, -35), (140, -38), (147, -39), (150, -37), (153, -31),
     (150, -24), (146, -19), (142, -14), (137, -12), (132, -11),
     (126, -14), (122, -17), (117, -20)],
]

NAVY_TOP = (10, 24, 44)
NAVY_BOT = (13, 34, 56)
LAND_FILL = (27, 58, 92)
LAND_LINE = (62, 110, 158)
GRID = (255, 255, 255, 18)
RED_GLOW = (255, 59, 48)
RED_CORE = (255, 120, 100)
GOLD = (255, 196, 66)
WHITE = (255, 255, 255)
INK = (6, 18, 32)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def star(cx: float, cy: float, r_out: float, r_in: float) -> list[tuple[float, float]]:
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rounded_pill(draw: ImageDraw.ImageDraw, box, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2,
                           fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def draw_label(draw, cx, cy, main, sub, f_main, f_sub, accent=WHITE):
    """Centred two-line label pill at (cx, cy); returns its box."""
    w1, h1 = text_size(draw, main, f_main)
    w2, h2 = text_size(draw, sub, f_sub) if sub else (0, 0)
    pad_x, pad_y = 42, 26
    w = max(w1, w2) + 2 * pad_x
    h = h1 + (h2 + 14 if sub else 0) + 2 * pad_y
    box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
    rounded_pill(draw, box, fill=INK, outline=WHITE, width=3)
    y = box[1] + pad_y
    draw.text((cx - w1 / 2, y), main, font=f_main, fill=accent)
    if sub:
        y += h1 + 14
        draw.text((cx - w2 / 2, y), sub, font=f_sub, fill=(205, 220, 235))
    return box


def draw_fire_line(draw, points, glow_layer):
    """Thick glowing red polyline through lon/lat points."""
    xy = [project(lon, lat) for lon, lat in points]
    g = ImageDraw.Draw(glow_layer)
    g.line(xy, fill=RED_GLOW + (90,), width=48, joint="curve")
    g.line(xy, fill=RED_GLOW + (140,), width=26, joint="curve")
    draw.line(xy, fill=RED_CORE, width=12, joint="curve")
    for x, y in xy:
        draw.ellipse([x - 13, y - 13, x + 13, y + 13],
                     fill=RED_GLOW, outline=WHITE, width=4)


def main() -> None:
    img = Image.new("RGB", (W, H))
    # Vertical navy gradient.
    top = Image.new("RGB", (1, H))
    top.putdata([tuple(int(NAVY_TOP[i] + (NAVY_BOT[i] - NAVY_TOP[i]) * y / H)
                       for i in range(3)) for y in range(H)])
    img = top.resize((W, H))
    draw = ImageDraw.Draw(img, "RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Graticule.
    for lon in range(-150, 181, 30):
        x = (lon + 180) / 360 * W
        draw.line([(x, MAP_Y0), (x, MAP_Y1)], fill=GRID, width=2)
    for lat in range(-30, 79, 30):
        _, y = project(0, lat)
        draw.line([(0, y), (W, y)], fill=GRID, width=2)

    # Continents.
    for poly in CONTINENTS:
        xy = [project(lon, lat) for lon, lat in poly]
        draw.polygon(xy, fill=LAND_FILL, outline=LAND_LINE, width=3)

    # ---- Title band ----
    f_title = font(BOLD, 290)
    f_sub = font(REG, 74)
    title = "DUNIA, 22 NOV"
    tw, th = text_size(draw, title, f_title)
    draw.text(((W - tw) / 2, 55), title, font=f_title, fill=WHITE)
    draw.line([(W / 2 - tw / 2, 55 + th + 18), (W / 2 + tw / 2, 55 + th + 18)],
              fill=RED_GLOW, width=10)
    sub = "MINGGU · 22 NOVEMBER 2026 — SATU HARI, SATU GAMBAR"
    sw, _ = text_size(draw, sub, f_sub)
    draw.text(((W - sw) / 2, 55 + th + 48), sub, font=f_sub, fill=(190, 210, 228))

    # ---- Fire lines ----
    draw_fire_line(draw, [(47.5, 29.3), (50.6, 26.2), (58.0, 23.6)], glow)
    draw_fire_line(draw, [(18.0, 59.0), (19.0, 54.0), (24.0, 52.0),
                          (32.0, 49.5)], glow)
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Estonia border closure: separate red dot with white ring.
    ex, ey = project(25.0, 59.0)
    draw.ellipse([ex - 15, ey - 15, ex + 15, ey + 15],
                 fill=RED_GLOW, outline=WHITE, width=4)

    # ---- Shenzhen gold star (APEC) ----
    sx, sy = project(114.05, 22.55)
    draw.ellipse([sx - 78, sy - 78, sx + 78, sy + 78],
                 outline=GOLD + (200,), width=6)
    draw.polygon(star(sx, sy, 66, 27), fill=GOLD)

    # ---- Peru quake mark ----
    qx, qy = project(-75.0, -10.0)
    for r, a in ((96, 120), (66, 170), (38, 230)):
        draw.ellipse([qx - r, qy - r, qx + r, qy + r],
                     outline=(255, 255, 255, a), width=7)
    draw.ellipse([qx - 16, qy - 16, qx + 16, qy + 16], fill=WHITE)

    # ---- India cyclone mark ----
    cx_, cy_ = project(78.0, 21.0)
    for r, start in ((30, 20), (58, 140), (86, 260)):
        draw.arc([cx_ - r, cy_ - r, cx_ + r, cy_ + r], start, start + 200,
                 fill=(140, 200, 255), width=10)
    draw.ellipse([cx_ - 14, cy_ - 14, cx_ + 14, cy_ + 14], fill=(140, 200, 255))

    # ---- Region labels ----
    f_lab = font(BOLD, 96)
    f_lsub = font(REG, 64)
    kx, ky = project(47.5, 29.3)
    box = draw_label(draw, 2050, 880, "TELUK DISERANG",
                     "Iran serang pangkalan AS", f_lab, f_lsub, RED_CORE)
    draw.line([(2050, box[3]), (kx + 20, ky - 30)], fill=WHITE, width=4)
    bx, by = project(20.0, 58.0)
    box = draw_label(draw, 1450, 560, "BALTIK MEMANAS",
                     "Ukraina · Polandia · Estonia", f_lab, f_lsub, RED_CORE)
    draw.line([(1620, box[3] - 10), (bx - 15, by - 25)], fill=WHITE, width=4)
    box = draw_label(draw, 2500, 1450, "SHENZHEN · APEC",
                     "Trump · Xi · Putin", f_lab, f_lsub, GOLD)
    draw.line([(2500, box[1]), (sx + 30, sy + 60)], fill=WHITE, width=4)
    box = draw_label(draw, 760, 1560, "ANDES 6,9",
                     "Gempa Peru", f_lab, f_lsub, WHITE)
    draw.line([(900, box[3] - 30), (qx - 90, qy + 30)], fill=WHITE, width=4)
    box = draw_label(draw, 2150, 1780, "SIKLON AKVAN",
                     "India", f_lab, f_lsub, (140, 200, 255))
    draw.line([(2150, box[1]), (cx_ + 40, cy_ + 80)], fill=WHITE, width=4)

    # ---- Footer badges ----
    f_badge = font(BOLD, 54)
    badges = ["COP31 BUNTU", "SINALOA 11 TEWAS", "BOLSONARO ICU",
              "CATHERINE BBC", "FBI: PERETASAN"]
    widths = [text_size(draw, b, f_badge)[0] + 56 for b in badges]
    gap = 26
    total = sum(widths) + gap * (len(badges) - 1)
    x = (W - total) / 2
    y0, y1 = 2500, 2610
    for b, w in zip(badges, widths):
        rounded_pill(draw, [x, y0, x + w, y1], fill=(28, 52, 84),
                     outline=WHITE, width=3)
        bw, bh = text_size(draw, b, f_badge)
        draw.text((x + (w - bw) / 2, y0 + (y1 - y0 - bh) / 2), b,
                  font=f_badge, fill=WHITE)
        x += w + gap
    f_foot = font(REG, 54)
    foot = "RINGKASAN BERITA DUNIA · 22 NOVEMBER 2026"
    fw, _ = text_size(draw, foot, f_foot)
    draw.text(((W - fw) / 2, 2680), foot, font=f_foot, fill=(150, 175, 198))

    # Downscale to final size and save.
    final = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    final.save("news.png", optimize=True)
    print("wrote news.png")


if __name__ == "__main__":
    main()
