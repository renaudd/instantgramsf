"""Generate and composite the InstantGram SF Encounter Card Face mockups (900x1400, 2.25"x3.5").

Incorporates all final specifications:
  1. Larger Combat Formula ([pistol] : Formula with Rome Die [R] enclosed in a square):
     - Rendered with a 62-68px Pistol icon, 54-58px bold formula text, and a square-enclosed 'R'
       (Rome die icon) replacing "(R)".
  2. Cash Symbol ([cash]) as Job Symbol & Computer Icon ([computer]) as Job Deck Symbol:
     - Top-Right Outcome Bar / Bezel uses the isometric Cash Stack symbol (cash_white.png / cash.png).
     - Faction Posture Bar uses [computer][cash]?/!/!! for Top Job Deck offers/demands/threats,
       [cash]?/!/!! for the card's bespoke Job, ?/!/!! for the card's bespoke Deal/Demand,
       and [pistol] for Combat.
  3. Larger Gems on Non-Phone Screen Cards (Wanted Poster & Holographic Police ID):
     - Gems are tight-cropped to their non-transparent circle and rendered at >= the size of the
       preceding thumbs-up / thumbs-down icon (82px on Wanted Poster, 64px on Police ID), with
       a crisp black border and diagonal red slash on negative gems.
  4. Mechanically Aligned, Ultra-Concise Lower Box Assignments in Large Text:
     - Simple single-action Jobs (Sell, Delivery*, Hit, Special) and Deals/Demands (Sell*, Buy, Demand)
       rendered in large bold typography (34-42px) with no redundant faction/reward prose.
     - Price tables ONLY appear on Delivery Jobs (1-row +B Fence value table + good name, category,
       and SUV blocks) or Bespoke Good Sale Deals (2-row +B Retail / -B Wholesale table + good name,
       category, SUV blocks, and combat effect).
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREV_ARTIFACT_DIR = "/Users/rend/.gemini/antigravity/brain/fcf1e550-742e-4462-b29d-a619e90abf1e"
CURR_ARTIFACT_DIR = "/Users/rend/.gemini/antigravity/brain/035ce4f5-f07e-4b5c-a74e-237e70fe6f07"
MOCKUP_DIR = os.path.join(ROOT, "public/assets/fp/mockups")
ICON_DIR = os.path.join(ROOT, "public/assets/icons")

FONTS = "/System/Library/Fonts/Supplemental"
F_COND = os.path.join(FONTS, "DIN Condensed Bold.ttf")
F_BOLD = os.path.join(FONTS, "Arial Bold.ttf")
F_REG = os.path.join(FONTS, "Arial.ttf")
F_ITALIC = os.path.join(FONTS, "Arial Italic.ttf")
F_SERIF_B = os.path.join(FONTS, "Georgia Bold.ttf")
F_SERIF = os.path.join(FONTS, "Georgia.ttf")
F_SERIF_I = os.path.join(FONTS, "Georgia Italic.ttf")
F_MONO = os.path.join(FONTS, "Courier New Bold.ttf")
F_SYM = "/System/Library/Fonts/SFNS.ttf"
F_NUM = os.path.join(FONTS, "DIN Alternate Bold.ttf")

CARD_W, CARD_H = 900, 1400  # Exact 2.25" x 3.5" (9:14) at 400 DPI
SCARCITY = ["<<", "<", "=", ">", ">>"]
SCARCITY_COLORS = [(31, 122, 31), (31, 160, 60), (190, 170, 20), (214, 90, 40), (150, 20, 40)]

FACTION_BAR_STYLE = {
    "MAGA": {
        "bg": (228, 175, 182),
        "border": (155, 38, 52),
        "divider": (248, 232, 235),
        "text": (28, 14, 18),
    },
    "TECH": {
        "bg": (192, 224, 242),
        "border": (45, 118, 165),
        "divider": (240, 248, 255),
        "text": (14, 24, 34),
    },
    "DSA": {
        "bg": (165, 198, 238),
        "border": (38, 82, 168),
        "divider": (235, 244, 255),
        "text": (14, 20, 38),
    },
    "MS13": {
        "bg": (214, 194, 224),
        "border": (108, 52, 142),
        "divider": (246, 238, 252),
        "text": (24, 14, 32),
    },
    "ISIS": {
        "bg": (178, 218, 196),
        "border": (34, 118, 72),
        "divider": (236, 250, 242),
        "text": (12, 28, 18),
    },
}


def load_icon(name, size, tight=False):
    p = os.path.join(ICON_DIR, name)
    im = Image.open(p).convert("RGBA")
    if tight:
        bbox = im.getbbox()
        if bbox:
            im = im.crop(bbox)
    return im.resize((size, size), Image.LANCZOS)


def add_black_border_to_rgba(im, border_px=3, border_color=(12, 12, 16, 255)):
    """Add a crisp dark border around any RGBA icon so white/colored icons pop on light backgrounds."""
    w, h = im.size
    pad = border_px + 2
    out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    alpha = np.array(im.split()[3])
    padded_a = np.pad(alpha, pad, mode="constant", constant_values=0)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (border_px * 2 + 1, border_px * 2 + 1))
    dilated_a = cv2.dilate(padded_a, k, iterations=1)
    rim = np.zeros((h + 2 * pad, w + 2 * pad, 4), dtype=np.uint8)
    rim[:, :, 0] = border_color[0]
    rim[:, :, 1] = border_color[1]
    rim[:, :, 2] = border_color[2]
    rim[:, :, 3] = dilated_a
    rim_img = Image.fromarray(rim)
    out.paste(rim_img, (0, 0), rim_img)
    out.paste(im, (pad, pad), im)
    return out, pad


def paste_with_optional_border(canvas, im, x, y, black_border=False, border_px=3):
    if black_border:
        bordered, pad = add_black_border_to_rgba(im, border_px=border_px)
        canvas.paste(bordered, (int(x - pad), int(y - pad)), bordered)
    else:
        canvas.paste(im, (int(x), int(y)), im)


def draw_gem_with_slash(canvas, x, y, gem_name, is_negative=False, size=58, black_border=False, border_px=3):
    """Draw a tight-cropped faction gem at exact visual diameter `size`; if negative, draw a bold diagonal red slash."""
    gem_file = {
        "Ruby": "ruby.png",
        "Sapphire": "sapphire.png",
        "Diamond": "diamond.png",
        "Amethyst": "amethyst.png",
        "Emerald": "emerald.png",
    }[gem_name]
    gem = load_icon(gem_file, size, tight=True)
    if black_border:
        paste_with_optional_border(canvas, gem, x, y, black_border=True, border_px=border_px)
    else:
        halo = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hd.ellipse((2, 2, size + 5, size + 5), fill=(255, 255, 255, 55))
        halo = halo.filter(ImageFilter.GaussianBlur(2.0))
        canvas.paste(halo, (int(x - 4), int(y - 4)), halo)
        canvas.paste(gem, (int(x), int(y)), gem)
    if is_negative:
        d = ImageDraw.Draw(canvas)
        x0, y0 = int(x + 2), int(y + size - 2)
        x1, y1 = int(x + size - 2), int(y + 2)
        sw = max(6, int(size * 0.11))
        if black_border:
            d.line((x0, y0, x1, y1), fill=(12, 12, 16), width=sw + 8)
        d.line((x0, y0, x1, y1), fill=(255, 255, 255), width=sw + 4)
        d.line((x0, y0, x1, y1), fill=(235, 32, 38), width=sw)
    return int(x + size + 10)


def draw_rome_die_box(d, x, cy, box_sz, fill_col, bg_col=None):
    """Draw the Rome die icon: 'R' enclosed in a rounded square box."""
    half = box_sz // 2
    x0, y0, x1, y1 = int(x), int(cy - half), int(x + box_sz), int(cy - half + box_sz)
    bw = max(2, int(round(box_sz * 0.08)))
    if bg_col is not None:
        d.rounded_rectangle((x0, y0, x1, y1), radius=max(4, box_sz // 7), fill=bg_col, outline=fill_col, width=bw)
    else:
        d.rounded_rectangle((x0, y0, x1, y1), radius=max(4, box_sz // 7), outline=fill_col, width=bw)
    f_r = ImageFont.truetype(F_SERIF_B, int(box_sz * 0.72))
    bb = d.textbbox((0, 0), "R", font=f_r)
    rw, rh = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x0 + (box_sz - rw) / 2 - bb[0], y0 + (box_sz - rh) / 2 - bb[1]), "R", font=f_r, fill=fill_col)
    return box_sz


def draw_formula_with_rome_die(d, x, cy, formula_str, font, fill_col, die_bg=None):
    """Render a formula string (e.g. ': 2X(R) - 1') replacing '(R)' with the square-enclosed Rome die icon."""
    parts = formula_str.split("(R)")
    cur_x = int(x)
    box_sz = int(font.size * 0.96)
    for idx, part in enumerate(parts):
        if part:
            bb = d.textbbox((0, 0), part, font=font)
            pw, ph = bb[2] - bb[0], bb[3] - bb[1]
            d.text((cur_x, int(cy - ph / 2 - bb[1])), part, font=font, fill=fill_col)
            cur_x += pw + 4
        if idx < len(parts) - 1:
            cur_x += 2
            draw_rome_die_box(d, cur_x, cy, box_sz, fill_col, bg_col=die_bg)
            cur_x += box_sz + 4
    return cur_x


def draw_phone_bezel_outcomes(canvas, friendly_gems, friendly_reward, combat_loot, hostile_gems):
    """Draw Friendly & Hostile Outcomes + Job/Combat Rewards directly onto the top & bottom black phone bezels."""
    d = ImageDraw.Draw(canvas)

    top_cy = 70
    bot_cy = 1316

    # Paint a sleek dark smoked-glass bottom bezel strip (y=1278..1356) matching the top bezel surface
    d.rectangle((46, 1278, 854, 1354), fill=(16, 22, 26))
    d.line((46, 1278, 854, 1278), fill=(58, 70, 78), width=2)

    gem_sz = 58
    thumb_sz = 58
    status_icon_sz = 52

    f_colon = ImageFont.truetype(F_BOLD, 38)
    f_rew = ImageFont.truetype(F_SYM, 38)
    try:
        f_rew.set_variation_by_name("Bold")
    except Exception:
        pass

    # 1. TOP-LEFT BEZEL: Large Green Thumbs-Up + Large Tight-Cropped Friendly Faction Gems
    thumb_green = load_icon("thumb_up_green.png", thumb_sz)
    canvas.paste(thumb_green, (62, top_cy - thumb_sz // 2), thumb_green)
    d.text((64 + thumb_sz, top_cy - 22), ":", font=f_colon, fill=(255, 255, 255))

    gx = 80 + thumb_sz
    for g_name, g_sign in friendly_gems:
        gx = draw_gem_with_slash(canvas, gx, top_cy - gem_sz // 2, g_name, is_negative=(g_sign == "-"), size=gem_sz)

    # 2. TOP-RIGHT BEZEL: All-White Cash Stack Icon (cash_white.png) + All-White Job Reward
    cash_w = load_icon("cash_white.png", status_icon_sz)
    rew_txt = f":{friendly_reward}"
    bb = d.textbbox((0, 0), rew_txt, font=f_rew)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    rx = 836 - tw
    canvas.paste(cash_w, (rx - status_icon_sz - 4, top_cy - status_icon_sz // 2), cash_w)
    d.text((rx, top_cy - th // 2 - bb[1]), rew_txt, font=f_rew, fill=(255, 255, 255))

    # 3. BOTTOM-LEFT BEZEL: All-White Pistol Icon + All-White Combat Reward
    pistol_w = load_icon("pistol_white.png", status_icon_sz)
    canvas.paste(pistol_w, (62, bot_cy - status_icon_sz // 2), pistol_w)
    loot_txt = f":{combat_loot}"
    bb_l = d.textbbox((0, 0), loot_txt, font=f_rew)
    lh = bb_l[3] - bb_l[1]
    d.text((68 + status_icon_sz, bot_cy - lh // 2 - bb_l[1]), loot_txt, font=f_rew, fill=(255, 255, 255))

    # 4. BOTTOM-RIGHT BEZEL: Hostile Faction Gems (left) + Red Thumbs-Up Pointing UP (right)
    thumb_red_up = load_icon("thumb_up_red.png", thumb_sz)
    td_x = 838 - thumb_sz
    canvas.paste(thumb_red_up, (td_x, bot_cy - thumb_sz // 2), thumb_red_up)
    d.text((td_x - 16, bot_cy - 22), ":", font=f_colon, fill=(255, 255, 255))

    hx = td_x - 22
    for g_name, g_sign in reversed(hostile_gems):
        hx -= (gem_sz + 10)
        draw_gem_with_slash(canvas, hx, bot_cy - gem_sz // 2, g_name, is_negative=(g_sign == "-"), size=gem_sz)


def draw_tall_faction_interaction_bar(canvas, x0, y0, x1, y1, faction, tiers):
    """Draw the Faction Interaction Bar using:
      - [pistol] (combat.png) for COMBAT
      - [computer][cash]?/!/!! (laptop.png + cash.png) for DECK_CASH_? / DECK_CASH_! / DECK_CASH_!!
      - [cash]?/!/!! (cash.png) for CASH_? / CASH_! / CASH_!!
      - ? / ! / !! for bespoke deal/demand
    """
    st = FACTION_BAR_STYLE[faction]
    d = ImageDraw.Draw(canvas)
    d.rectangle((x0, y0, x1, y1), fill=st["bg"], outline=st["border"], width=3)

    n = len(tiers)
    cell_w = (x1 - x0) / n
    bar_h = y1 - y0
    pistol = load_icon("combat.png", int(bar_h * 0.46))
    computer = load_icon("laptop.png", int(bar_h * 0.40))
    cash = load_icon("cash.png", int(bar_h * 0.44))
    f_sym = ImageFont.truetype(F_SERIF_B, int(bar_h * 0.42))
    f_cond = ImageFont.truetype(F_BOLD, int(bar_h * 0.34))

    for i, (cond_str, spec) in enumerate(tiers):
        cx0 = int(x0 + i * cell_w)
        cx1 = int(x0 + (i + 1) * cell_w)
        if i > 0:
            d.line((cx0, y0 + 3, cx0, y1 - 3), fill=st["divider"], width=4)

        mid_x = (cx0 + cx1) // 2
        top_cy = y0 + int(bar_h * 0.31)
        bot_cy = y0 + int(bar_h * 0.75)

        if spec == "COMBAT":
            canvas.paste(pistol, (mid_x - pistol.size[0] // 2, top_cy - pistol.size[1] // 2), pistol)
        elif spec.startswith("IF_CARRYING:"):
            carry_txt = spec.split(":", 1)[1].strip()
            pistol_sm = load_icon("combat.png", int(bar_h * 0.38))
            max_lbl_w = max(60, int(cell_w) - pistol_sm.size[0] - 24)
            if " or " in carry_txt or " and " in carry_txt or len(carry_txt) > 9:
                f_carry = ImageFont.truetype(F_BOLD, int(bar_h * 0.20))
                c_lines = wrap_text_lines(d, carry_txt, f_carry, max_lbl_w)
            else:
                f_carry = ImageFont.truetype(F_BOLD, int(bar_h * 0.22))
                c_lines = [carry_txt]
            line_widths = []
            line_bboxes = []
            for cln in c_lines:
                bb_cl = d.textbbox((0, 0), cln, font=f_carry)
                line_widths.append(bb_cl[2] - bb_cl[0])
                line_bboxes.append(bb_cl)
            lbl_w = max(line_widths) if line_widths else 0
            total_w = lbl_w + 6 + pistol_sm.size[0]
            sx = mid_x - total_w // 2
            lh = int(f_carry.size * 1.12)
            tot_th = len(c_lines) * lh
            ty_start = top_cy - tot_th // 2
            for idx_cl, cln in enumerate(c_lines):
                bb_cl = line_bboxes[idx_cl]
                lw = bb_cl[2] - bb_cl[0]
                d.text(
                    (sx + (lbl_w - lw) // 2 - bb_cl[0], ty_start + idx_cl * lh - bb_cl[1]),
                    cln,
                    font=f_carry,
                    fill=st["text"],
                )
            canvas.paste(pistol_sm, (sx + lbl_w + 6, top_cy - pistol_sm.size[1] // 2), pistol_sm)
        elif spec.startswith("DECK_CASH_") or spec.startswith("CUBE_CHEST_"):
            punc = spec.split("_")[-1]
            bb_p = d.textbbox((0, 0), punc, font=f_sym)
            pw = bb_p[2] - bb_p[0]
            total_w = computer.size[0] + 4 + cash.size[0] + 4 + pw
            sx = mid_x - total_w // 2
            canvas.paste(computer, (sx, top_cy - computer.size[1] // 2), computer)
            canvas.paste(cash, (sx + computer.size[0] + 4, top_cy - cash.size[1] // 2), cash)
            d.text(
                (sx + computer.size[0] + 4 + cash.size[0] + 4, top_cy - (bb_p[3] - bb_p[1]) // 2 - bb_p[1]),
                punc,
                font=f_sym,
                fill=st["text"],
            )
        elif spec.startswith("CASH_") or spec.startswith("CHEST_"):
            punc = spec.split("_")[-1]
            bb_p = d.textbbox((0, 0), punc, font=f_sym)
            pw = bb_p[2] - bb_p[0]
            total_w = cash.size[0] + 6 + pw
            sx = mid_x - total_w // 2
            canvas.paste(cash, (sx, top_cy - cash.size[1] // 2), cash)
            d.text(
                (sx + cash.size[0] + 6, top_cy - (bb_p[3] - bb_p[1]) // 2 - bb_p[1]),
                punc,
                font=f_sym,
                fill=st["text"],
            )
        else:
            bb_p = d.textbbox((0, 0), spec, font=f_sym)
            pw, ph = bb_p[2] - bb_p[0], bb_p[3] - bb_p[1]
            d.text((mid_x - pw // 2 - bb_p[0], top_cy - ph // 2 - bb_p[1]), spec, font=f_sym, fill=st["text"])

        bb_c = d.textbbox((0, 0), cond_str, font=f_cond)
        cw, ch = bb_c[2] - bb_c[0], bb_c[3] - bb_c[1]
        d.text((mid_x - cw // 2 - bb_c[0], bot_cy - ch // 2 - bb_c[1]), cond_str, font=f_cond, fill=st["text"])


def draw_cp_line(canvas, x, y, formula_str, dark_text=True, icon_sz=62, font_sz=54):
    """Draw a LARGE Combat Formula line ([pistol] : Formula) with [R] enclosed in a square."""
    d = ImageDraw.Draw(canvas)
    if dark_text:
        pistol = load_icon("combat.png", icon_sz)
    else:
        pistol_base = load_icon("combat.png", icon_sz)
        pistol, _ = add_black_border_to_rgba(pistol_base, border_px=3, border_color=(255, 255, 255, 240))
    canvas.paste(pistol, (int(x), int(y - icon_sz // 2 + 2)), pistol)
    f_cp = ImageFont.truetype(F_BOLD, font_sz)
    col = (18, 18, 24) if dark_text else (255, 242, 75)
    die_bg = (238, 228, 206) if dark_text else (48, 44, 24)
    draw_formula_with_rome_die(d, int(x + icon_sz + 8), y, f": {formula_str}", f_cp, col, die_bg=die_bg)


def wrap_text_lines(d, text, font, max_w):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = f"{cur} {w}".strip()
        bb = d.textbbox((0, 0), test, font=font)
        if bb[2] - bb[0] <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_good_price_grid(canvas, d, x0, y0, x1, y1, good_spec, dark_mode=False):
    """Draw a Good's metadata line (Name (Category) + SUV squares + optional combat text)
    followed by its 5-column Scarcity price table:
      - 1 price row (+B) for Delivery Job cargo (fencedSell)
      - 2 price rows (+B Retail and -B Wholesale) for Bespoke Good Sale Deals
    """
    name_cat = f"{good_spec['name']} ({good_spec['category']})"
    blocks = int(good_spec.get("blocks", 1))
    combat_txt = good_spec.get("combatText") or good_spec.get("combat")

    fg = (242, 246, 250) if dark_mode else (20, 22, 26)
    f_meta = ImageFont.truetype(F_SYM, 28)
    try:
        f_meta.set_variation_by_name("Bold")
    except Exception:
        pass

    meta_cy = y0 + 20
    bb_m = d.textbbox((0, 0), name_cat, font=f_meta)
    mw, mh = bb_m[2] - bb_m[0], bb_m[3] - bb_m[1]
    d.text((x0 + 4, meta_cy - mh // 2 - bb_m[1]), name_cat, font=f_meta, fill=fg)

    # Draw SUV block squares
    sq_sz = 20
    sq_x = x0 + 4 + mw + 22
    for _ in range(blocks):
        d.rectangle((sq_x, meta_cy - sq_sz // 2, sq_x + sq_sz, meta_cy + sq_sz // 2), fill=fg)
        sq_x += sq_sz + 8

    if combat_txt:
        draw_formula_with_rome_die(d, sq_x + 12, meta_cy, combat_txt, f_meta, fg)

    # Draw Table below metadata line
    ty0 = y0 + 50
    sell_vals = good_spec.get("sell")
    buy_vals = good_spec.get("buy")
    rows = []
    if sell_vals:
        rows.append(("sell", sell_vals))
    if buy_vals:
        rows.append(("buy", buy_vals))

    # Keep 1-row fence table proportional in height (same row height as 2-row table)
    if len(rows) == 1:
        ty1 = min(y1, ty0 + 168)
    else:
        ty1 = y1

    tbl_bg = (248, 246, 240) if not dark_mode else (28, 34, 38)
    grid_col = (28, 118, 48) if not dark_mode else (68, 168, 88)
    num_col = (20, 22, 26) if not dark_mode else (244, 248, 252)

    d.rectangle((x0, ty0, x1, ty1), fill=tbl_bg, outline=grid_col, width=3)

    has_row_label = len(rows) >= 1
    label_w = int((x1 - x0) * 0.14) if has_row_label else 0
    col_w = (x1 - x0 - label_w) / 5.0

    hdr_h = int((ty1 - ty0) * (0.34 if len(rows) == 1 else 0.26))
    row_h = (ty1 - ty0 - hdr_h) / max(1, len(rows))

    f_hdr = ImageFont.truetype(F_BOLD, int(hdr_h * 0.62))
    for ci in range(5):
        cx0 = x0 + label_w + ci * col_w
        bb = d.textbbox((0, 0), SCARCITY[ci], font=f_hdr)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text(
            (cx0 + (col_w - tw) / 2 - bb[0], ty0 + (hdr_h - th) / 2 - bb[1]),
            SCARCITY[ci],
            font=f_hdr,
            fill=SCARCITY_COLORS[ci],
        )
    d.line((x0, ty0 + hdr_h, x1, ty0 + hdr_h), fill=grid_col, width=2)

    f_lbl = ImageFont.truetype(F_SYM, int(row_h * 0.56))
    try:
        f_lbl.set_variation_by_name("Bold")
    except Exception:
        pass
    f_val = ImageFont.truetype(F_NUM, int(row_h * 0.56))

    for ri, (kind, vals) in enumerate(rows):
        ry0 = ty0 + hdr_h + ri * row_h
        if ri > 0:
            d.line((x0, ry0, x1, ry0), fill=grid_col, width=2)
        if has_row_label:
            sym_txt = "+\u20bf" if kind == "sell" else "-\u20bf"
            sym_col = (22, 130, 48) if (kind == "sell" and not dark_mode) else ((72, 225, 108) if kind == "sell" else ((235, 68, 68) if dark_mode else (175, 28, 32)))
            bb_s = d.textbbox((0, 0), sym_txt, font=f_lbl)
            sw, sh = bb_s[2] - bb_s[0], bb_s[3] - bb_s[1]
            d.text((x0 + (label_w - sw) / 2 - bb[0], ry0 + (row_h - sh) / 2 - bb_s[1]), sym_txt, font=f_lbl, fill=sym_col)

        for ci in range(5):
            cx0 = x0 + label_w + ci * col_w
            v_str = str(vals[ci])
            bb_v = d.textbbox((0, 0), v_str, font=f_val)
            vw, vh = bb_v[2] - bb_v[0], bb_v[3] - bb_v[1]
            d.text((cx0 + (col_w - vw) / 2 - bb_v[0], ry0 + (row_h - vh) / 2 - bb_v[1]), v_str, font=f_val, fill=num_col)

    for ci in range(6):
        cx = int(x0 + label_w + ci * col_w)
        d.line((cx, ty0, cx, ty1), fill=grid_col, width=2)


def draw_lower_card_details(
    canvas,
    x0,
    y0,
    x1,
    y1,
    dark_mode=False,
    assignments=None,
    good_table=None,
):
    """Render ultra-concise Job ([cash]?/!/!!) and/or Deal/Demand (?/!/!!) assignments in a
    LARGE, bold font. Only draws a price table if `good_table` is supplied (Delivery Job cargo
    or Bespoke Good Sale Deal).
    """
    d = ImageDraw.Draw(canvas)
    fg = (242, 245, 250) if dark_mode else (18, 20, 24)
    badge_bg = (42, 48, 56) if dark_mode else (228, 224, 214)
    badge_border = (118, 128, 142) if dark_mode else (88, 82, 74)
    accent_red = (255, 102, 102) if dark_mode else (178, 26, 32)
    accent_gold = (255, 232, 75) if dark_mode else (142, 44, 18)

    assignments = assignments or []
    has_table = good_table is not None

    # Choose large font size based on whether a table shares the box or not
    text_font_sz = 33 if has_table else (40 if len(assignments) == 1 else 36)
    f_text = ImageFont.truetype(F_SYM, text_font_sz)
    try:
        f_text.set_variation_by_name("Bold")
    except Exception:
        pass
    f_punc = ImageFont.truetype(F_SERIF_B, 34 if has_table else 38)

    pad_x = 24
    max_text_w = (x1 - x0) - pad_x * 2 - 126

    # Pre-wrap each assignment so we can center them cleanly in the available vertical space
    rendered_items = []
    for kind, punc, text_str in assignments:
        lines = wrap_text_lines(d, text_str, f_text, max_text_w)
        item_h = max(62, len(lines) * int(text_font_sz * 1.24))
        rendered_items.append((kind, punc, lines, item_h))

    avail_text_y1 = (y0 + 148) if has_table else (y1 - 16)
    total_items_h = sum(it[3] for it in rendered_items) + max(0, len(rendered_items) - 1) * (24 if not has_table else 12)
    cur_y = y0 + max(18, ((avail_text_y1 - y0) - total_items_h) // 2)

    for idx, (kind, punc, lines, item_h) in enumerate(rendered_items):
        if idx > 0 and not has_table:
            div_y = cur_y - 12
            div_col = (68, 76, 86) if dark_mode else (196, 192, 182)
            d.line((x0 + pad_x, div_y, x1 - pad_x, div_y), fill=div_col, width=2)

        bx0, by0 = x0 + pad_x, cur_y
        bx1, by1 = bx0 + 108, by0 + 56
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=10, fill=badge_bg, outline=badge_border, width=2)

        if kind == "job":
            cash_sm = load_icon("cash.png", 40)
            bb_p = d.textbbox((0, 0), punc, font=f_punc)
            pw, ph = bb_p[2] - bb_p[0], bb_p[3] - bb_p[1]
            tot_w = 40 + 6 + pw
            sx = (bx0 + bx1 - tot_w) // 2
            canvas.paste(cash_sm, (sx, (by0 + by1 - 40) // 2), cash_sm)
            d.text((sx + 46, (by0 + by1 - ph) // 2 - bb_p[1]), punc, font=f_punc, fill=accent_gold)
        else:
            lbl = f"{punc}"
            bb_p = d.textbbox((0, 0), lbl, font=f_punc)
            pw, ph = bb_p[2] - bb_p[0], bb_p[3] - bb_p[1]
            d.text(((bx0 + bx1 - pw) // 2 - bb_p[0], (by0 + by1 - ph) // 2 - bb_p[1]), lbl, font=f_punc, fill=accent_red)

        tx = bx1 + 18
        line_h = int(text_font_sz * 1.22)
        ty = by0 + max(0, (56 - len(lines) * line_h) // 2)
        for ln in lines:
            d.text((tx, ty), ln, font=f_text, fill=fg)
            ty += line_h

        cur_y += item_h + (24 if not has_table else 12)

    if has_table:
        tbl_y0 = max(cur_y + 4, y0 + 142)
        tbl_y1 = y1 - 18
        draw_good_price_grid(canvas, d, x0 + pad_x, tbl_y0, x1 - pad_x, tbl_y1, good_table, dark_mode=dark_mode)


def prepare_full_bleed_phone_base():
    """Crop the smartphone in influence_instantgram.png so the phone fills 100% of 900x1400,
    and remove the top-right signal/Wi-Fi/battery icons so the bezel icons take their place.
    """
    raw_phone = Image.open(os.path.join(MOCKUP_DIR, "influence_instantgram.png")).convert("RGB")
    phone_full = raw_phone.crop((76, 27, 772, 1239)).resize((CARD_W, CARD_H), Image.LANCZOS)

    # Inpaint out the white signal/Wi-Fi/battery status icons in the top-right bezel (y=58..104, x=650..820)
    p_arr = np.array(phone_full)
    roi = p_arr[58:104, 650:820]
    gray = roi.mean(axis=2)
    inpaint_mask = ((gray > 75) * 255).astype(np.uint8)
    inpaint_mask = cv2.dilate(inpaint_mask, np.ones((5, 5), np.uint8), iterations=1)
    roi_clean = cv2.inpaint(roi, inpaint_mask, 5, cv2.INPAINT_TELEA)
    p_arr[58:104, 650:820] = roi_clean
    phone_full = Image.fromarray(p_arr)

    mask = Image.new("L", (CARD_W, CARD_H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((46, 36, 854, 1352), radius=64, fill=255)
    md.rounded_rectangle((385, 34, 565, 74), radius=16, fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))

    arr = np.array(raw_phone, dtype=np.float32)
    patch = arr[865:1145, 150:698, :]
    med = np.median(patch, axis=(0, 1))
    delta = patch - med
    delta_top = np.tile(delta, (3, 2, 1))[:660, :808, :]
    delta_bot = np.flipud(delta_top)[:656, :808, :]
    glass_delta = np.vstack([delta_top, delta_bot])  # (1316, 808, 3)

    return phone_full, mask, glass_delta


def save_phone_card(screen_canvas, phone_base, mask, glass_delta, filename, glass_strength=0.65):
    scr_arr = np.array(screen_canvas.convert("RGB"), dtype=np.float32)
    sub = scr_arr[36:1352, 46:854, :]
    sub = np.clip(sub + glass_delta * glass_strength, 0, 255)
    scr_arr[36:1352, 46:854, :] = sub
    comp = Image.fromarray(scr_arr.astype(np.uint8))
    final = Image.composite(comp, phone_base, mask)
    out_path = os.path.join(MOCKUP_DIR, filename)
    final.save(out_path, quality=95)
    v2_name = filename.replace(".png", "_v2.jpg")
    final.save(os.path.join(MOCKUP_DIR, v2_name), quality=95)
    final.save(os.path.join(PREV_ARTIFACT_DIR, v2_name), quality=95)
    final.save(os.path.join(CURR_ARTIFACT_DIR, v2_name), quality=95)
    print("Saved unified full-bleed phone card:", out_path)


def build_standalone_wanted_poster_card(mugshot):
    """Build Standalone Wanted Poster Card (encounter_criminals_wanted_final.jpg).
    - Gems are tight-cropped and rendered at 82px diameter (>= the Wanted poster's thumbs-up/down icons)
      with black borders and red diagonal slash on negative gems.
    - Combat Formula uses the square-enclosed Rome die icon [R].
    - Lower box showcases a Bespoke Good Sale Deal: [?] Buy Black Tar Heroin at -? with full 2-row
      +B Retail / -B Wholesale price table.
    """
    raw_w = Image.open(os.path.join(PREV_ARTIFACT_DIR, "enc_criminals_wanted_1794554990209.jpg")).convert("RGB")
    w_card = raw_w.resize((CARD_W, CARD_H), Image.LANCZOS).convert("RGBA")
    w_arr = np.array(w_card.convert("RGB"))

    # 1. Extract the Wanted Poster's own illustrated red thumb from bottom-left (x=34..132, y=1278..1386 in 900x1400)
    rt_crop = w_arr[1278:1386, 34:132].copy()
    r, g, b = rt_crop[:, :, 0].astype(np.int16), rt_crop[:, :, 1].astype(np.int16), rt_crop[:, :, 2].astype(np.int16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    is_red = (r - g > 42) & (r > 85)
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    near_red = cv2.dilate(is_red.astype(np.uint8), k5, iterations=1) > 0
    fg_mask = (is_red | ((lum < 95) & near_red)).astype(np.uint8) * 255
    fg_mask = cv2.GaussianBlur(fg_mask, (3, 3), 0.8)
    rt_rgba = np.dstack([rt_crop, fg_mask])
    rt_up = Image.fromarray(rt_rgba).rotate(180, resample=Image.BICUBIC).resize((80, 74), Image.LANCZOS)

    # 2. Inpaint out the old bottom-left red thumb (x=30..136, y=1274..1390)
    bot_roi = w_arr[1272:1392, 28:140]
    br, bg, bb_c = bot_roi[:, :, 0].astype(np.int16), bot_roi[:, :, 1].astype(np.int16), bot_roi[:, :, 2].astype(np.int16)
    blum = 0.299 * br + 0.587 * bg + 0.114 * bb_c
    b_mask = (((br - bg) > 32) | (blum < 95)).astype(np.uint8) * 255
    b_mask = cv2.dilate(b_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[1272:1392, 28:140] = cv2.inpaint(bot_roi, b_mask, 7, cv2.INPAINT_TELEA)

    # 3. Inpaint out the old small top-left gems (x=140..285, y=22..96) keeping a clean margin inside tl_roi
    tl_roi = w_arr[8:110, 128:300]
    tl_r, tl_g, tl_b = tl_roi[:, :, 0].astype(np.int16), tl_roi[:, :, 1].astype(np.int16), tl_roi[:, :, 2].astype(np.int16)
    tl_lum = 0.299 * tl_r + 0.587 * tl_g + 0.114 * tl_b
    tl_mask = ((tl_lum < 145) | (np.abs(tl_r - tl_g) > 30) | (np.abs(tl_b - tl_g) > 28)).astype(np.uint8) * 255
    tl_mask[:8, :] = 0
    tl_mask[-8:, :] = 0
    tl_mask[:, :8] = 0
    tl_mask[:, -8:] = 0
    tl_mask = cv2.dilate(tl_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[8:110, 128:300] = cv2.inpaint(tl_roi, tl_mask, 7, cv2.INPAINT_TELEA)

    # 4. Inpaint out the top-right cash icon at x=750..880, y=16..112
    tr_roi = w_arr[16:112, 750:880]
    tlum = tr_roi.mean(axis=2)
    t_mask = ((tlum < 120) | (tlum > 235)).astype(np.uint8) * 255
    t_mask = cv2.dilate(t_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[16:112, 750:880] = cv2.inpaint(tr_roi, t_mask, 7, cv2.INPAINT_TELEA)

    # 5. Inpaint out ONLY "Combat Formula" and "[swords] 2XR-1" (y=474..648, x=474..836)
    cf_roi = w_arr[474:648, 474:836]
    cflum = cf_roi.mean(axis=2)
    cf_mask = (cflum < 115).astype(np.uint8) * 255
    cf_mask = cv2.dilate(cf_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[474:648, 474:836] = cv2.inpaint(cf_roi, cf_mask, 7, cv2.INPAINT_TELEA)

    w_card = Image.fromarray(w_arr).convert("RGBA")
    d = ImageDraw.Draw(w_card)

    f_colon = ImageFont.truetype(F_BOLD, 44)
    f_rew = ImageFont.truetype(F_SYM, 44)
    try:
        f_rew.set_variation_by_name("Bold")
    except Exception:
        pass

    # --- TOP OUTCOME BAR (80px tight-cropped gems >= the green thumb icon!) ---
    top_cy = 58
    gem_wanted_sz = 80
    d.text((116, top_cy - 24), ":", font=f_colon, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))
    gx = 138
    gx = draw_gem_with_slash(w_card, gx, top_cy - gem_wanted_sz // 2, "Amethyst", is_negative=False, size=gem_wanted_sz, black_border=True, border_px=4)
    gx = draw_gem_with_slash(w_card, gx + 4, top_cy - gem_wanted_sz // 2, "Ruby", is_negative=True, size=gem_wanted_sz, black_border=True, border_px=4)

    # Top-Right Job Reward ([cash] : B0.5) with black border on light background
    rew_txt = ":\u20bf0.5"
    bb_r = d.textbbox((0, 0), rew_txt, font=f_rew)
    rw, rh = bb_r[2] - bb_r[0], bb_r[3] - bb_r[1]
    rx = 868 - rw
    cash_icon = load_icon("cash_white.png", 64)
    paste_with_optional_border(w_card, cash_icon, rx - 68, top_cy - 32, black_border=True, border_px=3)
    d.text((rx, top_cy - rh // 2 - bb_r[1]), rew_txt, font=f_rew, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))

    # --- BOTTOM OUTCOME BAR (y=1270..1390, center y=1330) ---
    bot_cy = 1330
    pistol_w = load_icon("pistol_white.png", 58)
    paste_with_optional_border(w_card, pistol_w, 42, bot_cy - 29, black_border=True, border_px=3)
    loot_txt = ":\u20bf0.6"
    bb_l = d.textbbox((0, 0), loot_txt, font=f_rew)
    lh = bb_l[3] - bb_l[1]
    d.text((108, bot_cy - lh // 2 - bb_l[1]), loot_txt, font=f_rew, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))

    # Bottom-Right: 80px Negated -Amethyst gem + `:` + Wanted Poster Red Thumb pointing UP!
    td_x = 866 - rt_up.size[0]
    w_card.paste(rt_up, (td_x, bot_cy - rt_up.size[1] // 2), rt_up)
    d.text((td_x - 22, bot_cy - 24), ":", font=f_colon, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))
    draw_gem_with_slash(w_card, td_x - 28 - gem_wanted_sz, bot_cy - gem_wanted_sz // 2, "Amethyst", is_negative=True, size=gem_wanted_sz, black_border=True, border_px=4)

    # --- LARGE COMBAT FORMULA with Rome Die [R] right below CLIQUE ENFORCER ---
    draw_cp_line(w_card, 480, 548, "2X(R) - 1", dark_text=True, icon_sz=68, font_sz=58)

    # --- TALL FACTION POSTURE BAR ---
    draw_tall_faction_interaction_bar(
        w_card,
        x0=55, y0=698, x1=845, y1=817,
        faction="MS13",
        tiers=[("\u2264 -1", "COMBAT"), ("= 0", "DECK_CASH_!!"), ("\u2265 1", "?")],
    )

    # --- LOWER DETAIL BOX (Bespoke Good Sale Deal: Black Tar Heroin + 2-row price table) ---
    draw_lower_card_details(
        w_card,
        x0=56, y0=856, x1=844, y1=1240,
        dark_mode=False,
        assignments=[
            ("deal", "?", "Buy Black Tar Heroin at -?"),
        ],
        good_table={
            "name": "Black Tar Heroin",
            "category": "Opiates",
            "blocks": 2,
            "sell": ["7", "5", "3.2", "2.4", "1.5"],
            "buy": ["5.5", "4.2", "2.6", "1.8", "1"],
        },
    )

    out_jpg_prev = os.path.join(PREV_ARTIFACT_DIR, "encounter_criminals_wanted_final.jpg")
    out_jpg_curr = os.path.join(CURR_ARTIFACT_DIR, "encounter_criminals_wanted_final.jpg")
    out_jpg_mock = os.path.join(MOCKUP_DIR, "encounter_criminals_wanted_final.jpg")
    out_png_mock = os.path.join(MOCKUP_DIR, "encounter_criminals_wanted.png")
    rgb_out = w_card.convert("RGB")
    rgb_out.save(out_jpg_prev, quality=95)
    rgb_out.save(out_jpg_curr, quality=95)
    rgb_out.save(out_jpg_mock, quality=95)
    rgb_out.save(out_png_mock, quality=95)
    print("Saved standalone Wanted Poster card:", out_jpg_curr)


def build_standalone_police_id_card():
    """Build Standalone Holographic Police ID Card (encounter_cops_police_id_final.jpg).
    - Top-Left & Bottom-Right Outcome Bars use 62px tight-cropped gems (>= the Police ID's thumb icons).
    - Combat Formula uses the square-enclosed Rome die icon [R].
    - Lower box showcases a concise Sell Job (no price table, large bold text):
      [cash]!! Sell Opiates at + in E1!!
    """
    raw_id = Image.open(os.path.join(PREV_ARTIFACT_DIR, "enc_cops_police_id_1794554967299.jpg")).convert("RGB")
    id_card = raw_id.resize((CARD_W, CARD_H), Image.LANCZOS).convert("RGBA")
    arr = np.array(id_card.convert("RGB"))

    # 1. Extract the Police ID's own red thumb from bottom-left (x=88..146, y=1268..1326 in 900x1400)
    rt_cop_crop = arr[1268:1326, 88:146].copy()
    cr, cg, cb = rt_cop_crop[:, :, 0].astype(np.int16), rt_cop_crop[:, :, 1].astype(np.int16), rt_cop_crop[:, :, 2].astype(np.int16)
    clum = 0.299 * cr + 0.587 * cg + 0.114 * cb
    is_thumb_red = (cr - cg) > 75
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    near_thumb_red = cv2.dilate(is_thumb_red.astype(np.uint8), k3, iterations=1) > 0
    cop_rt_mask = (is_thumb_red | ((clum < 55) & near_thumb_red)).astype(np.uint8) * 255
    cop_rt_rgba = np.dstack([rt_cop_crop, cop_rt_mask])
    rt_cop_up = Image.fromarray(cop_rt_rgba).rotate(180, resample=Image.BICUBIC).resize((56, 56), Image.LANCZOS)

    # 2. Erase old small top-left gems (x=152..300, y=71..138) & top-right gold shield badge (x=735..815, y=71..138)
    for x in range(152, 305):
        arr[71:138, x] = arr[71:138, 450]
    for x in range(735, 816):
        arr[71:138, x] = arr[71:138, 725]

    # 3. Erase the old red thumb on the Bottom-Left of the bottom maroon outcome bar (y=1263..1330, x=84..152)
    arr[1263:1330, 84:152] = arr[1263:1330, 170:238]

    # 4. Erase ONLY "Combat Formula / [swords] 2XR" (y=500..594, x=365..620)
    for x in range(365, 620):
        arr[500:594, x] = arr[500:594, 650]

    # 5. Cleanly fill the interior of the lower cream box (x=104..796, y=800..1228) so no faint background artifacts show
    cream_med = np.median(arr[815:860, 200:700], axis=(0, 1)).astype(np.uint8)
    arr[800:1228, 104:796] = cream_med

    id_card = Image.fromarray(arr).convert("RGBA")
    d = ImageDraw.Draw(id_card)

    f_colon = ImageFont.truetype(F_BOLD, 38)
    f_rew = ImageFont.truetype(F_SYM, 38)
    try:
        f_rew.set_variation_by_name("Bold")
    except Exception:
        pass

    # --- TOP OUTCOME BAR (y=71..138, center y=104, 60px tight-cropped gems >= thumb icon) ---
    top_cy = 104
    gem_cop_sz = 60
    d.text((156, top_cy - 22), ":", font=f_colon, fill=(255, 255, 255), stroke_width=3, stroke_fill=(12, 24, 18))
    gx = 176
    gx = draw_gem_with_slash(id_card, gx, top_cy - gem_cop_sz // 2, "Ruby", is_negative=False, size=gem_cop_sz, black_border=True, border_px=3)
    gx = draw_gem_with_slash(id_card, gx + 2, top_cy - gem_cop_sz // 2, "Sapphire", is_negative=True, size=gem_cop_sz, black_border=True, border_px=3)

    # Top-Right: White Cash Symbol (cash_white.png) + white text (:B0.6)
    rew_txt = ":\u20bf0.6"
    bb_r = d.textbbox((0, 0), rew_txt, font=f_rew)
    rw, rh = bb_r[2] - bb_r[0], bb_r[3] - bb_r[1]
    rx = 812 - rw
    cash_w = load_icon("cash_white.png", 54)
    paste_with_optional_border(id_card, cash_w, rx - 58, top_cy - 27, black_border=True, border_px=2)
    d.text((rx, top_cy - rh // 2 - bb_r[1]), rew_txt, font=f_rew, fill=(255, 255, 255), stroke_width=3, stroke_fill=(12, 24, 18))

    # --- BOTTOM OUTCOME BAR (y=1263..1330, center y=1296) ---
    bot_cy = 1296
    pistol_w = load_icon("pistol_white.png", 52)
    paste_with_optional_border(id_card, pistol_w, 84, bot_cy - 26, black_border=True, border_px=2)
    loot_txt = ":\u20bf0.8"
    bb_l = d.textbbox((0, 0), loot_txt, font=f_rew)
    lh = bb_l[3] - bb_l[1]
    d.text((142, bot_cy - lh // 2 - bb_l[1]), loot_txt, font=f_rew, fill=(255, 255, 255), stroke_width=3, stroke_fill=(28, 10, 14))

    # Bottom-Right: 60px Slashed -Ruby & -Diamond gems + `:` + Police ID Red Thumb pointing UP
    td_x = 814 - rt_cop_up.size[0]
    id_card.paste(rt_cop_up, (td_x, bot_cy - rt_cop_up.size[1] // 2), rt_cop_up)
    d.text((td_x - 18, bot_cy - 22), ":", font=f_colon, fill=(255, 255, 255), stroke_width=3, stroke_fill=(28, 10, 14))
    hx = td_x - 24
    for g_name in ["Diamond", "Ruby"]:
        hx -= (gem_cop_sz + 10)
        draw_gem_with_slash(id_card, hx, bot_cy - gem_cop_sz // 2, g_name, is_negative=True, size=gem_cop_sz, black_border=True, border_px=3)

    # --- LARGE COMBAT FORMULA with Rome Die [R] right below SFPD NARCOTICS UNIT ---
    draw_cp_line(id_card, 368, 548, "2X(R)", dark_text=True, icon_sz=64, font_sz=56)

    # --- TALL FACTION POSTURE BAR ---
    draw_tall_faction_interaction_bar(
        id_card,
        x0=96, y0=652, x1=804, y1=766,
        faction="MAGA",
        tiers=[("\u2264 -1", "COMBAT"), ("= 0", "DECK_CASH_!!"), ("\u2265 1", "CASH_!!")],
    )

    # --- LOWER DETAIL BOX (Sell Job: No price table, huge concise text!) ---
    draw_lower_card_details(
        id_card,
        x0=98, y0=792, x1=802, y1=1234,
        dark_mode=False,
        assignments=[
            ("job", "!!", "Sell Opiates at + in E1!!"),
        ],
        good_table=None,
    )

    out_jpg_prev = os.path.join(PREV_ARTIFACT_DIR, "encounter_cops_police_id_final.jpg")
    out_jpg_curr = os.path.join(CURR_ARTIFACT_DIR, "encounter_cops_police_id_final.jpg")
    out_jpg_mock = os.path.join(MOCKUP_DIR, "encounter_cops_police_id_final.jpg")
    rgb_out = id_card.convert("RGB")
    rgb_out.save(out_jpg_prev, quality=95)
    rgb_out.save(out_jpg_curr, quality=95)
    rgb_out.save(out_jpg_mock, quality=95)
    print("Saved standalone Police ID card:", out_jpg_curr)


def build_all_smartphone_encounter_cards():
    phone_base, mask, glass_delta = prepare_full_bleed_phone_base()

    # Load portraits/photos and also save cropped portraits/art for the webapp!
    portraits_dir = os.path.join(ROOT, "public/assets/fp/portraits")
    os.makedirs(portraits_dir, exist_ok=True)

    raw_id = Image.open(os.path.join(PREV_ARTIFACT_DIR, "enc_cops_police_id_1794554967299.jpg")).convert("RGB")
    id_cropped = raw_id.crop((58, 38, 790, 1226)).resize((CARD_W, CARD_H), Image.LANCZOS).convert("RGBA")
    cop_portrait = id_cropped.crop((102, 304, 346, 560)).resize((228, 268), Image.LANCZOS)
    cop_portrait.convert("RGB").save(os.path.join(portraits_dir, "portrait_cop.jpg"), quality=92)

    star_crop = raw_id.crop((120, 134, 288, 282)).resize((74, 68), Image.LANCZOS).convert("RGBA")
    s_arr = np.array(star_crop)
    r, g, b = s_arr[:, :, 0].astype(np.int16), s_arr[:, :, 1].astype(np.int16), s_arr[:, :, 2].astype(np.int16)
    s_arr[(r - b) < 22, 3] = 0
    star_clean = Image.fromarray(s_arr)
    id_guilloche = id_cropped.crop((0, 250, 28, 950)).transpose(Image.ROTATE_90).resize((776, 504), Image.BICUBIC)
    id_guilloche = Image.blend(id_guilloche.convert("RGB"), Image.new("RGB", (776, 504), (236, 241, 246)), 0.78)

    wiki_raw = Image.open(os.path.join(PREV_ARTIFACT_DIR, "encounter_wikipedia_profile_1794554567134.jpg")).rotate(-8.5, resample=Image.BICUBIC)
    wiki_portrait = wiki_raw.crop((235, 392, 405, 588)).resize((230, 275), Image.LANCZOS)
    wiki_portrait.convert("RGB").save(os.path.join(portraits_dir, "portrait_zuck.jpg"), quality=92)

    news_raw = Image.open(os.path.join(PREV_ARTIFACT_DIR, "encounter_news_article_1794554589583.jpg"))
    sfpd_photo = news_raw.crop((238, 526, 620, 760)).resize((260, 210), Image.LANCZOS)
    sfpd_photo.convert("RGB").save(os.path.join(portraits_dir, "portrait_dea.jpg"), quality=92)

    cash_raw = Image.open(os.path.join(PREV_ARTIFACT_DIR, "encounter_criminals_app_1794554615754.jpg"))
    hood_avatar = cash_raw.crop((260, 378, 358, 476)).resize((185, 185), Image.LANCZOS)
    hood_avatar.convert("RGB").save(os.path.join(portraits_dir, "portrait_scammer.jpg"), quality=92)
    mugshot = cash_raw.crop((282, 394, 338, 462)).resize((215, 250), Image.LANCZOS)
    mugshot.convert("RGB").save(os.path.join(portraits_dir, "portrait_enforcer.jpg"), quality=92)

    wanted_raw = Image.open(os.path.join(PREV_ARTIFACT_DIR, "enc_criminals_wanted_1794554990209.jpg")).convert("RGB")
    wanted_mug = wanted_raw.crop((102, 232, 456, 608)).resize((230, 260), Image.LANCZOS)
    wanted_mug.save(os.path.join(portraits_dir, "portrait_wanted.jpg"), quality=92)

    weed_raw = Image.open(os.path.join(MOCKUP_DIR, "weed_humboldt_indoor.png"))
    weed_photo = weed_raw.crop((140, 260, 880, 560)).resize((250, 200), Image.LANCZOS)
    weed_photo.convert("RGB").save(os.path.join(portraits_dir, "portrait_farmer.jpg"), quality=92)

    SX0, SX1 = 46, 854
    SY_TOP, SY_BOT = 104, 1278

    # =========================================================================
    # 1. POLICE ID INSIDE PHONE SCREEN (Cops — SFPD Narcotics Unit)
    # =========================================================================
    c_cop = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_cop)
    d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(218, 224, 232))

    c_cop.paste(id_guilloche, (SX0 + 16, 114))
    d.rounded_rectangle((SX0 + 16, 114, SX1 - 16, 618), radius=18, outline=(28, 42, 68), width=4)
    d.rounded_rectangle((SX0 + 19, 117, SX1 - 19, 212), radius=15, fill=(14, 32, 62))
    d.rectangle((SX0 + 19, 190, SX1 - 19, 212), fill=(14, 32, 62))
    d.line((SX0 + 19, 212, SX1 - 19, 212), fill=(214, 176, 56), width=4)
    c_cop.paste(star_clean, (SX0 + 36, 126), star_clean)
    d.text((SX0 + 124, 122), "SAN FRANCISCO POLICE DEPT.", font=ImageFont.truetype(F_COND, 46), fill=(255, 255, 255))
    d.text((SX0 + 124, 174), "OFFICIAL LAW ENFORCEMENT CREDENTIAL \u2022 CITY & COUNTY OF SF", font=ImageFont.truetype(F_BOLD, 16), fill=(230, 198, 96))

    d.text((SX0 + 36, 224), "SFPD Narcotics\nUnit", font=ImageFont.truetype(F_BOLD, 42), fill=(14, 20, 30))
    cop_bio = [
        "Tactical contraband sweep squad",
        "operating out of Mission & SoMa",
        "precincts. Confiscates street",
        "Opiates and Uppers. MAGA.",
    ]
    by = 330
    for ln in cop_bio:
        d.text((SX0 + 36, by), ln, font=ImageFont.truetype(F_REG, 21), fill=(32, 38, 48))
        by += 26
    draw_cp_line(c_cop, SX0 + 36, 552, "2X(R)", dark_text=True, icon_sz=62, font_sz=54)

    c_cop.paste(cop_portrait, (SX1 - 266, 232))
    d.rectangle((SX1 - 266, 232, SX1 - 38, 500), outline=(20, 30, 48), width=3)
    d.rounded_rectangle((SX1 - 266, 510, SX1 - 38, 544), radius=6, fill=(14, 32, 62))
    d.text((SX1 - 252, 519), "BADGE #4192 \u2022 NARCOTICS", font=ImageFont.truetype(F_MONO, 14), fill=(235, 205, 100))

    draw_tall_faction_interaction_bar(
        c_cop,
        x0=SX0 + 16, y0=630, x1=SX1 - 16, y1=796,
        faction="MAGA",
        tiers=[("\u2264 -1", "COMBAT"), ("= 0", "DECK_CASH_!!"), ("\u2265 1", "CASH_!!")],
    )

    d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=12, fill=(246, 245, 240), outline=(45, 52, 64), width=3)
    draw_lower_card_details(
        c_cop,
        x0=SX0 + 16, y0=808, x1=SX1 - 16, y1=1266,
        dark_mode=False,
        assignments=[
            ("job", "!!", "Sell Opiates at + in E1!!"),
        ],
        good_table=None,
    )

    draw_phone_bezel_outcomes(
        c_cop,
        friendly_gems=[("Ruby", "+"), ("Sapphire", "-")],
        friendly_reward="\u20bf0.6",
        combat_loot="\u20bf0.8",
        hostile_gems=[("Ruby", "-"), ("Diamond", "-")],
    )
    save_phone_card(c_cop, phone_base, mask, glass_delta, "encounter_cops_police_id.png", glass_strength=0.45)

    # =========================================================================
    # 2. SNATCHTAP PROFILE (Criminals — Clique Enforcer)
    # =========================================================================
    c_snap = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_snap)
    d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(18, 18, 22))

    hy0, hy1 = SY_TOP, SY_TOP + 72
    d.rectangle((SX0, hy0, SX1, hy1), fill=(255, 252, 0))
    d.line((SX0, hy1, SX1, hy1), fill=(28, 28, 32), width=3)
    d.rounded_rectangle((SX0 + 18, hy0 + 12, SX0 + 68, hy0 + 60), radius=12, fill=(18, 18, 22))
    d.ellipse((SX0 + 30, hy0 + 20, SX0 + 56, hy0 + 46), fill=(255, 255, 255))
    d.polygon([(SX0 + 26, hy0 + 36), (SX0 + 60, hy0 + 36), (SX0 + 62, hy0 + 52), (SX0 + 51, hy0 + 47), (SX0 + 43, hy0 + 53), (SX0 + 35, hy0 + 47), (SX0 + 24, hy0 + 52)], fill=(255, 255, 255))
    d.text((SX0 + 82, hy0 + 14), "SnatchTap", font=ImageFont.truetype(F_BOLD, 36), fill=(14, 14, 18))
    d.rounded_rectangle((SX1 - 265, hy0 + 16, SX1 - 18, hy0 + 56), radius=20, fill=(18, 18, 22))
    d.text((SX1 - 242, hy0 + 26), "* TAP SCORE 48.9K", font=ImageFont.truetype(F_BOLD, 18), fill=(255, 252, 0))

    d.rounded_rectangle((SX0 + 16, 190, SX1 - 16, 618), radius=16, fill=(28, 28, 34), outline=(255, 252, 0), width=3)
    d.text((SX0 + 36, 206), "Clique Enforcer", font=ImageFont.truetype(F_BOLD, 44), fill=(255, 255, 255))
    d.text((SX0 + 36, 260), "@el_sombra_24th \u2022 MS13 Clique", font=ImageFont.truetype(F_MONO, 19), fill=(255, 252, 0))
    snap_bio = [
        "Runs street protection & late-night",
        "Opiates drops around 24th St BART",
        "and Mission alleys. Disappearing",
        "burners only. Aligned with MS13.",
    ]
    by = 298
    for ln in snap_bio:
        d.text((SX0 + 36, by), ln, font=ImageFont.truetype(F_REG, 21), fill=(224, 226, 232))
        by += 26
    d.rounded_rectangle((SX0 + 36, 414, SX0 + 282, 452), radius=18, fill=(44, 44, 54), outline=(110, 110, 126), width=2)
    d.ellipse((SX0 + 50, 426, SX0 + 64, 440), fill=(255, 252, 0))
    d.text((SX0 + 72, 423), "TURF: Mission / 24th", font=ImageFont.truetype(F_BOLD, 17), fill=(255, 252, 0))
    d.rounded_rectangle((SX0 + 294, 414, SX0 + 510, 452), radius=18, fill=(44, 44, 54), outline=(110, 110, 126), width=2)
    d.ellipse((SX0 + 308, 426, SX0 + 322, 440), fill=(255, 88, 88))
    d.text((SX0 + 330, 423), "ARMED ENFORCER", font=ImageFont.truetype(F_BOLD, 17), fill=(255, 115, 115))

    draw_cp_line(c_snap, SX0 + 36, 536, "2X(R) - 1", dark_text=False, icon_sz=62, font_sz=54)

    sc_x0, sc_y0, sc_x1, sc_y1 = SX1 - 268, 210, SX1 - 34, 492
    d.rounded_rectangle((sc_x0, sc_y0, sc_x1, sc_y1), radius=32, fill=(255, 252, 0), outline=(14, 14, 18), width=3)
    for dx in range(sc_x0 + 18, sc_x1 - 12, 22):
        d.ellipse((dx, sc_y0 + 7, dx + 7, sc_y0 + 14), fill=(14, 14, 18))
        d.ellipse((dx, sc_y1 - 14, dx + 7, sc_y1 - 7), fill=(14, 14, 18))
    for dy in range(sc_y0 + 24, sc_y1 - 18, 22):
        d.ellipse((sc_x0 + 7, dy, sc_x0 + 14, dy + 7), fill=(14, 14, 18))
        d.ellipse((sc_x1 - 14, dy, sc_x1 - 7, dy + 7), fill=(14, 14, 18))
    c_snap.paste(mugshot, (sc_x0 + 10, sc_y0 + 16))
    d.rectangle((sc_x0 + 10, sc_y0 + 16, sc_x0 + 225, sc_y0 + 266), outline=(14, 14, 18), width=3)
    d.rounded_rectangle((sc_x0, 506, sc_x1, 548), radius=20, fill=(255, 252, 0))
    d.text((sc_x0 + 28, 517), "+ SEND TAP / DROP", font=ImageFont.truetype(F_BOLD, 18), fill=(14, 14, 18))

    draw_tall_faction_interaction_bar(
        c_snap,
        x0=SX0 + 16, y0=630, x1=SX1 - 16, y1=796,
        faction="MS13",
        tiers=[("\u2264 -1", "COMBAT"), ("= 0", "DECK_CASH_!!"), ("\u2265 1", "?")],
    )

    d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=14, fill=(28, 28, 34), outline=(255, 252, 0), width=2)
    draw_lower_card_details(
        c_snap,
        x0=SX0 + 16, y0=808, x1=SX1 - 16, y1=1266,
        dark_mode=True,
        assignments=[
            ("deal", "?", "Buy Black Tar Heroin at -?"),
        ],
        good_table={
            "name": "Black Tar Heroin",
            "category": "Opiates",
            "blocks": 2,
            "sell": ["7", "5", "3.2", "2.4", "1.5"],
            "buy": ["5.5", "4.2", "2.6", "1.8", "1"],
        },
    )

    draw_phone_bezel_outcomes(
        c_snap,
        friendly_gems=[("Amethyst", "+"), ("Ruby", "-")],
        friendly_reward="\u20bf0.5",
        combat_loot="\u20bf0.6",
        hostile_gems=[("Amethyst", "-")],
    )
    save_phone_card(c_snap, phone_base, mask, glass_delta, "encounter_criminals_snapchat.png", glass_strength=0.65)

    # =========================================================================
    # 3. WIKIBIO (Mark Zuckerberg — Celebrities)
    # =========================================================================
    c_wiki = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_wiki)
    d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(255, 255, 255))

    hy0, hy1 = SY_TOP, SY_TOP + 70
    d.rectangle((SX0, hy0, SX1, hy1), fill=(234, 236, 240))
    d.line((SX0, hy1, SX1, hy1), fill=(162, 169, 177), width=2)
    d.rounded_rectangle((SX0 + 18, hy0 + 11, SX0 + 68, hy0 + 59), radius=10, fill=(51, 102, 204))
    d.text((SX0 + 27, hy0 + 15), "WB", font=ImageFont.truetype(F_SERIF_B, 24), fill=(255, 255, 255))
    d.text((SX0 + 82, hy0 + 11), "WikiBio", font=ImageFont.truetype(F_SERIF_B, 30), fill=(32, 33, 34))
    d.text((SX0 + 82, hy0 + 43), "The Free Biographical Encyclopedia", font=ImageFont.truetype(F_SERIF_I, 16), fill=(84, 89, 93))
    d.rounded_rectangle((SX1 - 210, hy0 + 15, SX1 - 18, hy0 + 55), radius=6, fill=(255, 255, 255), outline=(162, 169, 177), width=2)
    d.text((SX1 - 196, hy0 + 25), "Search WikiBio...", font=ImageFont.truetype(F_REG, 17), fill=(114, 119, 125))

    d.rounded_rectangle((SX0 + 16, 188, SX1 - 16, 618), radius=6, fill=(248, 249, 250), outline=(162, 169, 177), width=2)
    d.rectangle((SX0 + 18, 190, SX1 - 18, 246), fill=(206, 223, 242))
    d.text((SX0 + 32, 200), "Mark Zuckerberg", font=ImageFont.truetype(F_SERIF_B, 36), fill=(32, 33, 34))
    d.text((SX1 - 245, 208), "[edit | cite source]", font=ImageFont.truetype(F_REG, 18), fill=(51, 102, 204))

    bio_rows = [
        ("Faction:", "TECH (Leader)", True),
        ("Role:", "FaceSpace CEO", False),
        ("Turf:", "SoMa / Embarcadero", True),
        ("Notes:", "“He’s actually quite", False),
        ("", "likeable.”", False),
    ]
    by = 262
    for lbl, val, is_link in bio_rows:
        if lbl:
            d.text((SX0 + 32, by), lbl, font=ImageFont.truetype(F_BOLD, 22), fill=(32, 33, 34))
        d.text((SX0 + 136, by), val, font=ImageFont.truetype(F_REG, 22), fill=(51, 102, 204) if is_link else (32, 33, 34))
        by += 35

    d.line((SX0 + 32, 456, SX0 + 510, 456), fill=(200, 204, 209), width=2)
    draw_cp_line(c_wiki, SX0 + 32, 536, "4(R) + 1", dark_text=True, icon_sz=62, font_sz=54)

    c_wiki.paste(wiki_portrait, (SX1 - 266, 264))
    d.rectangle((SX1 - 266, 264, SX1 - 36, 539), outline=(162, 169, 177), width=2)
    d.text((SX1 - 262, 548), "Sun Valley / SF Summit", font=ImageFont.truetype(F_REG, 16), fill=(84, 89, 93))

    draw_tall_faction_interaction_bar(
        c_wiki,
        x0=SX0 + 16, y0=630, x1=SX1 - 16, y1=796,
        faction="TECH",
        tiers=[("\u2264 -2", "COMBAT"), ("= -1", "DECK_CASH_!!"), ("\u2265 0", "CASH_!!")],
    )

    d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=6, fill=(248, 249, 250), outline=(162, 169, 177), width=2)
    draw_lower_card_details(
        c_wiki,
        x0=SX0 + 16, y0=808, x1=SX1 - 16, y1=1266,
        dark_mode=False,
        assignments=[
            ("job", "!!", "Pick up Nuke at F1 and deliver to C3!!"),
        ],
        good_table={
            "name": "Nuke",
            "category": "Weapon",
            "blocks": 4,
            "sell": ["7.5", "6", "5", "3.5", "3"],
        },
    )

    draw_phone_bezel_outcomes(
        c_wiki,
        friendly_gems=[("Ruby", "+"), ("Sapphire", "-")],
        friendly_reward="\u20bf1.5",
        combat_loot="\u20bf1.5",
        hostile_gems=[("Ruby", "-"), ("Diamond", "-")],
    )
    save_phone_card(c_wiki, phone_base, mask, glass_delta, "encounter_celebrities_wikipedia.png", glass_strength=0.45)

    # =========================================================================
    # 4. $CASHNET (Crypto Scammer — Criminals)
    # =========================================================================
    c_cash = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_cash)
    d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(14, 20, 18))

    hy0, hy1 = SY_TOP, SY_TOP + 70
    d.rectangle((SX0, hy0, SX1, hy1), fill=(0, 214, 79))
    d.text((SX0 + 22, hy0 + 13), "$CashNet", font=ImageFont.truetype(F_BOLD, 38), fill=(10, 18, 12))
    d.rounded_rectangle((SX1 - 235, hy0 + 15, SX1 - 20, hy0 + 55), radius=20, fill=(12, 24, 16))
    d.text((SX1 - 212, hy0 + 24), "P2P ESCROW", font=ImageFont.truetype(F_BOLD, 19), fill=(0, 235, 95))

    d.rounded_rectangle((SX0 + 16, 188, SX1 - 16, 618), radius=14, fill=(22, 32, 28), outline=(0, 195, 75), width=2)
    d.text((SX0 + 36, 206), "Crypto Scammer", font=ImageFont.truetype(F_BOLD, 44), fill=(248, 255, 250))
    d.text((SX0 + 36, 262), "$rugpull_sf \u2022 TECH Syndicate", font=ImageFont.truetype(F_MONO, 20), fill=(0, 230, 90))
    bio_c = [
        "Operates OTC stablecoin laundromat",
        "in SoMa & Nob Hill. Buys and sells",
        "Party and Uppers via P2P escrow",
        "drops. Aligned with TECH.",
    ]
    by = 308
    for ln in bio_c:
        d.text((SX0 + 36, by), ln, font=ImageFont.truetype(F_REG, 22), fill=(205, 220, 212))
        by += 30
    draw_cp_line(c_cash, SX0 + 36, 536, "X(R) + 1", dark_text=False, icon_sz=62, font_sz=54)

    av_mask = Image.new("L", (185, 185), 0)
    ImageDraw.Draw(av_mask).ellipse((0, 0, 184, 184), fill=255)
    c_cash.paste(hood_avatar, (SX1 - 236, 236), av_mask)
    d.ellipse((SX1 - 238, 234, SX1 - 49, 423), outline=(0, 230, 90), width=4)
    d.rounded_rectangle((SX1 - 232, 446, SX1 - 54, 488), radius=16, fill=(0, 185, 68))
    d.text((SX1 - 208, 457), "$ SEND / REQ", font=ImageFont.truetype(F_BOLD, 18), fill=(10, 18, 12))

    draw_tall_faction_interaction_bar(
        c_cash,
        x0=SX0 + 16, y0=630, x1=SX1 - 16, y1=796,
        faction="TECH",
        tiers=[("\u2264 -2", "COMBAT"), ("= -1", "!"), ("\u2265 0", "CASH_?")],
    )

    d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=14, fill=(24, 34, 30), outline=(0, 195, 75), width=2)
    draw_lower_card_details(
        c_cash,
        x0=SX0 + 16, y0=808, x1=SX1 - 16, y1=1266,
        dark_mode=True,
        assignments=[
            ("deal", "!", "Sell Upper at ++!"),
            ("job", "?", "Sell 3 Party at + in C4 in one transaction?"),
        ],
        good_table=None,
    )

    draw_phone_bezel_outcomes(
        c_cash,
        friendly_gems=[("Diamond", "+"), ("Sapphire", "-")],
        friendly_reward="\u20bf0.5",
        combat_loot="\u20bf0.6",
        hostile_gems=[("Diamond", "-"), ("Ruby", "-")],
    )
    save_phone_card(c_cash, phone_base, mask, glass_delta, "encounter_criminals_payment.png", glass_strength=0.65)

    # =========================================================================
    # 5. THE SF CHRONICLER NEWS ARTICLE (Cops — DEA Task Force)
    # =========================================================================
    c_news = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_news)
    d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(246, 242, 232))

    hy0, hy1 = SY_TOP, SY_TOP + 82
    d.rectangle((SX0, hy0, SX1, hy1), fill=(238, 232, 218))
    d.line((SX0, hy1 - 6, SX1, hy1 - 6), fill=(28, 26, 24), width=3)
    d.line((SX0, hy1, SX1, hy1), fill=(28, 26, 24), width=1)
    f_mast = ImageFont.truetype(F_SERIF_B, 42)
    mast = "The SF Chronicler"
    bb = d.textbbox((0, 0), mast, font=f_mast)
    d.text(((SX0 + SX1 - (bb[2] - bb[0])) // 2, hy0 + 8), mast, font=f_mast, fill=(20, 18, 16))
    sub_m = "SAN FRANCISCO BAY AREA METRO EDITION  \u2022  BREAKING CRIME DESK"
    f_subm = ImageFont.truetype(F_BOLD, 14)
    bb2 = d.textbbox((0, 0), sub_m, font=f_subm)
    d.text(((SX0 + SX1 - (bb2[2] - bb2[0])) // 2, hy0 + 58), sub_m, font=f_subm, fill=(85, 78, 70))

    d.rectangle((SX0 + 16, 198, SX1 - 16, 618), fill=(252, 249, 242), outline=(180, 172, 158), width=2)
    d.rectangle((SX0 + 32, 212, SX0 + 186, 238), fill=(175, 28, 32))
    d.text((SX0 + 42, 216), "FEDERAL SWEEP", font=ImageFont.truetype(F_BOLD, 16), fill=(255, 255, 255))
    d.text((SX0 + 32, 248), "DEA Task Force", font=ImageFont.truetype(F_SERIF_B, 42), fill=(18, 18, 18))
    d.text((SX0 + 32, 298), "By Metro Crime Desk \u2022 Civic Center & Tenderloin", font=ImageFont.truetype(F_SERIF_I, 18), fill=(95, 88, 80))

    news_body = [
        "Federal narcotics interdiction unit",
        "deployed across Tenderloin & SoMa",
        "corridors. Authorized to seize",
        "bulk Opiates & Uppers on sight.",
        "Backed by MAGA federal prosecutors.",
    ]
    by = 336
    for ln in news_body:
        d.text((SX0 + 32, by), ln, font=ImageFont.truetype(F_SERIF, 21), fill=(32, 30, 28))
        by += 27

    draw_cp_line(c_news, SX0 + 32, 542, "3X(R) + 2", dark_text=True, icon_sz=62, font_sz=54)

    c_news.paste(sfpd_photo, (SX1 - 292, 244))
    d.rectangle((SX1 - 292, 244, SX1 - 32, 454), outline=(40, 38, 34), width=2)
    d.text((SX1 - 290, 462), "DEA tactical units stage at", font=ImageFont.truetype(F_SERIF_I, 16), fill=(85, 80, 72))
    d.text((SX1 - 290, 482), "Civic Center Plaza. (Chronicle)", font=ImageFont.truetype(F_SERIF_I, 16), fill=(85, 80, 72))

    draw_tall_faction_interaction_bar(
        c_news,
        x0=SX0 + 16, y0=630, x1=SX1 - 16, y1=796,
        faction="MAGA",
        tiers=[("\u2264 -1", "COMBAT"), ("= 0", "!!"), ("\u2265 1", "CASH_!")],
    )

    d.rectangle((SX0 + 16, 808, SX1 - 16, 1266), fill=(252, 249, 242), outline=(180, 172, 158), width=2)
    draw_lower_card_details(
        c_news,
        x0=SX0 + 16, y0=808, x1=SX1 - 16, y1=1266,
        dark_mode=False,
        assignments=[
            ("deal", "!!", "Give me all of your Opiates!!"),
            ("job", "!", "Kill an ISIS!"),
        ],
        good_table=None,
    )

    draw_phone_bezel_outcomes(
        c_news,
        friendly_gems=[("Ruby", "+"), ("Sapphire", "-")],
        friendly_reward="\u20bf0.8",
        combat_loot="\u20bf1.0",
        hostile_gems=[("Ruby", "-"), ("Amethyst", "-")],
    )
    save_phone_card(c_news, phone_base, mask, glass_delta, "encounter_news_article.png", glass_strength=0.45)

    # =========================================================================
    # 6. GREG'S LIST AD (Criminals — Pot Farmers)
    # =========================================================================
    c_cl = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_cl)
    d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(255, 255, 255))

    hy0, hy1 = SY_TOP, SY_TOP + 68
    d.rectangle((SX0, hy0, SX1, hy1), fill=(238, 238, 246))
    d.line((SX0, hy1, SX1, hy1), fill=(180, 180, 204), width=2)
    d.text((SX0 + 20, hy0 + 14), "greg's list > sfbay > gigs > emerald triangle", font=ImageFont.truetype(F_SERIF, 24), fill=(85, 26, 139))
    d.rounded_rectangle((SX1 - 135, hy0 + 16, SX1 - 18, hy0 + 52), radius=6, fill=(255, 255, 255), outline=(160, 160, 185), width=2)
    d.text((SX1 - 118, hy0 + 24), "post / reply", font=ImageFont.truetype(F_REG, 17), fill=(85, 26, 139))

    d.rectangle((SX0 + 16, 184, SX1 - 16, 618), fill=(250, 250, 252), outline=(204, 204, 216), width=2)
    d.rounded_rectangle((SX0 + 32, 198, SX0 + 164, 234), radius=6, fill=(102, 51, 153))
    d.text((SX0 + 44, 206), "\u2709 reply now", font=ImageFont.truetype(F_BOLD, 17), fill=(255, 255, 255))
    d.text((SX0 + 180, 206), "posted 14 mins ago \u2022 haight / oakland", font=ImageFont.truetype(F_REG, 17), fill=(110, 114, 122))

    d.text((SX0 + 32, 246), "\u2606 Pot Farmers (Humboldt Direct)", font=ImageFont.truetype(F_SERIF_B, 33), fill=(0, 0, 238))
    cl_body = [
        "Emerald Triangle growers with surplus",
        "indoor flower & shrooms parked in",
        "Haight. Looking for SUV driver or",
        "immediate bulk Weed offload. DSA.",
    ]
    by = 304
    for ln in cl_body:
        d.text((SX0 + 32, by), ln, font=ImageFont.truetype(F_REG, 21), fill=(28, 28, 32))
        by += 28

    draw_cp_line(c_cl, SX0 + 32, 540, "2X(R)", dark_text=True, icon_sz=62, font_sz=54)

    c_cl.paste(weed_photo, (SX1 - 282, 300))
    d.rectangle((SX1 - 282, 300, SX1 - 32, 500), outline=(140, 140, 155), width=2)
    d.rounded_rectangle((SX1 - 282, 512, SX1 - 32, 550), radius=6, fill=(238, 238, 246), outline=(180, 180, 204), width=1)
    d.text((SX1 - 266, 521), "compensation: BTC / flower", font=ImageFont.truetype(F_REG, 17), fill=(50, 50, 64))

    draw_tall_faction_interaction_bar(
        c_cl,
        x0=SX0 + 16, y0=630, x1=SX1 - 16, y1=796,
        faction="DSA",
        tiers=[("\u2264 -1", "COMBAT"), ("= 0", "CASH_!"), ("\u2265 1", "?")],
    )

    d.rectangle((SX0 + 16, 808, SX1 - 16, 1266), fill=(250, 250, 252), outline=(204, 204, 216), width=2)
    draw_lower_card_details(
        c_cl,
        x0=SX0 + 16, y0=808, x1=SX1 - 16, y1=1266,
        dark_mode=False,
        assignments=[
            ("job", "!", "Sell Weed at -- in A5!"),
            ("deal", "?", "Buy Cheapest Mkt Weapon for \u20bf0.9?"),
        ],
        good_table=None,
    )

    draw_phone_bezel_outcomes(
        c_cl,
        friendly_gems=[("Sapphire", "+"), ("Ruby", "-")],
        friendly_reward="\u20bf0.4",
        combat_loot="\u20bf0.5",
        hostile_gems=[("Sapphire", "-")],
    )
    save_phone_card(c_cl, phone_base, mask, glass_delta, "encounter_criminals_craigslist.png", glass_strength=0.45)

    # Also build the two standalone physical cards (Wanted Poster & Police ID)!
    build_standalone_wanted_poster_card(mugshot)
    build_standalone_police_id_card()


if __name__ == "__main__":
    build_all_smartphone_encounter_cards()
