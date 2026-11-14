"""Generate the InstantGram SF icons (256x256 RGBA):
  - cash.png / chest.png              : Isometric cash stack extracted from encounter_criminals_wanted_final (Mission symbol)
  - cash_white.png                    : All-white status-bar version of the cash stack (for phone bezels & outcome bars)
  - laptop.png / deck.png             : Crisp open laptop icon (Deck symbol: [computer][cash] = top Mission Deck card)
  - laptop_white.png                  : All-white status-bar laptop icon
  - combat.png / pistol.png           : Crisp semi-automatic pistol icon (Attack / Combat symbol)
  - pistol_white.png                  : All-white status-bar pistol icon (for bottom-left bezel / outcome bar)
  - thumb_up_green.png / thumb_up.png : Large vibrant green thumbs-up (Friendly outcome)
  - thumb_up_red.png                  : Large vibrant red thumbs-up pointing UP (for bottom-right bezel; points down when rotated 180 deg)
  - thumb_down.png                    : Red thumbs-down (180-deg rotated for general UI)
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(ROOT, "public/assets/icons")
MOCKUP_DIR = os.path.join(ROOT, "public/assets/fp/mockups")
ARTIFACT_DIR = "/Users/rend/.gemini/antigravity/brain/fcf1e550-742e-4462-b29d-a619e90abf1e"


def extract_wanted_cash_icons():
    """Extract the isometric cash stack icon from encounter_criminals_wanted_final
    and produce both the standard (cash.png / chest.png) and all-white (cash_white.png) icons.
    """
    src_path = os.path.join(MOCKUP_DIR, "encounter_wanted_poster_1794554513357.jpg")
    if not os.path.exists(src_path):
        src_path = os.path.join(ARTIFACT_DIR, "enc_criminals_wanted_1794554990209.jpg")
    else:
        src_path = os.path.join(ARTIFACT_DIR, "enc_criminals_wanted_1794554990209.jpg")

    im_w = Image.open(src_path).convert("RGB")
    # Cash icon bounding box in enc_criminals_wanted_1794554990209.jpg is (720, 24, 822, 99)
    crop = im_w.crop((716, 18, 826, 102))
    # Upscale 4x for smooth anti-aliased processing
    up_w, up_h = 110 * 4, 84 * 4
    crop_up = crop.resize((up_w, up_h), Image.LANCZOS)
    gray = np.array(crop_up, dtype=np.float32).mean(axis=2)

    # Ink darkness in [0..1]: gray <= 65 is pure ink (1.0), gray >= 155 is paper (0.0)
    ink_strength = np.clip((155.0 - gray) / (155.0 - 55.0), 0.0, 1.0)

    # Determine the outer silhouette of the cash stack using flood fill from the borders
    binary_ink = (ink_strength > 0.32).astype(np.uint8) * 255
    # Close tiny 1px gaps along outer border if any
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(binary_ink, cv2.MORPH_CLOSE, kernel)

    # Flood-fill from corners on the inverted mask to find exterior paper
    inv = 255 - closed
    ff_mask = np.zeros((up_h + 2, up_w + 2), dtype=np.uint8)
    for sx, sy in [(0, 0), (up_w - 1, 0), (0, up_h - 1), (up_w - 1, up_h - 1)]:
        cv2.floodFill(inv, ff_mask, (sx, sy), 128)
    inside_silhouette = (inv != 128).astype(np.float32)
    inside_smooth = cv2.GaussianBlur(inside_silhouette, (5, 5), 1.0)

    # 1. Standard Cash Icon (dark ink lines + crisp white/warm-ivory bill interior so it pops on any color bar)
    rgba_std = np.zeros((up_h, up_w, 4), dtype=np.uint8)
    # Interior fill is bright bill-white (250, 250, 246), ink is deep charcoal-black (16, 18, 20)
    for c_idx, (ink_c, fill_c) in enumerate([(16, 250), (18, 250), (20, 245)]):
        val = ink_strength * ink_c + (1.0 - ink_strength) * fill_c
        rgba_std[:, :, c_idx] = np.clip(val, 0, 255).astype(np.uint8)
    alpha_std = np.clip(np.maximum(inside_smooth, ink_strength) * 255.0, 0, 255).astype(np.uint8)
    rgba_std[:, :, 3] = alpha_std

    # Place centered on a square 256x256 canvas with a subtle outer halo for contrast
    canvas_std = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    icon_std = Image.fromarray(rgba_std)
    target_w = 236
    target_h = int(round(up_h * (target_w / up_w)))
    icon_std_rs = icon_std.resize((target_w, target_h), Image.LANCZOS)
    ox = (256 - target_w) // 2
    oy = (256 - target_h) // 2
    canvas_std.paste(icon_std_rs, (ox, oy), icon_std_rs)

    # 2. All-White Cash Icon (white ink lines, transparent interior/exterior, for dark phone bezels & outcome bars)
    rgba_white = np.zeros((up_h, up_w, 4), dtype=np.uint8)
    rgba_white[:, :, 0] = 255
    rgba_white[:, :, 1] = 255
    rgba_white[:, :, 2] = 255
    # Boost ink_strength slightly so white strokes look bold and crisp at status-bar size
    white_alpha = np.clip((ink_strength ** 0.75) * 255.0, 0, 255).astype(np.uint8)
    rgba_white[:, :, 3] = white_alpha

    canvas_white = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    icon_white_rs = Image.fromarray(rgba_white).resize((target_w, target_h), Image.LANCZOS)
    canvas_white.paste(icon_white_rs, (ox, oy), icon_white_rs)

    return canvas_std, canvas_white


def draw_thumbs_up_icon(fill_main, fill_hi, fill_shade, rim_col=(255, 255, 255, 255)):
    """Render a bold, unmistakable thumbs-up icon at 1024x1024 and downsample to 256x256."""
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    for pass_idx in range(3):
        if pass_idx == 0:
            pad = 38
            col = (12, 16, 20, 245)
        elif pass_idx == 1:
            pad = 20
            col = rim_col
        else:
            pad = 0
            col = fill_main

        # Cuff (left vertical rounded rect)
        d.rounded_rectangle((84 - pad, 440 - pad, 276 + pad, 888 + pad), radius=48 + pad, fill=col)

        # Main palm + curled fingers block
        palm_poly = [
            (296 - pad, 450 - pad),
            (415, 290 - pad),
            (450, 118 - pad),
            (545 + pad, 86 - pad),
            (628 + pad, 135 - pad),
            (638 + pad, 255),
            (592 + pad, 398 - pad),
            (868 + pad, 398 - pad),
            (932 + pad, 462 - pad),
            (912 + pad, 565),
            (888 + pad, 675),
            (846 + pad, 785),
            (785 + pad, 882 + pad),
            (316 - pad, 882 + pad),
        ]
        d.polygon(palm_poly, fill=col)
        d.ellipse((442 - pad, 76 - pad, 636 + pad, 256 + pad), fill=col)
        d.ellipse((780 - pad, 398 - pad, 944 + pad, 558 + pad), fill=col)
        d.ellipse((760 - pad, 512 - pad, 926 + pad, 670 + pad), fill=col)
        d.ellipse((732 - pad, 626 - pad, 896 + pad, 782 + pad), fill=col)
        d.ellipse((695 - pad, 736 - pad, 854 + pad, 884 + pad), fill=col)

    d.ellipse((474, 104, 598, 224), fill=fill_hi)
    d.rounded_rectangle((560, 418, 892, 476), radius=24, fill=fill_hi)
    d.rounded_rectangle((112, 472, 248, 856), radius=28, fill=fill_shade)
    d.ellipse((150, 740, 214, 804), fill=rim_col)

    for gy in [546, 658, 768]:
        d.line((680, gy, 895, gy), fill=fill_shade, width=22)

    return im.resize((256, 256), Image.LANCZOS)


def draw_pistol_icon(all_white=False):
    """Render a crisp semi-automatic pistol icon (either full color for card face or all-white for bezel)."""
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if all_white:
        fg = (255, 255, 255, 255)
        cut = (0, 0, 0, 0)
        d.rounded_rectangle((110, 210, 920, 430), radius=36, fill=fg)
        d.rounded_rectangle((880, 248, 964, 392), radius=16, fill=fg)
        d.polygon([(145, 210), (195, 156), (235, 156), (235, 210)], fill=fg)
        d.polygon([(830, 210), (860, 164), (896, 164), (896, 210)], fill=fg)
        d.rounded_rectangle((220, 390, 790, 505), radius=24, fill=fg)
        grip_poly = [
            (155, 395),
            (425, 395),
            (325, 865),
            (110, 865),
        ]
        d.polygon(grip_poly, fill=fg)
        d.rounded_rectangle((96, 825, 345, 895), radius=22, fill=fg)
        d.pieslice((70, 340, 260, 490), 90, 260, fill=fg)
        d.rounded_rectangle((365, 480, 615, 675), radius=48, fill=fg)
        d.rounded_rectangle((412, 512, 568, 632), radius=28, fill=cut)
        d.arc((430, 505, 535, 625), start=300, end=110, fill=fg, width=34)
        d.rounded_rectangle((465, 248, 635, 320), radius=14, fill=cut)
        for sx in [210, 265, 320]:
            d.line((sx, 255, sx - 24, 385), fill=cut, width=24)
        return im.resize((256, 256), Image.LANCZOS)

    outline = (18, 22, 28, 255)
    steel_main = (76, 86, 102, 255)
    steel_hi = (148, 162, 184, 255)
    steel_dark = (42, 48, 58, 255)
    grip_col = (34, 36, 42, 255)

    for is_out in [True, False]:
        p = 28 if is_out else 0
        c_slide = outline if is_out else steel_main
        c_frame = outline if is_out else steel_dark
        c_grip = outline if is_out else grip_col

        d.polygon([(145 - p, 210), (195 - p, 148 - p), (242 + p, 148 - p), (242 + p, 210)], fill=c_slide)
        d.polygon([(825 - p, 210), (858 - p, 156 - p), (900 + p, 156 - p), (900 + p, 210)], fill=c_slide)
        d.rounded_rectangle((875 - p, 244 - p, 968 + p, 396 + p), radius=18 + p, fill=c_frame)
        d.rounded_rectangle((110 - p, 206 - p, 920 + p, 434 + p), radius=34 + p, fill=c_slide)
        d.rounded_rectangle((210 - p, 400 - p, 795 + p, 512 + p), radius=22 + p, fill=c_frame)
        d.rounded_rectangle((360 - p, 480 - p, 620 + p, 680 + p), radius=48 + p, fill=c_frame)
        grip_poly = [
            (150 - p, 400 - p),
            (430 + p, 400 - p),
            (330 + p, 865 + p),
            (105 - p, 865 + p),
        ]
        d.polygon(grip_poly, fill=c_grip)
        d.rounded_rectangle((92 - p, 825 - p, 350 + p, 898 + p), radius=22 + p, fill=c_frame)

    d.rounded_rectangle((416, 520, 566, 628), radius=24, fill=(0, 0, 0, 0))
    d.rounded_rectangle((410, 514, 572, 634), radius=28, outline=outline, width=18)
    d.arc((432, 505, 535, 625), start=300, end=110, fill=outline, width=36)

    d.rounded_rectangle((140, 226, 895, 290), radius=16, fill=steel_hi)
    d.rounded_rectangle((470, 246, 640, 332), radius=12, fill=(28, 32, 38, 255), outline=outline, width=12)
    for sx in [205, 260, 315]:
        d.line((sx, 265, sx - 24, 395), fill=outline, width=22)
    d.polygon([(185, 455), (370, 455), (295, 805), (140, 805)], fill=(54, 58, 68, 255), outline=outline, width=12)

    return im.resize((256, 256), Image.LANCZOS)


def draw_laptop_icon(all_white=False):
    """Render a crisp open laptop icon (Deck symbol [computer] across cards & UI)."""
    S = 1024
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    if all_white:
        fg = (255, 255, 255, 255)
        cut = (0, 0, 0, 0)
        d.rounded_rectangle((156, 168, 868, 668), radius=48, fill=fg)
        d.rounded_rectangle((224, 236, 800, 596), radius=20, fill=cut)
        d.rounded_rectangle((464, 224, 560, 262), radius=10, fill=fg)
        base_poly = [
            (64, 712),
            (960, 712),
            (920, 824),
            (104, 824),
        ]
        d.polygon(base_poly, fill=fg)
        d.rounded_rectangle((64, 696, 960, 764), radius=24, fill=fg)
        d.rounded_rectangle((96, 748, 928, 830), radius=32, fill=fg)
        d.rounded_rectangle((432, 696, 592, 738), radius=14, fill=cut)
        return im.resize((256, 256), Image.LANCZOS)

    outline = (18, 24, 34, 255)
    lid_col = (52, 62, 78, 255)
    screen_bg = (28, 138, 218, 255)
    screen_hi = (92, 198, 255, 255)
    base_top = (188, 198, 212, 255)
    base_front = (118, 130, 148, 255)

    d.rounded_rectangle((140, 148, 884, 668), radius=52, fill=outline)
    d.rounded_rectangle((168, 176, 856, 644), radius=36, fill=lid_col)
    d.rounded_rectangle((204, 212, 820, 604), radius=18, fill=screen_bg, outline=outline, width=12)
    d.polygon([(216, 224), (580, 224), (380, 592), (216, 592)], fill=screen_hi)

    d.polygon([(140, 636), (884, 636), (972, 772), (52, 772)], fill=base_top, outline=outline, width=28)
    d.polygon([(205, 666), (819, 666), (876, 742), (148, 742)], fill=(42, 50, 64, 255))
    d.rounded_rectangle((52, 756, 972, 852), radius=32, fill=base_front, outline=outline, width=28)
    d.rounded_rectangle((432, 760, 592, 804), radius=14, fill=outline)

    return im.resize((256, 256), Image.LANCZOS)


def main():
    # 1. Green Thumbs-Up (Friendly outcome)
    green_thumb = draw_thumbs_up_icon(
        fill_main=(34, 218, 92, 255),
        fill_hi=(115, 250, 155, 255),
        fill_shade=(18, 138, 52, 255),
        rim_col=(255, 255, 255, 255),
    )
    green_thumb.save(os.path.join(ICON_DIR, "thumb_up_green.png"))
    green_thumb.save(os.path.join(ICON_DIR, "thumb_up.png"))

    # 2. Red Thumbs-Up pointing UP (for bottom-right bezel; points DOWN when card is turned 180 deg upside-down)
    red_thumb_up = draw_thumbs_up_icon(
        fill_main=(238, 42, 52, 255),
        fill_hi=(255, 118, 124, 255),
        fill_shade=(152, 18, 26, 255),
        rim_col=(255, 255, 255, 255),
    )
    red_thumb_up.save(os.path.join(ICON_DIR, "thumb_up_red.png"))

    red_thumb_down = red_thumb_up.transpose(Image.ROTATE_180)
    red_thumb_down.save(os.path.join(ICON_DIR, "thumb_down.png"))

    # 3. Pistol icons (Attack / Combat symbol)
    pistol_col = draw_pistol_icon(all_white=False)
    pistol_col.save(os.path.join(ICON_DIR, "combat.png"))
    pistol_col.save(os.path.join(ICON_DIR, "pistol.png"))

    pistol_white = draw_pistol_icon(all_white=True)
    pistol_white.save(os.path.join(ICON_DIR, "pistol_white.png"))

    # 4. Cash Stack icons (Mission / Quest symbol across the board, replacing computer icon)
    cash_col, cash_white = extract_wanted_cash_icons()
    cash_col.save(os.path.join(ICON_DIR, "cash.png"))
    cash_col.save(os.path.join(ICON_DIR, "chest.png"))
    cash_white.save(os.path.join(ICON_DIR, "cash_white.png"))

    # 5. Computer / Laptop icons (Deck symbol: [computer][cash] = top Mission Deck card)
    laptop_col = draw_laptop_icon(all_white=False)
    laptop_col.save(os.path.join(ICON_DIR, "laptop.png"))
    laptop_col.save(os.path.join(ICON_DIR, "deck.png"))

    laptop_white = draw_laptop_icon(all_white=True)
    laptop_white.save(os.path.join(ICON_DIR, "laptop_white.png"))

    print("Successfully generated all InstantGram SF icons in", ICON_DIR)


if __name__ == "__main__":
    main()
