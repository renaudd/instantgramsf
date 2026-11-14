#!/usr/bin/env python3
"""
Render a rich top-down bird's-eye view of an SUV interior for the InstantGram SF player mat:
- Saved to public/assets/icons/suv_mat_board_bg.jpg and public/assets/rome_art/suv_wagon_board_bg.jpg
- Outer SUV body/roof rails/bumpers push right up against all 4 edges of the canvas.
- Left 25% column: Front cabin with curved windshield, dashboard, steering wheel, center console, and 2 leather bucket seats (Henchmen slots).
- Right 75% area: Spacious rear cargo bay with a 2x3 grid of recessed heavy-duty rubber cargo bays (Goods slots).
"""

import os
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render_suv_mat(w: int = 1600, h: int = 920) -> Image.Image:
    # Base canvas: deep night asphalt at very corners
    img = Image.new("RGB", (w, h), (16, 8, 28))
    draw = ImageDraw.Draw(img)

    # 1. Outer SUV Body Shell (pushes right up to the limits of the printable space: 2px margin)
    draw.rounded_rectangle((2, 2, w - 3, h - 3), radius=54, fill=(48, 42, 64), outline=(145, 132, 175), width=4)
    # Metallic body paint highlight bevel along top & bottom fenders
    draw.rounded_rectangle((8, 8, w - 9, h - 9), radius=48, fill=(62, 54, 82), outline=(185, 165, 218), width=3)

    # Side Mirrors sticking out near A-pillar (x ~ 115)
    draw.polygon([(95, 10), (150, 0), (166, 16), (112, 24)], fill=(78, 68, 102), outline=(195, 180, 225), width=2)
    draw.polygon([(95, h - 10), (150, h - 1), (166, h - 16), (112, h - 24)], fill=(78, 68, 102), outline=(195, 180, 225), width=2)

    # Bright xenon headlight lenses at front-left corners & ruby LED taillight bars at rear-right corners
    draw.rounded_rectangle((3, 42, 22, 205), radius=7, fill=(225, 245, 255), outline=(130, 205, 255), width=3)
    draw.rounded_rectangle((3, h - 205, 22, h - 42), radius=7, fill=(225, 245, 255), outline=(130, 205, 255), width=3)
    draw.rounded_rectangle((w - 22, 48, w - 3, 220), radius=6, fill=(255, 42, 95), outline=(255, 150, 180), width=3)
    draw.rounded_rectangle((w - 22, h - 220, w - 3, h - 48), radius=6, fill=(255, 42, 95), outline=(255, 150, 180), width=3)

    # Tinted Side Windows along top & bottom edges of the cabin (with B, C, D pillars)
    win_ranges = [(130, 425), (450, 980), (1005, 1520)]
    for x0, x1 in win_ranges:
        draw.polygon(
            [(x0, 12), (x1, 12), (x1 - 12, 40), (x0 + 12, 40)],
            fill=(32, 52, 78),
            outline=(135, 165, 205),
            width=2,
        )
        draw.polygon(
            [(x0, h - 12), (x1, h - 12), (x1 - 12, h - 40), (x0 + 12, h - 40)],
            fill=(32, 52, 78),
            outline=(135, 165, 205),
            width=2,
        )

    # Chrome Roof Rails + Crossbar Mounts running along top and bottom edges
    draw.rounded_rectangle((145, 20, w - 65, 30), radius=5, fill=(205, 202, 220), outline=(90, 84, 110), width=2)
    draw.rounded_rectangle((145, h - 30, w - 65, h - 20), radius=5, fill=(205, 202, 220), outline=(90, 84, 110), width=2)

    # 2. Inner SUV Cabin Floor & Trim (fills almost the entire mat: x=22..w-22, y=40..h-40)
    ix0, iy0, ix1, iy1 = 22, 40, w - 22, h - 40
    draw.rounded_rectangle((ix0, iy0, ix1, iy1), radius=34, fill=(32, 28, 42), outline=(120, 108, 150), width=3)

    # Hot-pink / neon-magenta LED ambient interior trim strip around the cabin perimeter
    draw.rounded_rectangle((ix0 + 4, iy0 + 4, ix1 - 4, iy1 - 4), radius=30, outline=(255, 45, 155), width=2)

    # 3. Curved Front Windshield & Dashboard Console on far left (x=28..100)
    # Swept windshield glass
    draw.polygon(
        [(28, iy0 + 26), (62, iy0 + 10), (62, iy1 - 10), (28, iy1 - 26)],
        fill=(38, 64, 94),
        outline=(135, 175, 215),
        width=2,
    )
    # Windshield reflection lines
    draw.line((36, iy0 + 60, 54, iy0 + 150), fill=(110, 155, 200), width=2)
    draw.line((36, iy1 - 150, 54, iy1 - 60), fill=(110, 155, 200), width=2)

    # Dashboard pod
    dash_x0, dash_x1 = 56, 104
    draw.rounded_rectangle((dash_x0, iy0 + 12, dash_x1, iy1 - 12), radius=18, fill=(52, 46, 68), outline=(130, 118, 162), width=2)
    mid_y = h // 2
    # Center touchscreen display on dashboard
    draw.rounded_rectangle((dash_x0 + 10, mid_y - 62, dash_x1 - 6, mid_y + 62), radius=6, fill=(20, 32, 54), outline=(255, 65, 165), width=2)
    draw.line((dash_x0 + 16, mid_y - 38, dash_x1 - 12, mid_y - 10), fill=(80, 210, 255), width=2)
    draw.line((dash_x0 + 16, mid_y + 20, dash_x1 - 14, mid_y + 42), fill=(255, 90, 180), width=2)

    # Steering wheel in front of driver seat (Top-Left Seat)
    sw_cy = int(iy0 + (iy1 - iy0) * 0.27)
    draw.ellipse((dash_x1 - 18, sw_cy - 58, dash_x1 + 32, sw_cy + 58), outline=(170, 160, 195), width=10)
    draw.ellipse((dash_x1 - 2, sw_cy - 18, dash_x1 + 16, sw_cy + 18), fill=(95, 88, 118), outline=(170, 160, 195), width=2)
    draw.line((dash_x1 + 7, sw_cy - 54, dash_x1 + 7, sw_cy + 54), fill=(140, 130, 168), width=5)
    draw.line((dash_x1 - 14, sw_cy, dash_x1 + 28, sw_cy), fill=(140, 130, 168), width=6)

    # 4. Left Zone (Henchmen Bucket Seats — Left 25% of interior: x=108..412)
    seat_x0, seat_x1 = 108, 412
    # Center console with gear shifter & dual cupholders between the two seats
    con_y0, con_y1 = mid_y - 24, mid_y + 24
    draw.rounded_rectangle((dash_x1 - 4, con_y0, seat_x1 - 8, con_y1), radius=10, fill=(60, 52, 78), outline=(138, 124, 170), width=2)
    draw.rounded_rectangle((130, mid_y - 14, 182, mid_y + 14), radius=5, fill=(34, 28, 46), outline=(155, 140, 188), width=2)
    draw.ellipse((212, mid_y - 13, 238, mid_y + 13), fill=(22, 18, 30), outline=(150, 138, 180), width=2)
    draw.ellipse((250, mid_y - 13, 276, mid_y + 13), fill=(22, 18, 30), outline=(150, 138, 180), width=2)
    # Padded leather center armrest
    draw.rounded_rectangle((292, mid_y - 16, seat_x1 - 16, mid_y + 16), radius=6, fill=(78, 66, 98), outline=(145, 130, 178), width=2)

    # Helper to draw a top-down quilted leather SUV seat
    def draw_leather_seat(sy0: int, sy1: int, is_top: bool):
        # Outer leather seat shell
        draw.rounded_rectangle((seat_x0, sy0, seat_x1, sy1), radius=26, fill=(68, 56, 88), outline=(155, 138, 190), width=3)
        # Headrest on the left side of the seat (facing forward/right or backrest on left)
        hr_w = 48
        draw.rounded_rectangle((seat_x0 + 8, sy0 + 34, seat_x0 + 8 + hr_w, sy1 - 34), radius=14, fill=(92, 76, 116), outline=(185, 168, 220), width=2)
        # Chrome headrest posts
        draw.line((seat_x0 + 56, sy0 + 75, seat_x0 + 66, sy0 + 75), fill=(210, 210, 225), width=4)
        draw.line((seat_x0 + 56, sy1 - 75, seat_x0 + 66, sy1 - 75), fill=(210, 210, 225), width=4)
        # Seat cushion & quilted ribs
        c_x0, c_y0, c_x1, c_y1 = seat_x0 + 66, sy0 + 24, seat_x1 - 16, sy1 - 24
        draw.rounded_rectangle((c_x0, c_y0, c_x1, c_y1), radius=16, fill=(48, 40, 64), outline=(122, 108, 152), width=2)
        for rx in range(c_x0 + 30, c_x1 - 10, 34):
            draw.line((rx, c_y0 + 6, rx, c_y1 - 6), fill=(76, 64, 98), width=2)
        for ry in range(c_y0 + 30, c_y1 - 10, 34):
            draw.line((c_x0 + 6, ry, c_x1 - 6, ry), fill=(76, 64, 98), width=2)
        # Side bolsters (top & bottom of seat)
        draw.rounded_rectangle((seat_x0 + 60, sy0 + 6, seat_x1 - 12, sy0 + 24), radius=8, fill=(82, 68, 106), outline=(140, 124, 174), width=2)
        draw.rounded_rectangle((seat_x0 + 60, sy1 - 24, seat_x1 - 12, sy1 - 6), radius=8, fill=(82, 68, 106), outline=(140, 124, 174), width=2)
        # Seatbelt strap across bolster
        if is_top:
            draw.line((seat_x0 + 70, sy0 + 10, seat_x0 + 165, c_y1 - 12), fill=(195, 45, 115), width=5)
        else:
            draw.line((seat_x0 + 70, sy1 - 10, seat_x0 + 165, c_y0 + 12), fill=(195, 45, 115), width=5)

    draw_leather_seat(iy0 + 18, mid_y - 28, True)
    draw_leather_seat(mid_y + 28, iy1 - 18, False)

    # Structural B-pillar partition bar between Front Cabin (Henchmen) and Rear Cargo Bay (Goods)
    div_x = 424
    draw.line((div_x, iy0 + 6, div_x, iy1 - 6), fill=(155, 138, 192), width=6)

    # 5. Right Zone (Rear SUV Cargo Trunk — Right 75% of interior: x=438..ix1-20)
    cargo_x0, cargo_y0, cargo_x1, cargo_y1 = 438, iy0 + 14, ix1 - 22, iy1 - 14
    draw.rounded_rectangle((cargo_x0, cargo_y0, cargo_x1, cargo_y1), radius=22, fill=(38, 34, 50), outline=(142, 126, 178), width=3)

    # Wheel well arches along top and bottom of cargo bay
    draw.rounded_rectangle((cargo_x0 + 360, iy0 + 4, cargo_x0 + 660, iy0 + 18), radius=8, fill=(74, 64, 96), outline=(155, 140, 190), width=2)
    draw.rounded_rectangle((cargo_x0 + 360, iy1 - 18, cargo_x0 + 660, iy1 - 4), radius=8, fill=(74, 64, 96), outline=(155, 140, 190), width=2)

    # Horizontal ribbed rubber trunk mat texture across the cargo floor
    for ry in range(cargo_y0 + 12, cargo_y1 - 10, 16):
        draw.line((cargo_x0 + 10, ry, cargo_x1 - 10, ry), fill=(48, 42, 62), width=3)

    # 2 rows x 3 columns of recessed cargo organizer bays inside the SUV trunk
    pad_x, pad_y = 16, 16
    gap_x, gap_y = 14, 14
    bay_w = (cargo_x1 - cargo_x0 - 2 * pad_x - 2 * gap_x) // 3
    bay_h = (cargo_y1 - cargo_y0 - 2 * pad_y - gap_y) // 2

    for r in range(2):
        for c in range(3):
            bx0 = cargo_x0 + pad_x + c * (bay_w + gap_x)
            by0 = cargo_y0 + pad_y + r * (bay_h + gap_y)
            bx1 = bx0 + bay_w
            by1 = by0 + bay_h
            # Recessed cargo tray with metallic tie-down perimeter
            draw.rounded_rectangle((bx0, by0, bx1, by1), radius=14, fill=(26, 22, 36), outline=(118, 104, 152), width=3)
            # Inner aluminum cargo slide rails
            for rx in range(bx0 + 28, bx1 - 18, 38):
                draw.line((rx, by0 + 10, rx, by1 - 10), fill=(44, 38, 58), width=3)
            # Corner chrome tie-down D-rings
            for cx, cy in [(bx0 + 12, by0 + 12), (bx1 - 12, by0 + 12), (bx0 + 12, by1 - 12), (bx1 - 12, by1 - 12)]:
                draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(175, 165, 205), outline=(70, 60, 90), width=1)

    # Rear tailgate bumper & brushed aluminum scuff plate on the far right edge (x = ix1-18..w-6)
    draw.rounded_rectangle((ix1 - 18, iy0 + 44, w - 6, iy1 - 44), radius=8, fill=(92, 84, 114), outline=(185, 172, 215), width=2)
    for ry in range(iy0 + 62, iy1 - 58, 20):
        draw.line((ix1 - 14, ry, w - 10, ry), fill=(155, 145, 182), width=2)

    # Subtle overhead dome-light specular sheen
    arr = np.array(img, dtype=np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx - w * 0.52) / (w * 0.58)) ** 2 + ((yy - h * 0.5) / (h * 0.58)) ** 2)
    vignette = np.clip(1.10 - 0.18 * (dist ** 1.6), 0.85, 1.10)[:, :, None]
    arr = np.clip(arr * vignette, 0, 255).astype(np.uint8)
    out_img = Image.fromarray(arr)

    out_paths = [
        os.path.join(ROOT, "public/assets/icons/suv_mat_board_bg.jpg"),
        os.path.join(ROOT, "public/assets/rome_art/suv_wagon_board_bg.jpg"),
    ]
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        out_img.save(p, quality=93)
        print("Saved SUV mat to:", p)
    return out_img


if __name__ == "__main__":
    render_suv_mat()
