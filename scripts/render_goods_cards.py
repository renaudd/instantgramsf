"""Render InstantGram SF goods cards: card art + traits & price overlay.

The card art carries a light title banner at the top and a large blank light panel in the
lower half. This script finds both areas automatically, then draws on them:
  - the card name and category in the title banner (over any title baked into the art)
  - a combat-effect line (with [R] Rome die enclosed in a square), the SUV space symbols,
    and the price table in the blank panel

Usage:
  python3 scripts/render_goods_cards.py                       # render the six mock-ups
  python3 scripts/render_goods_cards.py <card_id> <art> <out> # render one card
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = "/System/Library/Fonts/Supplemental"
F_TITLE = os.path.join(FONTS, "DIN Condensed Bold.ttf")
F_BOLD = os.path.join(FONTS, "Arial Bold.ttf")
F_SERIF_B = os.path.join(FONTS, "Georgia Bold.ttf")
F_NUM = os.path.join(FONTS, "DIN Alternate Bold.ttf")

CATEGORY_LABEL = {
    "Grain": "WEED", "Weed": "WEED",
    "Marble": "PARTY", "Party": "PARTY",
    "Weapons": "WEAPONS", "Henchmen": "HENCHMEN", "Henchman": "HENCHMEN",
    "Meat Animals": "PILL UPPERS", "Pill Uppers": "PILL UPPERS",
    "Exotic Animals": "POWDER UPPERS", "Powder Uppers": "POWDER UPPERS",
    "Cheap Wine": "STREET OPIATES", "Street Opiates": "STREET OPIATES",
    "Fine Wine": "PHARMA OPIATES", "Pharma Opiates": "PHARMA OPIATES",
    "Uppers": "UPPERS", "Opiates": "OPIATES",
}
SCARCITY = ["<<", "<", "=", ">", ">>"]
SCARCITY_COLORS = [(31, 122, 31), (31, 160, 60), (190, 170, 20), (214, 90, 40), (150, 20, 40)]
INK = (24, 22, 20)
SELL_GREEN = (22, 110, 40)
BUY_RED = (150, 28, 28)
GRID = (60, 60, 60)
SCARCITY_LABEL = {"Grain": "WEED", "Weed": "WEED", "Marble": "PARTY", "Party": "PARTY"}


def btc(units):
    """Engine amounts are tenths of a Bitcoin (1 Denarius = 0.1 BTC)."""
    v = round(int(units)) / 10
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def load_cards():
    m = json.load(open(os.path.join(ROOT, "src/data/market_and_missions.json"), encoding="utf-8"))
    return {c["id"]: c for c in m["market"]}


def category_label(card):
    return CATEGORY_LABEL.get(card.get("subcategory"), CATEGORY_LABEL.get(card.get("track"), str(card.get("track", "")).upper()))


def light_rows(gray, y0, y1, x0, x1, thresh=205, frac=0.93):
    rows = []
    w = x1 - x0
    px = gray.load()
    for y in range(y0, y1):
        n = sum(1 for x in range(x0, x1, 2) if px[x, y] >= thresh)
        rows.append(n / (w / 2) >= frac)
    return rows


def longest_run(flags, offset):
    best, cur, start, bstart = 0, 0, 0, 0
    for i, f in enumerate(flags):
        if f:
            if cur == 0:
                start = i
            cur += 1
            if cur > best:
                best, bstart = cur, start
        else:
            cur = 0
    return offset + bstart, offset + bstart + best


def panel_x_bounds(gray, y, thresh=205):
    px = gray.load()
    w = gray.size[0]
    mid = w // 2
    left = mid
    while left > 0 and px[left, y] >= thresh:
        left -= 1
    right = mid
    while right < w - 1 and px[right, y] >= thresh:
        right += 1
    return left + 1, right - 1


def find_zones(img):
    gray = img.convert("L")
    W, H = gray.size
    ys = int(H * 0.40)
    py0, py1 = longest_run(light_rows(gray, ys, H, int(W * 0.25), int(W * 0.75)), ys)
    px0, px1 = panel_x_bounds(gray, (py0 + py1) // 2)
    if px1 < W * 0.85:
        px1 = W - px0
    px = gray.load()
    def edge_light(y):
        cols = list(range(int(W * 0.115), int(W * 0.135)))
        return sum(1 for x in cols if px[x, y] >= 140) / len(cols) >= 0.85
    ty0, ty1 = longest_run([edge_light(y) for y in range(0, int(H * 0.32))], 0)
    xm = int(W * 0.125)
    tx0 = xm
    while tx0 > 0 and px[tx0, (ty0 + ty1) // 2] >= 140:
        tx0 -= 1
    tx1 = int(W * 0.875)
    while tx1 < W - 1 and px[tx1, (ty0 + ty1) // 2] >= 190:
        tx1 += 1
    tx0, tx1 = tx0 + 1, tx1 - 1
    if tx1 < W * 0.85:
        tx1 = W - tx0
    return (tx0, ty0, tx1, ty1), (px0, py0, px1, py1)


def fit_font(path, text, max_w, start, min_size=10):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def center_text(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x0 + (x1 - x0 - tw) / 2 - bb[0], y0 + (y1 - y0 - th) / 2 - bb[1]), text, font=font, fill=fill)


def draw_title(img, d, zone, card):
    x0, y0, x1, y1 = zone
    fill = tuple(int(v) for v in ImageStat.Stat(img.crop((x0 + 4, y0 + 4, x0 + 24, y1 - 4))).median)
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), fill=fill)
    h = y1 - y0
    name = card["name"].upper()
    sub = (card.get("subtitle") or "").upper() or None
    title_font = fit_font(F_TITLE, name, (x1 - x0) * 0.9, int(h * 0.58))
    cat = category_label(card) + (f"  \u2022  {sub}" if sub else "")
    cat_font = fit_font(F_BOLD, cat, (x1 - x0) * 0.9, int(h * 0.17))
    center_text(d, (x0, y0 + h * 0.04, x1, y0 + h * 0.70), name, title_font, INK)
    center_text(d, (x0, y0 + h * 0.68, x1, y1 - h * 0.06), cat, cat_font, (176, 60, 20))


F_SYM = "/System/Library/Fonts/SFNS.ttf"  # has the Bitcoin glyph


def draw_symbols(d, x_left, cy, size, blocks, henchmen):
    """SUV space counters, anchored to the left edge of the traits line."""
    items = [("sq", INK)] * blocks + [("tri", (196, 150, 20))] * henchmen
    gap = size * 0.40
    x = x_left
    for kind, col in items:
        if kind == "sq":
            d.rectangle((x, cy - size / 2, x + size, cy + size / 2), fill=col)
        else:
            d.polygon([(x, cy + size / 2), (x + size / 2, cy - size / 2), (x + size, cy + size / 2)], fill=col, outline=INK)
        x += size + gap
    return x


def trait_text(card):
    """Only mechanically relevant text: CP formulas and special abilities (none = no combat effect)."""
    if card.get("track") == "Henchmen":
        return card.get("combatText")
    if card.get("combat") or card.get("rarityBonus"):
        return card.get("combatText")
    return None


def measure_trait_with_rome_die(d, text, font):
    parts = text.split("(R)")
    box_sz = int(font.size * 1.04)
    tot_w = 0
    for idx, p in enumerate(parts):
        if p:
            bb = d.textbbox((0, 0), p, font=font)
            tot_w += (bb[2] - bb[0])
        if idx < len(parts) - 1:
            tot_w += box_sz + 8
    return tot_w


def fit_trait_font(d, path, text, max_w, start, min_size=12):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if measure_trait_with_rome_die(d, text, f) <= max_w:
            return f
        size -= 1
    return ImageFont.truetype(path, min_size)


def draw_right_aligned_trait_with_rome_die(d, x_right, cy, text, font, fill):
    """Draw trait text right-aligned at x_right, replacing '(R)' with a square-enclosed 'R' Rome die icon."""
    parts = text.split("(R)")
    box_sz = int(font.size * 1.04)
    tot_w = measure_trait_with_rome_die(d, text, font)

    cur_x = int(x_right - tot_w)
    for idx, p in enumerate(parts):
        if p:
            bb = d.textbbox((0, 0), p, font=font)
            pw, ph = bb[2] - bb[0], bb[3] - bb[1]
            d.text((cur_x - bb[0], int(cy - ph / 2 - bb[1])), p, font=font, fill=fill)
            cur_x += pw
        if idx < len(parts) - 1:
            cur_x += 4
            bx0, by0 = cur_x, int(cy - box_sz // 2)
            bx1, by1 = cur_x + box_sz, by0 + box_sz
            d.rounded_rectangle((bx0, by0, bx1, by1), radius=max(4, box_sz // 7), fill=(238, 228, 206), outline=fill, width=max(2, box_sz // 11))
            f_r = ImageFont.truetype(F_SERIF_B, int(box_sz * 0.72))
            bb_r = d.textbbox((0, 0), "R", font=f_r)
            rw, rh = bb_r[2] - bb_r[0], bb_r[3] - bb_r[1]
            d.text((bx0 + (box_sz - rw) / 2 - bb_r[0], by0 + (box_sz - rh) / 2 - bb_r[1]), "R", font=f_r, fill=fill)
            cur_x += box_sz + 4


def price_label(img, box, kind):
    """Bold green +₿ (sell) or italic red -₿ (buy/hire), as in the online game."""
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0), int(y1 - y0)
    txt = "+\u20bf" if kind == "sell" else "-\u20bf"
    col = SELL_GREEN if kind == "sell" else BUY_RED
    layer = Image.new("RGBA", (w * 2, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    f = ImageFont.truetype(F_SYM, int(h * 0.62))
    try:
        f.set_variation_by_name("Bold" if kind == "sell" else "Semibold")
    except Exception:
        pass
    center_text(ld, (0, 0, w * 2, h), txt, f, col)
    if kind == "buy":
        layer = layer.transform(layer.size, Image.AFFINE, (1, 0.22, -h * 0.11, 0, 1, 0), resample=Image.BICUBIC)
    layer = layer.crop((w // 2, 0, w // 2 + w, h))
    img.paste(layer, (int(x0), int(y0)), layer)


def draw_panel(img, d, zone, card):
    x0, y0, x1, y1 = zone
    w, h = x1 - x0, y1 - y0
    pad = w * 0.05
    # Erase existing text in the blank panel first so re-renders are 100% clean
    panel_bg = tuple(int(v) for v in ImageStat.Stat(img.crop((x0 + 6, y0 + 6, x0 + 36, y0 + 36))).median)
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), fill=panel_bg)

    # Traits line: SUV space (left) + combat/abilities with [R] Rome die (right)
    line_h = h * 0.275
    cy = y0 + h * 0.012 + line_h / 2
    sym = line_h * 0.44
    x_after = draw_symbols(d, x0 + pad * 0.85, cy, sym, int(card.get("blocks") or 0), int(card.get("henchmen") or 0))
    tt = trait_text(card)
    if tt:
        avail = (x1 - pad * 0.65) - (x_after + pad * 0.30)
        max_single_sz = int(line_h * 0.88)
        f_single = fit_trait_font(d, F_BOLD, tt, avail, max_single_sz)
        # If a long compound trait (" - " or " & ") shrinks on 1 line, stack it on 2 lines to fill vertical whitespace
        split_sep = " - " if " - " in tt else (" & " if " & " in tt else None)
        if split_sep and f_single.size < int(line_h * 0.58):
            p1, p2 = tt.split(split_sep, 1)
            line1 = p1.strip()
            line2 = ("& " + p2.strip()) if split_sep == " & " else p2.strip()
            target_2l = int(line_h * 0.47)
            f1 = fit_trait_font(d, F_BOLD, line1, avail, target_2l)
            f2 = fit_trait_font(d, F_BOLD, line2, avail, target_2l)
            f_both = f1 if f1.size <= f2.size else f2
            cy1 = y0 + h * 0.012 + line_h * 0.26
            cy2 = y0 + h * 0.012 + line_h * 0.76
            draw_right_aligned_trait_with_rome_die(d, x1 - pad * 0.65, cy1, line1, f_both, INK)
            draw_right_aligned_trait_with_rome_die(d, x1 - pad * 0.65, cy2, line2, f_both, INK)
        else:
            draw_right_aligned_trait_with_rome_die(d, x1 - pad * 0.65, cy, tt, f_single, INK)

    # Price table
    tx0, tx1 = x0 + pad, x1 - pad
    ty0 = y0 + h * 0.012 + line_h + h * 0.014
    ty1 = y1 - h * 0.05
    sell, buy = card.get("sell"), card.get("buy")
    rows = ([("sell", sell)] if sell else []) + [("buy", buy)]
    hdr_ratio = 0.55
    unit = (ty1 - ty0) / (len(rows) + hdr_ratio)
    hdr_h = unit * hdr_ratio
    label_w = (tx1 - tx0) * 0.12
    col_w = (tx1 - tx0 - label_w) / 5
    d.rectangle((tx0, ty0, tx1, ty1), outline=SELL_GREEN, width=3)
    # header
    for ci in range(5):
        cx0 = tx0 + label_w + ci * col_w
        f = ImageFont.truetype(F_BOLD, int(hdr_h * 0.62))
        center_text(d, (cx0, ty0, cx0 + col_w, ty0 + hdr_h), SCARCITY[ci], f, SCARCITY_COLORS[ci])
    d.line((tx0, ty0 + hdr_h, tx1, ty0 + hdr_h), fill=SELL_GREEN, width=2)
    for ri, (kind, vals) in enumerate(rows):
        ry0 = ty0 + hdr_h + ri * unit
        if ri:
            d.line((tx0, ry0, tx1, ry0), fill=SELL_GREEN, width=2)
        price_label(img, (tx0, ry0, tx0 + label_w, ry0 + unit), kind)
        for ci in range(5):
            cx0 = tx0 + label_w + ci * col_w
            v = btc(vals[ci])
            bold = kind == "buy" and ci == 2
            f = fit_font(F_NUM, v, col_w * 0.86, int(unit * (0.62 if bold else 0.52)))
            center_text(d, (cx0, ry0, cx0 + col_w, ry0 + unit), v, f, INK)
    for ci in range(6):
        cx = tx0 + label_w + ci * col_w
        d.line((cx, ty0, cx, ty1), fill=SELL_GREEN, width=2)


_ZONE_CACHE = {}


def render(card, art, out, crop_art_out=None):
    img = Image.open(art).convert("RGB")
    if art not in _ZONE_CACHE:
        _ZONE_CACHE[art] = find_zones(img)
    title_zone, panel_zone = _ZONE_CACHE[art]
    if crop_art_out:
        tx0, ty0, tx1, ty1 = title_zone
        px0, py0, px1, py1 = panel_zone
        art_y0 = int(ty1 + (py0 - ty1) * 0.13)
        art_y1 = int(py0 - 6)
        art_crop = img.crop((px0, art_y0, px1, art_y1))
        art_crop.save(crop_art_out, quality=92)
    d = ImageDraw.Draw(img)
    draw_title(img, d, title_zone, card)
    draw_panel(img, d, panel_zone, card)
    if out.lower().endswith(".jpg") or out.lower().endswith(".jpeg"):
        img.save(out, quality=90)
    else:
        img.save(out)
    return title_zone, panel_zone


MOCKUPS = {
    "grn_?": ("OG Kush", "weed_humboldt_indoor.png", "art_weed.jpg"),
    "mrb_?": ("Champagne Molly", "party_pure_mdma_crystal.png", "art_party.jpg"),
    "ea_?": ("Peruvian Flake", "uppers_peruvian_flake.png", "art_uppers.jpg"),
    "cw_?": ("China White", "opiates_china_white.png", "art_opiates.jpg"),
    "wpn_?": ("Glawk 19", "weapons_glock_19.png", "art_weapons.jpg"),
    "grd_?": ("Big Mike", "henchmen_big_mike.png", "art_henchmen.jpg"),
}

TRACK_TO_TEMPLATE = {
    "Grain": "weed_humboldt_indoor.png",
    "Weed": "weed_humboldt_indoor.png",
    "Marble": "party_pure_mdma_crystal.png",
    "Party": "party_pure_mdma_crystal.png",
    "Animals": "uppers_peruvian_flake.png",
    "Meat Animals": "uppers_peruvian_flake.png",
    "Exotic Animals": "uppers_peruvian_flake.png",
    "Uppers": "uppers_peruvian_flake.png",
    "Wine": "opiates_china_white.png",
    "Cheap Wine": "opiates_china_white.png",
    "Fine Wine": "opiates_china_white.png",
    "Opiates": "opiates_china_white.png",
    "Weapons": "weapons_glock_19.png",
    "Weapon": "weapons_glock_19.png",
    "Henchmen": "henchmen_big_mike.png",
    "Henchman": "henchmen_big_mike.png",
}

if __name__ == "__main__":
    cards = load_cards()
    if len(sys.argv) == 4:
        print(render(cards[sys.argv[1]], sys.argv[2], sys.argv[3]))
        sys.exit()
    src = os.path.join(ROOT, "public/assets/fp/mockups")
    dst = os.path.join(src, "rendered")
    art_dst = os.path.join(ROOT, "public/assets/fp/goods_art")
    cards_dst = os.path.join(ROOT, "public/assets/fp/cards/goods")
    os.makedirs(dst, exist_ok=True)
    os.makedirs(art_dst, exist_ok=True)
    os.makedirs(cards_dst, exist_ok=True)
    by_name = {c["name"]: c for c in cards.values()}
    for _, (name, art, crop_name) in MOCKUPS.items():
        card = by_name[name]
        out = os.path.join(dst, art)
        crop_out = os.path.join(art_dst, crop_name)
        print(card["id"], name, render(card, os.path.join(src, art), out, crop_art_out=crop_out))

    # Render all 88 Market & Henchmen cards into public/assets/fp/cards/goods/<id>.jpg
    count = 0
    for cid, card in cards.items():
        trk = card.get("track") or card.get("subcategory") or card.get("category") or "Grain"
        tpl_name = TRACK_TO_TEMPLATE.get(trk, "weed_humboldt_indoor.png")
        out_path = os.path.join(cards_dst, f"{cid}.jpg")
        render(card, os.path.join(src, tpl_name), out_path)
        count += 1
    print(f"Rendered {count} market & henchmen cards into {cards_dst}")
