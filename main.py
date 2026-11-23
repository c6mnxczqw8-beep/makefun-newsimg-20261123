#!/usr/bin/env python3
"""Entry program for the news-image-20261123 make.fun bounty.

It draws an original newspaper front page -- "THE WORLD TODAY / MONDAY
23 NOVEMBER 2026" -- with six illustrated panels summing up that day's
world news, and writes it as a 1024x1024 PNG to the output directory
(MAKEFUN_OUTPUT_DIR, default /output).

The drawing uses Pillow when it is available. The grading container is
standard-library-only, so when Pillow is missing the program falls back
to copying the bundled entry.png -- which this same program's drawing
code produced -- so the bytes written are identical either way. There
is no randomness and no clock anywhere in the drawing: every run on the
same machine writes exactly the same bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

W = H = 1024
PAPER = (247, 242, 231)
INK = (22, 19, 15)
GREY = (96, 92, 84)

FONT_CANDIDATES = {
    "serif": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "serif-bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "serif-italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
}


def load_font(ImageFont, kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    """Greedy word wrap against pixel widths; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, ImageFont, kind, text, start_size, max_width):
    """Largest bold size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > 10:
        font = load_font(ImageFont, kind, size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return load_font(ImageFont, kind, size)


def draw_masthead(draw, ImageFont):
    # Double rule above the nameplate, in the classic broadsheet style.
    draw.line([(28, 22), (996, 22)], fill=INK, width=2)
    draw.line([(28, 28), (996, 28)], fill=INK, width=6)
    title = "THE WORLD TODAY"
    font = fit_font(draw, ImageFont, "serif-bold", title, 96, 940)
    tw = draw.textlength(title, font=font)
    draw.text(((W - tw) / 2, 40), title, font=font, fill=INK)
    # Black date band.
    draw.rectangle([28, 120, 996, 162], fill=INK)
    date = "MONDAY 23 NOVEMBER 2026"
    dfont = fit_font(draw, ImageFont, "serif-bold", date, 34, 700)
    dw = draw.textlength(date, font=dfont)
    draw.text(((W - dw) / 2, 129), date, font=dfont, fill=(255, 255, 255))
    sub = "The day's six biggest stories, drawn and typeset by program code"
    sfont = load_font(ImageFont, "serif-italic", 17)
    sw = draw.textlength(sub, font=sfont)
    draw.text(((W - sw) / 2, 168), sub, font=sfont, fill=GREY)
    draw.line([(28, 190), (996, 190)], fill=INK, width=2)


def panel_frame(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    return (x + 6, y + 6, x + w - 6, y + 224)  # illustration box


def draw_panel_text(draw, ImageFont, x, y, w, headline, caption):
    hfont = load_font(ImageFont, "serif-bold", 25)
    cy = y + 232
    for line in wrap(draw, headline, hfont, w - 16):
        draw.text((x + 10, cy), line, font=hfont, fill=INK)
        cy += 30
    cfont = load_font(ImageFont, "serif", 16)
    cy += 4
    for line in wrap(draw, caption, cfont, w - 16):
        draw.text((x + 10, cy), line, font=cfont, fill=(52, 48, 42))
        cy += 21


# --- Panel illustrations: flat editorial shapes, all original --------

def ill_libya(draw):
    # Naval drones strike a warship off a Libyan port.
    x0, y0, x1, y1 = 0, 0, 312, 218  # local coords, offset applied by caller
    draw.rectangle([x0, y0, x1, 120], fill=(172, 203, 226))       # sky
    draw.rectangle([x0, 120, x1, y1], fill=(36, 90, 138))         # sea
    for i in range(5):                                            # waves
        yy = 138 + i * 16
        draw.line([(14 + (i % 2) * 22, yy), (90 + (i % 2) * 22, yy)],
                  fill=(120, 170, 205), width=2)
    # Warship: hull, superstructure, mast.
    draw.polygon([(70, 128), (238, 128), (222, 146), (88, 146)], fill=(88, 94, 102))
    draw.rectangle([128, 108, 196, 128], fill=(104, 110, 118))
    draw.rectangle([150, 88, 162, 108], fill=(104, 110, 118))
    draw.line([(156, 88), (156, 66)], fill=(70, 74, 80), width=3)
    # Explosion at the stern.
    cx, cy = 84, 118
    for dx, dy, r in [(0, 0, 15), (-14, -8, 10), (13, -10, 10), (2, -18, 9)]:
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                     fill=(240, 150, 40))
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(250, 210, 90))
    # Three naval drones with wakes.
    for bx, by in [(36, 176), (120, 192), (216, 178)]:
        draw.polygon([(bx, by), (bx + 30, by), (bx + 24, by + 8), (bx + 6, by + 8)],
                     fill=(28, 30, 34))
        draw.line([(bx - 16, by + 4), (bx, by + 4)], fill=(210, 230, 242), width=2)
        draw.line([(bx - 10, by + 9), (bx + 2, by + 9)], fill=(210, 230, 242), width=2)
    # Port cranes on the right horizon.
    for px in (258, 286):
        draw.line([(px, 120), (px, 78)], fill=(70, 74, 80), width=3)
        draw.line([(px, 78), (px + 22, 78)], fill=(70, 74, 80), width=3)
        draw.line([(px + 20, 78), (px + 20, 96)], fill=(70, 74, 80), width=2)


def ill_kyiv(draw):
    # Rescuers at a collapsed block of flats, Kyiv region.
    draw.rectangle([0, 0, 312, 218], fill=(206, 188, 164))        # dusk sky
    draw.rectangle([0, 176, 312, 218], fill=(120, 108, 92))       # ground
    # Standing part of the block.
    draw.rectangle([26, 52, 168, 178], fill=(148, 142, 130))
    for r in range(4):
        for c in range(3):
            wx, wy = 40 + c * 42, 64 + r * 28
            draw.rectangle([wx, wy, wx + 24, wy + 16], fill=(52, 50, 46))
    draw.rectangle([26, 40, 168, 52], fill=(110, 104, 94))        # roof slab
    # Collapsed right section: jagged floors and rubble.
    draw.polygon([(168, 70), (238, 96), (246, 132), (230, 178), (168, 178)],
                 fill=(132, 126, 114))
    draw.line([(168, 92), (240, 116)], fill=(90, 84, 74), width=3)
    draw.line([(168, 122), (244, 140)], fill=(90, 84, 74), width=3)
    for rx, ry, rw in [(196, 168, 34), (232, 176, 26), (168, 180, 30), (252, 188, 22)]:
        draw.polygon([(rx, ry), (rx + rw, ry), (rx + rw - 8, ry - 10)], fill=(104, 98, 88))
    # Dust cloud.
    for dx, dy, r in [(206, 62, 22), (232, 52, 16), (186, 48, 13)]:
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(216, 208, 194))
    # Rescue truck with orange light bar.
    draw.rectangle([36, 182, 108, 202], fill=(196, 84, 30))
    draw.rectangle([44, 170, 84, 182], fill=(214, 102, 40))
    draw.rectangle([58, 158, 74, 170], fill=(250, 176, 60))
    for wx in (50, 94):
        draw.ellipse([wx - 8, 196, wx + 8, 210], fill=(30, 28, 26))
    # Two rescuer figures.
    for fx in (140, 164):
        draw.ellipse([fx - 5, 178, fx + 5, 188], fill=(240, 190, 60))
        draw.line([(fx, 188), (fx, 202)], fill=(40, 40, 44), width=4)


def ill_cop(draw):
    # COP31: a wilting, cracked globe above an empty conference table.
    draw.rectangle([0, 0, 312, 218], fill=(238, 226, 198))
    # Blazing sun, top right.
    sx, sy = 262, 44
    for ang in range(0, 360, 45):
        import math
        rad = math.radians(ang)
        x1, y1 = sx + 26 * math.cos(rad), sy + 26 * math.sin(rad)
        x2, y2 = sx + 38 * math.cos(rad), sy + 38 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=(232, 150, 40), width=4)
    draw.ellipse([sx - 22, sy - 22, sx + 22, sy + 22], fill=(244, 178, 62))
    # Globe, cracked, tilted stems wilting beneath it.
    gx, gy, gr = 118, 92, 54
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(96, 148, 104))
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 20, 160, fill=(52, 96, 120), width=3)
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=(52, 96, 120), width=3)
    draw.line([(gx, gy - gr), (gx, gy + gr)], fill=(52, 96, 120), width=3)
    cracks = [(gx - 10, gy - 40), (gx + 4, gy - 18), (gx - 6, gy + 2),
              (gx + 10, gy + 22), (gx + 2, gy + 44)]
    draw.line(cracks, fill=(60, 44, 30), width=3)
    draw.line([(gx + 4, gy - 18), (gx + 24, gy - 8)], fill=(60, 44, 30), width=3)
    # Wilted stem and leaf.
    draw.arc([gx - 30, gy + gr - 6, gx + 26, gy + gr + 44], 200, 320,
             fill=(96, 130, 70), width=4)
    # Empty conference table with nameplates and untouched glasses.
    draw.rectangle([18, 168, 294, 182], fill=(110, 84, 58))
    draw.rectangle([30, 182, 42, 204], fill=(88, 66, 44))
    draw.rectangle([270, 182, 282, 204], fill=(88, 66, 44))
    for px in (52, 118, 184, 244):
        draw.rectangle([px, 152, px + 30, 168], fill=(250, 248, 240), outline=(150, 144, 130))
        draw.rectangle([px + 40, 158, px + 46, 168], fill=(170, 200, 220))
    # Drooping flag poles behind the table.
    for fx in (36, 276):
        draw.line([(fx, 66), (fx, 152)], fill=(120, 116, 108), width=3)
        draw.polygon([(fx, 66), (fx + 26, 74), (fx, 88)], fill=(168, 158, 140))


def ill_democrats(draw, F):
    # The Capitol under a deep-blue night, and the number of the day.
    draw.rectangle([0, 0, 312, 218], fill=(22, 42, 92))
    for sx, sy in [(24, 22), (66, 40), (282, 26), (238, 14), (292, 66), (40, 74)]:
        draw.ellipse([sx, sy, sx + 4, sy + 4], fill=(230, 234, 245))
    # Dome and facade in pale stone.
    draw.rectangle([96, 128, 216, 176], fill=(226, 228, 232))
    draw.pieslice([104, 62, 208, 150], 180, 360, fill=(226, 228, 232))
    draw.rectangle([150, 44, 162, 66], fill=(226, 228, 232))
    draw.ellipse([152, 36, 160, 46], fill=(250, 200, 80))
    for cx in range(108, 200, 16):
        draw.rectangle([cx, 138, cx + 7, 172], fill=(168, 174, 186))
    draw.rectangle([84, 176, 228, 184], fill=(200, 204, 210))
    # The tally, in gold.
    font = F("serif-bold", 84)
    draw.text((18, 108), "258", font=font, fill=(250, 200, 80))
    # Rows of seats: a blue wave over a red rump.
    for r in range(3):
        for c in range(14):
            cx, cy = 16 + c * 20, 192 + r * 8
            colour = (86, 130, 220) if c < 10 else (196, 84, 84)
            draw.ellipse([cx, cy, cx + 7, cy + 5], fill=colour)


def ill_khartoum(draw, F):
    # Dawn over Khartoum: drones above the skyline, a U.N. building below.
    bands = [(52, 48, 84), (96, 62, 96), (164, 84, 84), (216, 124, 78), (240, 168, 104)]
    for i, colour in enumerate(bands):
        draw.rectangle([0, i * 30, 312, i * 30 + 30], fill=colour)
    draw.rectangle([0, 150, 312, 218], fill=(40, 34, 40))         # ground
    # Skyline silhouettes, with a minaret.
    for bx, bh in [(8, 52), (44, 70), (84, 44), (196, 62), (238, 48), (272, 66)]:
        draw.rectangle([bx, 168 - bh, bx + 32, 168], fill=(30, 26, 32))
    draw.rectangle([150, 96, 158, 168], fill=(30, 26, 32))
    draw.polygon([(146, 96), (154, 78), (162, 96)], fill=(30, 26, 32))
    # The U.N. building, white, in the foreground.
    draw.rectangle([104, 150, 196, 196], fill=(238, 238, 240))
    draw.rectangle([104, 142, 196, 150], fill=(210, 214, 220))
    font = F("serif-bold", 30)
    draw.text((128, 156), "UN", font=font, fill=(40, 100, 170))
    # Three quadcopter drones.
    for dx, dy in [(56, 44), (150, 28), (248, 52)]:
        draw.rectangle([dx - 7, dy - 3, dx + 7, dy + 3], fill=(18, 16, 20))
        for rx in (dx - 16, dx + 10):
            draw.line([(rx, dy - 6), (rx + 6, dy - 6)], fill=(18, 16, 20), width=2)
        draw.line([(dx, dy + 3), (dx, dy + 9)], fill=(18, 16, 20), width=2)
    # A plume of smoke over the rooftops.
    for dx, dy, r in [(232, 118, 13), (244, 104, 10), (254, 92, 8)]:
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(120, 112, 112))


def ill_manchester(draw, F):
    # A great arena at night, the crowd streaming out through haze.
    draw.rectangle([0, 0, 312, 218], fill=(14, 18, 32))
    # The arena bowl.
    draw.rounded_rectangle([36, 34, 276, 128], radius=26, fill=(58, 68, 94))
    draw.rounded_rectangle([36, 34, 276, 76], radius=20, fill=(84, 98, 128))
    font = F("serif-bold", 27)
    tw = draw.textlength("ARENA", font=font)
    draw.text(((312 - tw) / 2, 44), "ARENA", font=font, fill=(250, 226, 150))
    for wx in range(58, 258, 20):                                  # lit windows
        draw.rectangle([wx, 92, wx + 10, 104], fill=(250, 214, 130))
    # Haze hanging over the doors.
    for dx, dy, r in [(110, 128, 26), (160, 122, 32), (208, 128, 24)]:
        draw.ellipse([dx - r, dy - r // 2, dx + r, dy + r // 2], fill=(150, 152, 160))
    # Police light bars at the edges.
    for px in (30, 262):
        draw.rectangle([px, 138, px + 20, 146], fill=(40, 44, 56))
        draw.rectangle([px, 132, px + 9, 138], fill=(70, 120, 250))
        draw.rectangle([px + 11, 132, px + 20, 138], fill=(240, 70, 70))
    # The crowd: rows of heads pouring toward the bottom corners.
    colours = [(232, 190, 140), (170, 190, 220), (220, 160, 160),
               (180, 220, 180), (240, 230, 200), (200, 180, 230)]
    n = 0
    for r in range(4):
        for c in range(13):
            cx = 22 + c * 23 + (r % 2) * 9
            cy = 158 + r * 14
            draw.ellipse([cx, cy, cx + 10, cy + 10], fill=colours[n % len(colours)])
            n += 1


STORIES = [
    (lambda d, F: ill_libya(d),
     "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
     "Seven naval drones struck near Benghazi: a warship sunk, a "
     "helicopter destroyed and a cargo ship hit."),
    (lambda d, F: ill_kyiv(d),
     "RUSSIAN STRIKES KILL 15 IN KYIV REGION",
     "A flats block collapsed in Dymer. Rescuers raced on Monday to "
     "find survivors in the rubble."),
    (lambda d, F: ill_cop(d),
     "COP31 TALKS COLLAPSE WITH NO DEAL",
     "The EU and others rejected a final text that dropped any "
     "mention of moving away from fossil fuels."),
    (ill_democrats,
     "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992",
     "A North Carolina win took the party to at least 258 seats, "
     "its largest majority in over 30 years."),
    (ill_khartoum,
     "DRONES HIT HOMES AND U.N. BUILDING IN KHARTOUM",
     "Dawn strikes destroyed a house and damaged U.N. premises "
     "with staff inside Sudan's capital."),
    (ill_manchester,
     "12,000 EVACUATED FROM MANCHESTER ARENA",
     "An unknown substance released in the crowd left more than "
     "50 people treated and one in hospital."),
]

PANEL_W, PANEL_H = 312, 397
GRID_X = (28, 356, 684)
GRID_Y = (202, 613)


def render(out_path):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, ImageFont)

    def font_of(kind, size):
        return load_font(ImageFont, kind, size)

    for i, (ill, headline, caption) in enumerate(STORIES):
        px, py = GRID_X[i % 3], GRID_Y[i // 3]
        tile = Image.new("RGB", (PANEL_W, 218), PAPER)
        ill(ImageDraw.Draw(tile), font_of)
        img.paste(tile, (px, py + 6))
        draw = ImageDraw.Draw(img)
        panel_frame(draw, px, py, PANEL_W, PANEL_H)
        draw_panel_text(draw, ImageFont, px, py, PANEL_W, headline, caption)

    img.save(out_path, format="PNG")
    return out_path


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    try:
        import PIL  # noqa: F401
    except ImportError:
        # Standard-library-only runtime: ship the bundled image, which
        # this program's drawing code produced, byte for byte.
        shutil.copyfile(os.path.join(HERE, "entry.png"), dst)
        return 0
    render(dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
