"""Draw the 18 November front page using only Pillow and local fonts."""

from functools import lru_cache
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PAPER = "#F6F1E7"
INK = "#1A1A1A"
RED = "#B3202C"
BLUE = "#1F4E79"
GOLD = "#E8B33A"
WHITE = "#FFFFFF"
GREY = "#6B6257"

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF = FONT_DIR / "DejaVuSerif-Bold.ttf"
BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
REGULAR = FONT_DIR / "DejaVuSans.ttf"


@lru_cache(maxsize=None)
def font(path, size):
    if not path.is_file():
        raise FileNotFoundError(path)
    return ImageFont.truetype(path, size)


def bounds(face, text):
    left, top, right, bottom = face.getbbox(text)
    return min(left, 0), top, max(right, face.getlength(text)), bottom


def wrap(text, face, width):
    lines = []
    for paragraph in text.splitlines():
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            left, _, right, _ = bounds(face, candidate)
            if line and right - left > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    return lines


def fit(text, path, size, width, max_lines, min_size=None):
    min_size = size if min_size is None else min_size
    for trial in range(size, min_size - 1, -1):
        face = font(path, trial)
        lines = wrap(text, face, width)
        if len(lines) <= max_lines and all(
            right - left <= width
            for left, _, right, _ in (bounds(face, line) for line in lines)
        ):
            return face, lines
    raise ValueError(f"Text does not fit in {max_lines} lines: {text}")


def block_height(face, lines, leading):
    _, top, _, _ = face.getbbox(lines[0])
    _, _, _, bottom = face.getbbox(lines[-1])
    return (len(lines) - 1) * leading + bottom - top


def draw_block(draw, box, face, lines, leading, color, *, center=False):
    x, y, width, height = box
    first_top = face.getbbox(lines[0])[1]
    for index, line in enumerate(lines):
        left, top, right, bottom = bounds(face, line)
        line_width = right - left
        line_y = index * leading - first_top
        if line_width > width or line_y + top < 0 or line_y + bottom > height:
            raise ValueError(f"Text overflows its box: {line}")
        offset = int((width - line_width) // 2) if center else 0
        draw.text((x + offset - left, y + line_y), line, font=face, fill=color)


def label(draw, box, text, path, size, color, *, center=True):
    x, y, width, height = box
    face, lines = fit(text, path, size, width, 1)
    padding = (height - block_height(face, lines, size)) // 2
    draw_block(draw, (x, y + padding, width, height - padding),
               face, lines, size, color, center=center)


def star(draw, x, y, radius, color):
    points = []
    for index in range(10):
        angle = -pi / 2 + index * pi / 5
        distance = radius if index % 2 == 0 else radius * 0.382
        points.append((round(x + distance * cos(angle)), round(y + distance * sin(angle))))
    draw.polygon(points, fill=color)


def apec(draw):
    # Each flag has a 72 × 48 field above a four-pixel pole.
    for x in (49, 139, 229):
        draw.rectangle((x, 204, x + 3, 339), fill=INK)
        draw.ellipse((x - 2, 199, x + 5, 206), fill=INK)

    for stripe in range(7):
        top = 210 + stripe * 48 // 7
        bottom = 210 + (stripe + 1) * 48 // 7 - 1
        draw.rectangle((53, top, 124, bottom), fill=RED if stripe % 2 == 0 else WHITE)
    draw.rectangle((53, 210, 82, 236), fill=BLUE)
    for y in (215, 223, 231):
        for x in (59, 67, 75):
            star(draw, x, y, 2.4, WHITE)

    draw.rectangle((143, 210, 214, 257), fill=RED)
    star(draw, 162, 228, 13, GOLD)

    for index, color in enumerate((WHITE, BLUE, RED)):
        y = 210 + index * 16
        draw.rectangle((233, y, 304, y + 15), fill=color)

    draw.pieslice((48, 308, 304, 372), 180, 360, fill=INK)
    draw.rectangle((48, 340, 304, 368), fill=INK)
    draw.rectangle((76, 369, 276, 376), fill=RED)
    label(draw, (32, 386, 288, 33), "APEC · SHENZHEN", BOLD, 18, INK)


def eu_icon(draw):
    draw.rounded_rectangle((5, 10, 82, 87), radius=12, fill=BLUE)
    for index in range(12):
        angle = index * pi / 6
        star(draw, 43.5 + 25 * sin(angle), 48.5 - 25 * cos(angle), 4, GOLD)

    draw.polygon([(94, 46), (117, 68), (122, 62), (129, 83),
                  (107, 78), (112, 73), (88, 52)], fill=INK)
    draw.rounded_rectangle((45, 91, 145, 136), radius=5, fill=PAPER, outline=INK, width=3)
    draw.rounded_rectangle((51, 97, 139, 130), radius=3, outline=BLUE, width=2)
    label(draw, (53, 98, 85, 31), "EUR 45B", BOLD, 16, BLUE)


def iran_icon(draw):
    for x, y in ((27, 28), (123, 28), (39, 66), (111, 66)):
        draw.line((75, 46, x, y), fill=INK, width=7)
        draw.ellipse((x - 15, y - 6, x + 15, y + 6), outline=INK, width=3)
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=INK)
    draw.rounded_rectangle((56, 37, 94, 55), radius=7, fill=INK)

    draw.ellipse((52, 88, 98, 134), outline=RED, width=4)
    draw.line((75, 81, 75, 98), fill=RED, width=3)
    draw.line((75, 124, 75, 141), fill=RED, width=3)
    draw.line((45, 111, 62, 111), fill=RED, width=3)
    draw.line((88, 111, 105, 111), fill=RED, width=3)
    draw.ellipse((72, 108, 78, 114), fill=RED)


def voyager_icon(draw):
    # Dashed trajectory from Earth to the probe.
    for angle in range(202, 326, 13):
        draw.arc((10, 44, 151, 132), angle, angle + 7, fill=BLUE, width=3)
    draw.ellipse((6, 65, 24, 83), fill=BLUE)
    draw.polygon([(8, 70), (15, 66), (19, 71), (15, 74), (11, 74)], fill=WHITE)

    draw.polygon([(96, 77), (108, 64), (126, 81), (114, 94)], fill=BLUE)
    draw.line((115, 82, 141, 106), fill=INK, width=4)
    draw.ellipse((138, 103, 145, 110), fill=GOLD)
    draw.line((100, 83, 88, 104), fill=INK, width=3)
    draw.line((105, 72, 83, 54), fill=INK, width=3)
    draw.ellipse((79, 50, 87, 58), fill=GOLD)
    draw.arc((69, 35, 115, 80), 315, 135, fill=INK, width=5)

    label(draw, (8, 112, 134, 30), "26 BN KM", BOLD, 18, BLUE)


def border_icon(draw):
    for y in range(22, 130, 13):
        draw.line((74, y, 74, y + 6), fill=GREY, width=3)

    for facing_right, color in ((True, BLUE), (False, RED)):
        def mirror(x):
            return x if facing_right else 149 - x

        draw.polygon([(mirror(x), y) for x, y in
                      ((7, 78), (43, 78), (59, 83), (54, 95), (14, 95))], fill=color)
        draw.polygon([(mirror(x), y) for x, y in
                      ((16, 80), (20, 68), (38, 68), (45, 73), (45, 80))], fill=color)
        draw.line((mirror(39), 73, mirror(66), 73), fill=color, width=5)
        draw.rounded_rectangle((min(mirror(10), mirror(57)), 88,
                                max(mirror(10), mirror(57)), 103), radius=7, fill=INK)
        for x in (18, 28, 38, 48):
            draw.ellipse((mirror(x) - 3, 92, mirror(x) + 3, 98), fill=PAPER)


def lead(draw):
    draw.line((32, 170, 991, 170), fill=INK, width=1)
    draw.line((32, 440, 991, 440), fill=INK, width=1)
    apec(draw)

    headline = "XI AND PUTIN MEET\nAS APEC SETS UP\nTRUMP-XI-PUTIN SUMMIT"
    caption = ("Historic first US-China-Russia trilateral set for\n"
               "Thursday in Shenzhen; Xi spoke against protectionism\n"
               "as the leaders gathered.")
    face, lines = fit(headline, BOLD, 40, 648, 3)
    draw_block(draw, (344, 198, 648, 120), face, lines, 43, INK)
    face, lines = fit(caption, REGULAR, 22, 648, 3)
    draw_block(draw, (344, 337, 648, 78), face, lines, 26, GREY)


def tile(img, draw, x, y, headline, caption, icon):
    draw.rectangle((x, y, x + 471, y + 221), fill=WHITE, outline=INK, width=2)
    icon_image = Image.new("RGB", (150, 150), WHITE)
    icon(ImageDraw.Draw(icon_image))
    img.paste(icon_image, (x + 12, y + 36))

    width = 294
    head_face, head_lines = fit(headline, BOLD, 27, width, 3, min_size=24)
    body_face, body_lines = fit(caption, REGULAR, 19, width, 3)
    head_leading = head_face.size + 3
    body_leading = 24
    head_height = block_height(head_face, head_lines, head_leading)
    body_height = block_height(body_face, body_lines, body_leading)
    gap = 14
    top = y + (222 - head_height - gap - body_height) // 2
    draw_block(draw, (x + 166, top, width, head_height),
               head_face, head_lines, head_leading, INK)
    draw_block(draw, (x + 166, top + head_height + gap, width, body_height),
               body_face, body_lines, body_leading, GREY)


def ticker(draw):
    draw.rectangle((0, 932, 1023, 1003), fill=INK)
    label(draw, (32, 932, 145, 72), "ALSO TODAY", BOLD, 20, RED, center=False)
    lines = [
        "Jeffries nears historic US House speakership · Waymo pulls robotaxis off US highways",
        "Gold below $3,800, a year-plus low · Deutsche Bank probed over 15M-file leak",
    ]
    for index, text in enumerate(lines):
        face, wrapped = fit(text, REGULAR, 20, 807, 1, min_size=18)
        draw_block(draw, (185, 943 + index * 25, 807, 24), face, wrapped, 25, WHITE)


def main():
    img = Image.new("RGB", (1024, 1024), PAPER)
    draw = ImageDraw.Draw(img)

    label(draw, (64, 20, 896, 72), "THE WORLD TODAY", SERIF, 62, INK)
    draw.line((64, 95, 959, 95), fill=INK, width=2)
    draw.line((64, 100, 959, 100), fill=INK, width=1)
    label(draw, (32, 112, 960, 44), "WEDNESDAY · 18 NOVEMBER 2026", BOLD, 34, RED)
    lead(draw)

    tile(img, draw, 32, 456, "EU PROPOSES EUR 45BN LOAN FOR UKRAINE",
         "Von der Leyen: Kyiv repays only after Russia pays war reparations.", eu_icon)
    tile(img, draw, 520, 456, "IRAN STRIKES KUWAIT AND BAHRAIN",
         "Retaliation for a US strike on Qeshm Island; Bahrain says it intercepted Iranian attacks.",
         iran_icon)
    tile(img, draw, 32, 694, "VOYAGER 1 REACHES ONE LIGHT-DAY FROM EARTH",
         "First spacecraft 26 billion km from home, 49 years after launch.", voyager_icon)
    tile(img, draw, 520, 694, "ETHIOPIA AND ERITREA MASS FORCES ON BORDER",
         "Monitors warn the rival armies are within striking distance.", border_icon)
    ticker(draw)

    output = Path(__file__).resolve().with_name("entry.png")
    img.save(output, optimize=True)
    print(f"Wrote {output.name} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
