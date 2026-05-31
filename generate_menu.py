#!/usr/bin/env python3
"""Generate a Khor Bros menu JPG from chosen twist flavors."""

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from tui import checkbox

def _resource_root():
    # PyInstaller --onefile extracts bundled data to sys._MEIPASS at runtime.
    return Path(getattr(sys, "_MEIPASS", Path(__file__).parent))


def _output_root():
    # Write next to the executable when frozen so the user can find the output.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


REPO = _resource_root()
COMBOS_FILE = REPO / "twist_combinations.md"
BASE_IMAGE = REPO / "images" / "DE.RM.VCVO2025.jpg"
OUT_DIR = _output_root() / "generated"

# Pixel regions in the 12113x6863 base image, established by inspection.
BG_COLOR = (0, 172, 236)  # sampled from base image (close to spec #00A3E0)
TEXT_COLOR = (255, 255, 255)
TWIST_BANNER_X = (7073, 11843)
SINGLE_BANNER_X = (7222, 11992)
TWIST_TEXT_Y = (720, 3540)
SINGLE_TEXT_Y = (4250, 6150)
PAINT_X = (6800, 12113)
TWIST_BANNER_Y = (34, 465)
SINGLE_BANNER_Y = (3596, 4027)

FONT_PATH = str(REPO / "fonts" / "BebasNeue.otf")
LETTER_SPACING_EM = 0.01  # tight tracking, standard for condensed faces
SHADOW_COLOR = (0, 15, 35)  # near-black navy, hard-edged
SHADOW_OFFSET_EM = 0.08  # offset as fraction of font size


def parse_combos(md_path):
    """Return ordered list of unique twist combinations from the markdown file."""
    text = md_path.read_text()
    section = text.split("## Unique Twist Combinations", 1)[1].split("##", 1)[0]
    combos = []
    for line in section.splitlines():
        m = re.match(r"\s*\d+\.\s+(.+)", line)
        if m:
            combos.append(m.group(1).strip())
    return combos


def single_flavors(selected_combos):
    """Extract unique single flavors from twist combos (preserving first-seen order)."""
    seen = []
    for combo in selected_combos:
        for part in combo.split("&"):
            f = part.strip()
            if f and f not in seen:
                seen.append(f)
    return seen


_MEASURE_DRAW = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def _tracked_width(text, font, tracking):
    """Width of `text` rendered with `tracking` px of extra space between chars."""
    if not text:
        return 0
    w = sum(_MEASURE_DRAW.textbbox((0, 0), ch, font=font)[2] for ch in text)
    return w + tracking * (len(text) - 1)


def _draw_tracked(draw, xy, text, font, fill, tracking, shadow_offset=0, shadow_fill=None):
    x, y = xy
    for ch in text:
        if shadow_offset and shadow_fill is not None:
            draw.text((x + shadow_offset, y + shadow_offset), ch, font=font, fill=shadow_fill)
        draw.text((x, y), ch, font=font, fill=fill)
        x += _MEASURE_DRAW.textbbox((0, 0), ch, font=font)[2] + tracking


def fit_font_single_column(lines, max_w, max_h, line_gap_frac=0.35, max_size=380):
    """Largest font where every line fits in max_w and stacked lines fit in max_h."""
    for size in range(max_size, 30, -2):
        font = ImageFont.truetype(FONT_PATH, size)
        tracking = size * LETTER_SPACING_EM
        widest = max(_tracked_width(ln, font, tracking) for ln in lines)
        if widest > max_w:
            continue
        line_h = size
        total = len(lines) * line_h + (len(lines) - 1) * int(line_h * line_gap_frac)
        if total <= max_h:
            return font, line_h, int(line_h * line_gap_frac), tracking
    font = ImageFont.truetype(FONT_PATH, 30)
    return font, 30, 10, 30 * LETTER_SPACING_EM


def fit_font_grid(items, cols, max_w, max_h, col_gap_frac=0.3, line_gap_frac=0.35, max_size=380):
    """Largest font where items arranged in `cols` columns fit width/height."""
    rows = (len(items) + cols - 1) // cols
    for size in range(max_size, 30, -2):
        font = ImageFont.truetype(FONT_PATH, size)
        tracking = size * LETTER_SPACING_EM
        col_w = max(_tracked_width(it, font, tracking) for it in items)
        col_gap = int(col_w * col_gap_frac)
        total_w = cols * col_w + (cols - 1) * col_gap
        if total_w > max_w:
            continue
        line_h = size
        total_h = rows * line_h + (rows - 1) * int(line_h * line_gap_frac)
        if total_h <= max_h:
            return font, col_w, col_gap, line_h, int(line_h * line_gap_frac), tracking
    font = ImageFont.truetype(FONT_PATH, 30)
    return font, 200, 60, 30, 10, 30 * LETTER_SPACING_EM


def render_centered_lines(draw, lines, font, line_h, line_gap, tracking, x_range, y_range, align="center"):
    shadow = line_h * SHADOW_OFFSET_EM
    n = len(lines)
    total_h = n * line_h + (n - 1) * line_gap
    cx = (x_range[0] + x_range[1]) / 2
    if align == "top":
        start_y = y_range[0]
    else:
        start_y = (y_range[0] + y_range[1]) / 2 - total_h / 2
    for i, ln in enumerate(lines):
        w = _tracked_width(ln, font, tracking)
        top = _MEASURE_DRAW.textbbox((0, 0), ln[0] if ln else "M", font=font)[1]
        _draw_tracked(draw, (cx - w / 2, start_y + i * (line_h + line_gap) - top),
                      ln, font, TEXT_COLOR, tracking, shadow, SHADOW_COLOR)


def render_grid(draw, items, cols, font, col_w, col_gap, line_h, line_gap, tracking, x_range, y_range, align="center"):
    shadow = line_h * SHADOW_OFFSET_EM
    rows = (len(items) + cols - 1) // cols
    total_w = cols * col_w + (cols - 1) * col_gap
    total_h = rows * line_h + (rows - 1) * line_gap
    cx = (x_range[0] + x_range[1]) / 2
    start_x = cx - total_w / 2
    if align == "top":
        start_y = y_range[0]
    else:
        start_y = (y_range[0] + y_range[1]) / 2 - total_h / 2
    for i, item in enumerate(items):
        r, c = divmod(i, cols)
        col_center_x = start_x + c * (col_w + col_gap) + col_w / 2
        w = _tracked_width(item, font, tracking)
        top = _MEASURE_DRAW.textbbox((0, 0), item[0] if item else "M", font=font)[1]
        y = start_y + r * (line_h + line_gap) - top
        _draw_tracked(draw, (col_center_x - w / 2, y), item, font, TEXT_COLOR, tracking,
                      shadow, SHADOW_COLOR)


def cols_for(n):
    if n <= 4:
        return 1
    return 2


def generate(selected_combos, out_path):
    img = Image.open(BASE_IMAGE).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Paint blue over the two text regions (preserving banners).
    draw.rectangle([PAINT_X[0], TWIST_BANNER_Y[1] + 1, PAINT_X[1], SINGLE_BANNER_Y[0] - 1], fill=BG_COLOR)
    draw.rectangle([PAINT_X[0], SINGLE_BANNER_Y[1] + 1, PAINT_X[1], 6200], fill=BG_COLOR)

    # Twist flavors.
    twist_lines = [c.upper() for c in selected_combos]
    tw_max_w = TWIST_BANNER_X[1] - TWIST_BANNER_X[0] - 200
    tw_max_h = TWIST_TEXT_Y[1] - TWIST_TEXT_Y[0]
    font, lh, lg, tracking = fit_font_single_column(twist_lines, tw_max_w, tw_max_h, line_gap_frac=0.7)
    render_centered_lines(draw, twist_lines, font, lh, lg, tracking, TWIST_BANNER_X, TWIST_TEXT_Y, align="top")

    # Single flavors.
    singles = [s.upper() for s in single_flavors(selected_combos)]
    cols = cols_for(len(singles))
    s_max_w = SINGLE_BANNER_X[1] - SINGLE_BANNER_X[0] - 200
    s_max_h = SINGLE_TEXT_Y[1] - SINGLE_TEXT_Y[0]
    font, col_w, col_gap, lh, lg, tracking = fit_font_grid(singles, cols, s_max_w, s_max_h)
    render_grid(draw, singles, cols, font, col_w, col_gap, lh, lg, tracking, SINGLE_BANNER_X, SINGLE_TEXT_Y, align="top")

    OUT_DIR.mkdir(exist_ok=True)
    img.save(out_path, quality=92)


def short_code(combo):
    """e.g. 'Vanilla & Chocolate' -> 'VC'; 'Peanut Butter & Chocolate' -> 'PbC'."""
    parts = [p.strip() for p in combo.split("&")]
    out = ""
    for p in parts:
        words = p.split()
        if len(words) == 1:
            out += words[0][0].upper()
        else:
            out += words[0][0].upper() + "".join(w[0].lower() for w in words[1:])
    return out


def main():
    combos = parse_combos(COMBOS_FILE)
    selected = checkbox("Choose twist flavors:", combos)
    if not selected:
        print("No flavors selected. Exiting.")
        sys.exit(0)

    code = "".join(short_code(c) for c in selected)
    out = OUT_DIR / f"DE.RM.{code}2025.jpg"
    generate(selected, out)
    print(f"\nWrote {out}")
    print(f"  Twists: {len(selected)}")
    print(f"  Singles: {len(single_flavors(selected))}")


if __name__ == "__main__":
    main()
